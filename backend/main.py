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
CAMPAIGNS = []

# Store full ICP rankings from all runs (for Leads Page)
ALL_ICP_LEADS = []

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
    
    # Smarter Classification for Fallback
    if any(w in text for w in ["immediately", "urgent", "asap", "immediate", "right now"]):
        urgency = "Immediate"
    elif any(w in text for w in ["high", "priority", "soon"]):
        urgency = "High"
    else:
        urgency = "Medium"
    
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

        # Sort and pick top lead
        df["engagement_score"] = pd.to_numeric(df["engagement_score"], errors="coerce").fillna(50)
        row = df.sort_values("engagement_score", ascending=False).iloc[0].to_dict()
        
        top_icp = {
            "name": row.get("name", "Target Executive"),
            "company": row.get("company", "Target Co"),
            "email": row.get("email") or DEFAULT_TO_EMAIL,
            "role": row.get("role", role),
            "industry": row.get("industry", "Technology"),
            "location": row.get("location", location or "Global"),
            "engagement_score": float(row.get("engagement_score", 70)),
            "priority": "High" if urgency == "High" or float(row.get("engagement_score", 0)) >= 75 else "Medium",
            "match_score": 90,
            "run_at": datetime.now().isoformat()
        }

        # Select channel based on urgency
        channel = "Call" if urgency == "Immediate" else ("Email" if top_icp["engagement_score"] >= 50 else "LinkedIn")
        
        # Populate ALL_ICP_LEADS so Leads Page works
        ALL_ICP_LEADS.append(top_icp)

        body = f"Hi {top_icp['name']},\n\nRe: {user_input}\n\nI noticed {top_icp['company']} is scaling. Would love to chat about solutions."
        return {
            "classification": {"role": role, "location": location or "Global", "urgency": urgency, "user_intent": "Strategic Outreach", "business_behavior": "Scaling"},
            "icp": top_icp,
            "icp_rankings": [top_icp],
            "selected_channel": channel,
            "channel_reasoning": f"Fallback mode: {channel} selected based on urgency and engagement score.",
            "generated_content": {"subject": f"Strategic Outreach: {role} opportunity", "body": body, "cta": "Reply"}
        }

    except Exception as e:
        print("Fallback error:", e)
        fallback_lead = {
            "name": "Target Executive", 
            "company": "Target Co", 
            "email": DEFAULT_TO_EMAIL, 
            "role": role,
            "industry": "Technology",
            "location": "Global",
            "engagement_score": 75, 
            "priority": "High", 
            "match_score": 85, 
            "run_at": datetime.now().isoformat()
        }
        ALL_ICP_LEADS.append(fallback_lead)
        return {
            "classification": {"role": role, "location": "Global", "urgency": "High", "user_intent": "Strategic Outreach", "business_behavior": "Scaling"},
            "icp": fallback_lead,
            "icp_rankings": [fallback_lead],
            "selected_channel": "Call",
            "channel_reasoning": "Fallback mode: High priority detected based on business signals.",
            "generated_content": {"subject": f"Strategic Outreach: {role} opportunity", "body": f"Hi,\n\nRe: {user_input}\n\nI noticed your work as {role}. Would love to connect.", "cta": "Reply"}
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

        # 2. Decide channel
        selected_channel = decide_channel_with_rules(classification, icp_raw)
        reasoning = get_channel_reasoning(classification, icp_raw, selected_channel)

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

        # 4. Transform to frontend format
        icp_transformed = {
            "name": icp_raw.get("name", ""),
            "company": icp_raw.get("company", ""),
            "email": icp_raw.get("email", ""),
            "engagementScore": icp_raw.get("engagement_score", 0),
            "priorityLevel": icp_raw.get("priority", "Medium"),
            "similarityConfidence": icp_raw.get("match_score", 0),
            "rank": rank,
        }

        execution = {}
        if selected_channel == "Email":
            execution = {
                "type": "Email",
                "subject": generated_content.get("subject", "Outreach"),
                "body": generated_content.get("body", ""),
                "cta": generated_content.get("cta", "Send Email")
            }
        elif selected_channel == "Call":
            script_parts = []
            for key in ["opening_line", "rapport_building", "problem_exploration", "value_pitch", "closing_cta"]:
                if generated_content.get(key):
                    script_parts.append(f"{key.replace('_', ' ').capitalize()}: {generated_content[key]}")
            
            execution = {
                "type": "Call",
                "script": "\n\n".join(script_parts) or "Call script generated.",
                "keyPoints": [generated_content.get("objection_handling", "Listen to prospect needs.")]
            }
        else: # LinkedIn
            execution = {
                "type": "LinkedIn",
                "connectionMessage": generated_content.get("connectionMessage", ""),
                "followUpMessage": generated_content.get("followUpMessage", "")
            }

        result = {
            "classification": classification_transformed,
            "icp": icp_transformed,
            "channel": {"selected": selected_channel, "reasoning": reasoning},
            "execution": execution,
            "status": "Sent"
        }

        # 5. Auto-send email
        if selected_channel == "Email" and execution.get("body"):
            try:
                recipient = icp_transformed.get("email") or DEFAULT_TO_EMAIL
                _auto_send_email(recipient, execution["subject"], execution["body"])
                result["emailAutoSent"] = True
            except Exception as e:
                print(f"Auto-send failed for {icp_transformed['name']}: {e}")

        return result
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

            # Accumulate ALL icp_rankings for Leads Page
            for icp_raw in icp_rankings:
                icp_raw["classification"] = classification_transformed
                icp_raw["run_at"] = datetime.now().isoformat()
                ALL_ICP_LEADS.append(icp_raw)
            
            # Include original icp_rankings and top-level selected channel/execution
            top = campaign_results[0] if campaign_results else {}
            response_payload = {
                "total_sent": len(campaign_results),
                "success_count": success_count,
                "failed_count": failed_count,
                "campaigns": campaign_results,
                # Provide the original icp_rankings (raw) for analytics aggregation
                "icp_rankings": selected_icps,
                # For frontend UI consistency during animation, also expose the first campaign at top-level
                **(top or {})
            }

            # Also expose the selected channel and execution at top-level if present
            if top.get("channel"):
                response_payload["selected_channel"] = top["channel"].get("selected")
                response_payload["channel_reasoning"] = top["channel"].get("reasoning")
            if top.get("execution"):
                response_payload["execution"] = top["execution"]

            return jsonify(response_payload), 200
        else:
            # Single Target Mode (Default)
            top_result = process_single_icp(classification_transformed, icp_rankings[0], 1, user_input)
            if not top_result:
                raise Exception("Failed to process top ICP")

            top_result["created_at"] = datetime.now().isoformat()
            CAMPAIGNS.append(top_result)

            # Accumulate ALL icp_rankings for Leads Page
            for icp_raw in icp_rankings:
                icp_raw["classification"] = classification_transformed
                icp_raw["run_at"] = datetime.now().isoformat()
                ALL_ICP_LEADS.append(icp_raw)

            # Also provide the full icp_rankings and top-level selected channel/execution
            payload = dict(top_result)
            payload["icp_rankings"] = icp_rankings
            payload["selected_channel"] = top_result.get("channel", {}).get("selected")
            payload["channel_reasoning"] = top_result.get("channel", {}).get("reasoning")
            payload["execution"] = top_result.get("execution")
            return jsonify(payload), 200

    except Exception as e:
        print(f"Process failed: {e}")
        # Final fallback - simple transformation of whatever we have
        transformed_result = run_fallback_strategy(user_input)
        transformed_result["created_at"] = datetime.now().isoformat()
        transformed_result["status"] = "Success"
        CAMPAIGNS.append(transformed_result)
        return jsonify(transformed_result), 200


@flask_app.route("/campaigns", methods=["GET"])
def get_campaigns():
    """Return campaign history sorted by most recent (created_at descending)"""
    sorted_campaigns = sorted(
        CAMPAIGNS,
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )
    return jsonify(sorted_campaigns), 200


@flask_app.route("/leads", methods=["GET"])
def get_leads():
    """
    Return ICP leads matched by the agent pipeline against the user's prompt.

    Data source: ALL_ICP_LEADS — populated exclusively by /run-strategy runs.
    Each entry was scored by the ICP Intelligence Agent (A2) against the
    user's specific target description.

    If no strategy has been run yet, returns has_runs=False so the frontend
    can show the correct prompt instead of an empty table.
    """
    try:
        if not ALL_ICP_LEADS:
            print("[Leads] No strategy runs yet — ALL_ICP_LEADS is empty")
            return jsonify({
                "has_runs": False,
                "total_qualified": 0,
                "leads": []
            }), 200

        # Deduplicate by email, keep highest match_score entry per person
        seen_emails = {}
        for lead in ALL_ICP_LEADS:
            email = lead.get("email", "")
            if not email:
                continue
            existing = seen_emails.get(email)
            if not existing or lead.get("match_score", 0) > existing.get("match_score", 0):
                seen_emails[email] = lead

        # Build response list
        PRIORITY_ORDER = {"High": 3, "Medium": 2, "Low": 1}
        leads = []
        for lead in seen_emails.values():
            eng = float(lead.get("engagement_score", 0))
            priority = lead.get("priority", "Low")
            icp_match = lead.get("classification", {}).get("icp_match", False)
            leads.append({
                "name":             lead.get("name", ""),
                "company":          lead.get("company", ""),
                "email":            lead.get("email", ""),
                "role":             lead.get("role", ""),
                "industry":         lead.get("industry", ""),
                "location":         lead.get("location", ""),
                "engagement_score": eng,
                "priority":         priority,
                "icp_match":        bool(icp_match),
                "match_score":      float(lead.get("match_score", 0)),
                "pain_point":       lead.get("pain_point_focus", ""),
                "tier":             "High" if eng >= 70 else "Medium",
                "run_at":           lead.get("run_at", ""),
            })

        # Sort: Priority (High first) then match_score then engagement_score desc
        leads.sort(
            key=lambda x: (
                PRIORITY_ORDER.get(x["priority"], 0),
                x["match_score"],
                x["engagement_score"]
            ),
            reverse=True
        )

        print(f"\n[Leads] Strategy runs (raw entries) : {len(ALL_ICP_LEADS)}")
        print(f"[Leads] Unique matched leads returned: {len(leads)}")
        if leads:
            print(f"[Leads] Top lead: {leads[0]['name']} | match={leads[0]['match_score']} | priority={leads[0]['priority']}")
        print()

        return jsonify({
            "has_runs": True,
            "total_qualified": len(leads),
            "leads": leads
        }), 200

    except Exception as e:
        print(f"[Leads] Error: {e}")
        return jsonify({"error": str(e), "has_runs": False, "leads": [], "total_qualified": 0}), 500


# Email configuration (matches default send targets)
DUMMY_FROM_EMAIL = os.environ.get("DUMMY_FROM_EMAIL", DEFAULT_FROM_EMAIL)
DUMMY_TO_EMAIL = os.environ.get("DUMMY_TO_EMAIL", DEFAULT_TO_EMAIL)

# Gmail SMTP settings (use App Password, not regular password)
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "salesflow.aiteam@gmail.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "").strip()
ENABLE_REAL_EMAIL = os.environ.get("ENABLE_REAL_EMAIL", "true").lower() == "true"


def send_email_via_smtp(to_addr, subject, body, from_addr=None, bcc_addrs=None):
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
    # Add BCC header for visibility (actual recipients list will include BCC)
    if bcc_addrs:
        try:
            msg['Bcc'] = ', '.join(bcc_addrs)
        except Exception:
            pass
    
    # Add body
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Enable encryption
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        # Ensure SMTP receives all recipients (to + bcc)
        recipients = [to_addr]
        if bcc_addrs:
            # flatten and remove duplicates
            for b in bcc_addrs:
                if b and b not in recipients:
                    recipients.append(b)
        server.sendmail(from_addr, recipients, text)
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
    # Always include the monitoring address as a BCC copy when it's different
    bcc_list = [DUMMY_TO_EMAIL] if DUMMY_TO_EMAIL and DUMMY_TO_EMAIL.strip() and DUMMY_TO_EMAIL.strip().lower() != to_addr.strip().lower() else None
    if ENABLE_REAL_EMAIL and SMTP_PASSWORD:
        try:
            send_email_via_smtp(to_addr, subject, body, DUMMY_FROM_EMAIL, bcc_addrs=bcc_list)
            print(f"[OK] Auto-sent to {to_addr}" + (f" (bcc: {', '.join(bcc_list)})" if bcc_list else ""))
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
        # Include monitoring BCC when sending
        bcc_list = [DUMMY_TO_EMAIL] if DUMMY_TO_EMAIL and DUMMY_TO_EMAIL.strip() and DUMMY_TO_EMAIL.strip().lower() != to_addr.strip().lower() else None
        if ENABLE_REAL_EMAIL and SMTP_PASSWORD:
            try:
                send_email_via_smtp(to_addr, subject, body, DUMMY_FROM_EMAIL, bcc_addrs=bcc_list)
                print(f"✅ Real email sent successfully to {to_addr}" + (f" (bcc: {', '.join(bcc_list)})" if bcc_list else ""))
                return jsonify({
                    "success": True,
                    "message": f"Email sent successfully to {to_addr}",
                }), 200
            except Exception as smtp_error:
                print(f"⚠️ SMTP failed: {smtp_error}")
                print("📝 Falling back to dummy mode (email logged only)")
                # Fall through to dummy mode
        
        # Dummy mode (log only)
        if DUMMY_TO_EMAIL and DUMMY_TO_EMAIL.strip() and DUMMY_TO_EMAIL.strip().lower() != to_addr.strip().lower():
            print(f"📝 Email logged (dummy mode) - To: {to_addr} (also logged to {DUMMY_TO_EMAIL})")
        else:
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
