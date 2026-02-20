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
from datetime import datetime
from graph.workflow import app
from agents.platform_agent import decide_channel_with_rules, get_channel_reasoning
from agents.content_agent import decide_tone, _build_email_prompt, _build_linkedin_prompt, _build_call_prompt, _fallback_content
from llm import call_llm
from utils import safe_json_parse

flask_app = Flask(__name__)
CORS(flask_app)

# Store campaign history in memory for this session
CAMPAIGNS = [
    {
        "created_at": "2026-02-19T10:00:00.000000",
        "status": "Sent",
        "classification": {"role": "HR Manager", "location": "London", "urgency": "High", "intent": "Hiring", "businessBehavior": "Professional"},
        "icp": {"name": "Sallee Kilbey", "company": "Vidoo", "email": "skilbey@vidoo.com", "engagementScore": 85, "priorityLevel": "High", "similarityConfidence": 98.5, "rank": 1},
        "channel": {"selected": "Email", "reasoning": "High engagement score and urgency signals."},
        "execution": {"type": "Email", "subject": "Talent acquisition strategy for Vidoo", "body": "Hi Sallee,\n\nI noticed Vidoo is expanding its EdTech presence in London. We have some interesting insights on talent retention for growing teams.\n\nBest,\nSalesFlow AI", "cta": "Schedule a call"}
    },
    {
        "created_at": "2026-02-19T11:00:00.000000",
        "status": "Sent",
        "classification": {"role": "CTO", "location": "Singapore", "urgency": "Medium", "intent": "Scaling", "businessBehavior": "Technical"},
        "icp": {"name": "Isidore Bardell", "company": "Jaxworks", "email": "ibardell@jaxworks.com", "engagementScore": 75, "priorityLevel": "High", "similarityConfidence": 85.0, "rank": 1},
        "channel": {"selected": "Call", "reasoning": "Technical profile, direct outreach preferred for high-value accounts."},
        "execution": {"type": "Call", "script": "Intro: Hello Isidore, I'm calling from SalesFlow AI. I saw your recent infrastructure updates at Jaxworks...\nValue: We help fintechs in Singapore scale their AI pipelines...", "keyPoints": ["AI scaling efficiency", "Regional compliance"]}
    }
]

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
            "channel_reasoning": channel_reasoning,
            "execution": execution
        }
    except Exception as e:
        print(f"Transform error: {e}")
        return raw_result

def process_single_icp(classification_transformed, icp_raw, rank, user_input):
    """
    Process a single ICP: decide channel, generate content, and execute.
    Returns a transformed StrategyResult.
    """
    try:
        # 1. Map classification to match agents' expected input (they expect snake_case mostly)
        classification = {
            "role": classification_transformed.get("role"),
            "location": classification_transformed.get("location"),
            "urgency": classification_transformed.get("urgency"),
            "business_behavior": classification_transformed.get("businessBehavior"),
            "intent": classification_transformed.get("intent"),
            "user_intent": classification_transformed.get("intent")
        }

        # 2. Decide channel - check if agent already recommended one, otherwise use rules
        selected_channel = icp_raw.get("recommended_channel")
        if not selected_channel:
            selected_channel = decide_channel_with_rules(classification, icp_raw)
            
        reasoning = icp_raw.get("channel_reasoning") or get_channel_reasoning(classification, icp_raw, selected_channel)

        # 3. Generate content
        tone = decide_tone(classification.get("urgency", "Medium"), icp_raw.get("priority", "Medium"))
        
        generated_content = {}
        try:
            if selected_channel == "Email":
                prompt = _build_email_prompt(classification, icp_raw, tone)
            elif selected_channel == "LinkedIn":
                prompt = _build_linkedin_prompt(classification, icp_raw, tone)
            else:
                prompt = _build_call_prompt(classification, icp_raw, tone)
            
            response = call_llm(prompt)
            generated_content = safe_json_parse(response) or _fallback_content(selected_channel, icp_raw, classification)
        except Exception:
            generated_content = _fallback_content(selected_channel, icp_raw, classification)

        # 4. Transform to frontend format with EXPLICIT channel override
        # We must package our decided channel into the "raw_result" structure 
        # so the transformer picks it up correctly
        synth_result = {
            "classification": classification,
            "icp": icp_raw,
            "selected_channel": selected_channel,  # <--- CRITICAL: Pass the decision
            "channel_reasoning": reasoning,        # <--- CRITICAL: Pass the reason
            "generated_content": generated_content
        }
        
        
        final_result = transform_workflow_result(synth_result)
        
        # 5. Auto-send email
        if selected_channel == "Email":
            try:
                execution = final_result.get("execution", {})
                # Force send to default email for testing/demo purposes
                recipient = DEFAULT_TO_EMAIL 
                # recipient = icp_raw.get("email") or DEFAULT_TO_EMAIL # <-- Old logic disabled for safety/testing
                
                if execution.get("body"):
                    _auto_send_email(recipient, execution["subject"], execution["body"])
                    final_result["emailAutoSent"] = True
            except Exception as e:
                print(f"Auto-send failed for {icp_raw.get('name')}: {e}")

        return final_result

    except Exception as e:
        print(f"Error processing ICP {icp_raw.get('name')}: {e}")
        return None

