import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load .env for SMTP_PASSWORD (avoids typing in terminal)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

import json
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS
from graph.workflow import app

flask_app = Flask(__name__)
CORS(flask_app)

# Default email for dummy/send - to: recipient, from: sender
DEFAULT_TO_EMAIL = os.environ.get("DEFAULT_TO_EMAIL", "pcoswomenscare@gmail.com")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "salesflow.aiteam@gmail.com")

# Fallback when workflow/LLM fails - no external deps
def run_fallback_strategy(user_input):
    """Rule-based fallback: always returns valid output without LLM."""
    text = (user_input or "").lower()
    role = "Product Manager" if any(w in text for w in ["research", "researching", "ai", "solutions"]) else (
        "HR Manager" if any(w in text for w in ["hr", "recruit", "hiring", "talent"]) else "Operations Manager"
    )
    if not role or role == "Operations Manager":
        if any(w in text for w in ["healthcare", "health"]) or "ai" in text:
            role = "Product Manager"
    location = "London" if "london" in text else ("New York" if "new york" in text or "usa" in text else "")
    try:
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "mock_dataset.csv"))
        if location:
            filtered = df[df["location"].str.lower().str.contains(location.lower(), na=False)]
            df = filtered if not filtered.empty else df
        if role:
            role_filtered = df[df["role"].str.lower().str.contains(role.split()[0].lower(), na=False)]
            if not role_filtered.empty:
                df = role_filtered
        if df.empty:
            df = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "mock_dataset.csv"))
        # Prefer healthcare/AI industry for healthcare/tech queries
        if any(w in text for w in ["healthcare", "health", "ai", "research"]):
            industry_filtered = df[df["industry"].str.lower().str.contains("healthcare|ai|edtech", na=False, regex=True)]
            if not industry_filtered.empty:
                df = industry_filtered
        row = df.sort_values("engagement_score", ascending=False).iloc[0].to_dict()
        top_icp = {
            "name": row.get("name", ""),
            "company": row.get("company", ""),
            "email": row.get("email") or DEFAULT_TO_EMAIL,
            "engagement_score": float(row.get("engagement_score", 50)),
            "priority": "High" if float(row.get("engagement_score", 0)) >= 75 else "Medium",
            "match_score": 85,
        }
        engagement = top_icp["engagement_score"]
        channel = "Email" if engagement >= 50 else "LinkedIn"
        body = f"Dear {top_icp['name']},\n\nI hope this email finds you well. As the {row.get('role')} at {row.get('company')}, I understand the challenges of {row.get('pain_point_focus', 'operations')}. We help companies like yours streamline processes. Would a brief call next week make sense?\n\nBest regards,\nSalesFlow AI Team"
        return {
            "classification": {"role": role, "location": location or "Various", "urgency": "Medium", "user_intent": "Outreach", "business_behavior": ""},
            "icp_rankings": [top_icp],
            "selected_channel": channel,
            "channel_reasoning": f"Selected {channel} based on engagement score ({engagement}).",
            "generated_content": {"subject": f"Quick intro – {row.get('company')} growth opportunity", "body": body, "cta": "Schedule a call"}
        }
    except Exception as e:
        print("Fallback error:", e)
        return {
            "classification": {"role": role, "location": location or "Various", "urgency": "Medium", "user_intent": "", "business_behavior": ""},
            "icp_rankings": [{"name": "Prospect", "company": "Target Co", "email": DEFAULT_TO_EMAIL, "engagement_score": 70, "priority": "Medium", "match_score": 80}],
            "selected_channel": "Email",
            "channel_reasoning": "Default channel (fallback mode).",
            "generated_content": {"subject": "Outreach opportunity", "body": f"Hi,\n\nRe: {user_input}\n\nWould love to connect.\n\nBest,\nSalesFlow", "cta": "Reply"}
        }

def transform_workflow_result(raw_result):
    """
    Transform LangGraph workflow output to match frontend StrategyResult type.
    """
    try:
        # Extract and map classification to frontend format (camelCase + intent)
        raw_class = raw_result.get("classification", {})
        classification = {
            "role": raw_class.get("role", ""),
            "location": raw_class.get("location", ""),
            "urgency": raw_class.get("urgency", ""),
            "intent": raw_class.get("user_intent", raw_class.get("intent", "")),
            "businessBehavior": raw_class.get("business_behavior", raw_class.get("businessBehavior", "")),
        }
        
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
            obj = generated_content.get("objection_handling") or generated_content.get("objection_handler")
            if obj:
                key_points.append(obj)
            
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
    data = request.get_json() or {}
    user_input = (data.get("input") or "").strip()
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        raw_result = app.invoke({"user_input": user_input})
    except Exception as e:
        print(f"Workflow failed, using fallback: {e}")
        raw_result = run_fallback_strategy(user_input)

    try:
        transformed_result = transform_workflow_result(raw_result)
        # Auto-send email when channel is Email (helpful for presentation)
        exec_data = transformed_result.get("execution", {})
        if exec_data.get("type") == "Email" and exec_data.get("subject") and exec_data.get("body"):
            try:
                _auto_send_email(
                    to_addr=DEFAULT_TO_EMAIL,
                    subject=exec_data["subject"],
                    body=exec_data["body"],
                )
                transformed_result["emailAutoSent"] = True
            except Exception as e:
                print(f"Auto-send email (non-blocking): {e}")
        return jsonify(transformed_result), 200
    except Exception as e:
        print(f"Transform failed: {e}")
        raw_result = run_fallback_strategy(user_input)
        transformed_result = transform_workflow_result(raw_result)
        # Auto-send on fallback path too
        exec_data = transformed_result.get("execution", {})
        if exec_data.get("type") == "Email" and exec_data.get("subject") and exec_data.get("body"):
            try:
                _auto_send_email(DEFAULT_TO_EMAIL, exec_data["subject"], exec_data["body"])
                transformed_result["emailAutoSent"] = True
            except Exception:
                pass
        return jsonify(transformed_result), 200


# Email configuration (matches default send targets)
DUMMY_FROM_EMAIL = os.environ.get("DUMMY_FROM_EMAIL", DEFAULT_FROM_EMAIL)
DUMMY_TO_EMAIL = os.environ.get("DUMMY_TO_EMAIL", DEFAULT_TO_EMAIL)

# Gmail SMTP settings (use App Password, not regular password)
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "salesflow.aiteam@gmail.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "").strip()
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


def _auto_send_email(to_addr, subject, body):
    """Auto-send when channel is Email. Uses SMTP if configured, else dummy mode."""
    to_addr = (to_addr or DUMMY_TO_EMAIL).strip()
    subject = (subject or "").strip()
    body = (body or "").strip()
    if not subject or not body:
        return
    print("\n========== AUTO-SEND EMAIL (Channel=Email) ==========")
    print(f"To: {to_addr}")
    print(f"Subject: {subject}")
    print("====================================================\n")
    if ENABLE_REAL_EMAIL and SMTP_PASSWORD:
        try:
            send_email_via_smtp(to_addr, subject, body, DUMMY_FROM_EMAIL)
            print(f"[OK] Auto-sent to {to_addr}")
        except Exception as e:
            print(f"[WARN] Auto-send SMTP failed: {e}")
    else:
        print("[OK] Auto-send logged (dummy mode)")


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
    if SMTP_PASSWORD and ENABLE_REAL_EMAIL:
        print("[Email] REAL mode - will send to inbox (SMTP configured)")
    else:
        print("[Email] DUMMY mode - logs only. Add SMTP_PASSWORD to backend/.env to send real emails.")
    flask_app.run(debug=True, host="0.0.0.0", port=8000)
