import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS
from graph.workflow import app

flask_app = Flask(__name__)
CORS(flask_app)

def transform_workflow_result(raw_result):
    """
    Transform LangGraph workflow output to match frontend StrategyResult type.
    """
    try:
        # Extract classification (already in correct format)
        classification = raw_result.get("classification", {})
        
        # Transform ICP rankings to single top ICP object
        icp_rankings = raw_result.get("icp_rankings", [])
        icp = {}
        if icp_rankings:
            top_icp = icp_rankings[0]
            icp = {
                "name": top_icp.get("name", ""),
                "company": top_icp.get("company", ""),
                "email": top_icp.get("email", ""),
                "engagementScore": top_icp.get("engagement_score", 0),
                "priorityLevel": top_icp.get("priority", "Medium"),
                "similarityConfidence": top_icp.get("match_score", 0),
                "rank": 1,
            }
        
        # Transform channel decision
        selected_channel = raw_result.get("selected_channel", "Email")
        channel_reasoning = raw_result.get("channel_reasoning", "Recommended based on prospect engagement and urgency signals.")
        channel = {
            "selected": selected_channel,
            "reasoning": channel_reasoning
        }
        
        # Transform execution content based on channel
        generated_content = raw_result.get("generated_content", {})
        execution = {}
        
        if selected_channel == "Email" and generated_content:
            execution = {
                "type": "Email",
                "subject": generated_content.get("subject", "Outreach Opportunity"),
                "body": generated_content.get("body", ""),
                "cta": generated_content.get("cta", "Send Email")
            }
        elif selected_channel == "Call" and generated_content:
            # Format call content into a script
            script_parts = []
            if generated_content.get("opening_line"):
                script_parts.append(f"Opening: {generated_content.get('opening_line')}")
            if generated_content.get("rapport_building"):
                script_parts.append(f"\nRapport: {generated_content.get('rapport_building')}")
            if generated_content.get("problem_exploration"):
                script_parts.append(f"\nExplore: {generated_content.get('problem_exploration')}")
            if generated_content.get("value_pitch"):
                script_parts.append(f"\nPitch: {generated_content.get('value_pitch')}")
            if generated_content.get("closing_cta"):
                script_parts.append(f"\nClose: {generated_content.get('closing_cta')}")
            
            key_points = []
            if generated_content.get("objection_handling"):
                key_points.append(generated_content.get("objection_handling"))
            
            execution = {
                "type": "Call",
                "script": "\n".join(script_parts) if script_parts else "See key points for call strategy",
                "keyPoints": key_points
            }
        elif selected_channel == "LinkedIn" and generated_content:
            execution = {
                "type": "LinkedIn",
                "connectionMessage": generated_content.get("connectionMessage", ""),
                "followUpMessage": generated_content.get("followUpMessage", "")
            }
        else:
            # Default execution
            execution = {
                "type": selected_channel,
                "script": json.dumps(generated_content) if generated_content else ""
            }
        
        return {
            "classification": classification,
            "icp": icp,
            "channel": channel,
            "execution": execution
        }
    except Exception as e:
        print(f"Transform error: {e}")
        return raw_result

@flask_app.route("/run-strategy", methods=["POST"])
def run_strategy():
    """Accept user input from frontend and run the agent workflow"""
    try:
        data = request.get_json()
        user_input = data.get("input", "").strip()
        
        if not user_input:
            return jsonify({"error": "No input provided"}), 400
        
        # Run the workflow with user input
        raw_result = app.invoke({
            "user_input": user_input
        })
        
        # Transform to frontend format
        transformed_result = transform_workflow_result(raw_result)
        
        return jsonify(transformed_result), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


# Email configuration
DUMMY_FROM_EMAIL = os.environ.get("DUMMY_FROM_EMAIL", "salesflow.aiteam@gmail.com")
DUMMY_TO_EMAIL = os.environ.get("DUMMY_TO_EMAIL", "pcoswomenscare@gmail.com")

# Gmail SMTP settings (use App Password, not regular password)
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "salesflow.aiteam@gmail.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")  # Set via environment variable or .env file
ENABLE_REAL_EMAIL = os.environ.get("ENABLE_REAL_EMAIL", "true").lower() == "true"


def send_email_via_smtp(to_addr, subject, body, from_addr=None):
    """
    Send email via Gmail SMTP.
    Requires SMTP_PASSWORD environment variable set (Gmail App Password).
    """
    if not SMTP_PASSWORD:
        raise ValueError("SMTP_PASSWORD not configured. Set it as environment variable.")
    
    from_addr = from_addr or DUMMY_FROM_EMAIL
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject
    
    # Add body
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Enable encryption
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(from_addr, to_addr, text)
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        raise


@flask_app.route("/send-email", methods=["POST"])
def send_email():
    """
    Email sending endpoint.
    If ENABLE_REAL_EMAIL=true and SMTP_PASSWORD is set, sends real email via SMTP.
    Otherwise, logs the email (dummy mode).
    """
    try:
        data = request.get_json() or {}
        to_addr = data.get("to", "").strip() or DUMMY_TO_EMAIL
        subject = data.get("subject", "").strip()
        body = data.get("body", "").strip()

        if not subject or not body:
            return jsonify({"error": "Missing 'subject' or 'body'"}), 400

        print("\n========== EMAIL SENDING ==========")
        print(f"From: {DUMMY_FROM_EMAIL}")
        print(f"To: {to_addr}")
        print(f"Subject: {subject}")
        print("Body:")
        print(body[:200] + "..." if len(body) > 200 else body)
        print("=====================================\n")

        # Try to send real email if enabled
        if ENABLE_REAL_EMAIL and SMTP_PASSWORD:
            try:
                send_email_via_smtp(to_addr, subject, body, DUMMY_FROM_EMAIL)
                print(f"✅ Real email sent successfully to {to_addr}")
                return jsonify({
                    "success": True,
                    "message": f"Email sent successfully to {to_addr}",
                }), 200
            except Exception as smtp_error:
                print(f"⚠️ SMTP failed: {smtp_error}")
                print("📝 Falling back to dummy mode (email logged only)")
                # Fall through to dummy mode
        
        # Dummy mode (log only)
        print(f"📝 Email logged (dummy mode) - To: {to_addr}")
        return jsonify({
            "success": True,
            "message": "Email logged (dummy mode). Set SMTP_PASSWORD to send real emails.",
        }), 200

    except Exception as e:
        print(f"Send email error: {e}")
        return jsonify({"error": str(e)}), 500

@flask_app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0", port=8000)