@flask_app.route("/run-strategy", methods=["POST"])
def run_strategy():
    """Accept user input from frontend and run the agent workflow"""
    data = request.get_json() or {}
    user_input = (data.get("input") or "").strip()
    campaign_mode = data.get("campaignMode", "single") 

    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        # 1. Run core workflow to get classification and ICP rankings
        raw_result = app.invoke({"user_input": user_input})
    except Exception as e:
        print(f"Workflow failed, using fallback: {e}")
        raw_result = run_fallback_strategy(user_input)

    try:
        # Extract classification (once for all ICPs)
        raw_class = raw_result.get("classification", {})
        classification_transformed = {
            "role": raw_class.get("role", ""),
            "location": raw_class.get("location", ""),
            "urgency": raw_class.get("urgency", "Medium"),
            "intent": raw_class.get("user_intent", raw_class.get("intent", "Outreach")),
            "businessBehavior": raw_class.get("business_behavior", raw_class.get("businessBehavior", "")),
        }

        icp_rankings = raw_result.get("icp_rankings", [])
        if not icp_rankings:
            return jsonify({"error": "No matching ICPs found"}), 404

        if campaign_mode == "multi":
            # Multi-ICP Mode: Top 5
            selected_icps = icp_rankings[:5]
            campaign_results = []
            success_count = 0
            failed_count = 0

            for i, icp_raw in enumerate(selected_icps):
                res = process_single_icp(classification_transformed, icp_raw, i + 1, user_input)
                if res:
                    res["created_at"] = datetime.now().isoformat()
                    campaign_results.append(res)
                    CAMPAIGNS.append(res)
                    success_count += 1
                else:
                    failed_count += 1
            
            return jsonify({
                "total_sent": len(campaign_results),
                "success_count": success_count,
                "failed_count": failed_count,
                "campaigns": campaign_results,
                # For frontend UI consistency during animation, we also return the first one as top-level result
                **campaign_results[0] 
            }), 200
        else:
            # Single Target Mode (Default)
            top_result = process_single_icp(classification_transformed, icp_rankings[0], 1, user_input)
            if not top_result:
                raise Exception("Failed to process top ICP")
                
            top_result["created_at"] = datetime.now().isoformat()
            CAMPAIGNS.append(top_result)
            return jsonify(top_result), 200

    except Exception as e:
        print(f"Process failed: {e}")
        # Final fallback - simple transformation of whatever we have
        transformed_result = transform_workflow_result(raw_result)
        transformed_result["created_at"] = datetime.now().isoformat()
        transformed_result["status"] = "Sent"
        CAMPAIGNS.append(transformed_result)
        return jsonify(transformed_result), 200


@flask_app.route("/campaigns", methods=["GET"])
def get_campaigns():
    """Return campaign history sorted by most recent (created_at descending)"""
    # Sort CAMPAIGNS by created_at in descending order
    sorted_campaigns = sorted(
        CAMPAIGNS, 
        key=lambda x: x.get("created_at", ""), 
        reverse=True
    )
    return jsonify(sorted_campaigns), 200


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
        # Force all emails to test address
        to_addr = DEFAULT_TO_EMAIL 
        # to_addr = data.get("to", "").strip() or DUMMY_TO_EMAIL

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
