# backend/agents/content_agent.py
# Agent 4 – Content Generation Agent (A4)
# Purpose: Generate platform-optimized content for LinkedIn (A4), Email (A5), or Call (A6) channels.

from typing import Dict
from llm import call_llm
from utils import safe_json_parse


def decide_tone(urgency: str, priority: str) -> str:
    """Tone adaptation based on urgency and ICP priority."""
    urgency = str(urgency or "").lower()
    priority = str(priority or "").lower()
    if urgency in ["immediate", "high"] and priority == "high":
        return "direct, confident and time-sensitive"
    elif priority == "high":
        return "professional, persuasive and results-focused"
    return "consultative, warm and relationship-building"


def _base_context(classification: Dict, icp: Dict) -> str:
    loc = classification.get("location") or icp.get("location", "")
    return f"""
Target Name: {icp.get('name', '')}
Target Role: {icp.get('role', '')}
Company: {icp.get('company', '')}
Industry: {icp.get('industry', '')}
Location: {loc}
Business Intent: {classification.get('business_behavior') or classification.get('businessBehavior', '')}
User Intent: {classification.get('user_intent') or classification.get('intent', '')}
Urgency: {classification.get('urgency', 'Medium')}
Pain Points: {icp.get('pain_point_focus', '')}
Engagement Score: {icp.get('engagement_score', 50)}
"""


def _build_email_prompt(classification: Dict, icp: Dict, tone: str) -> str:
    return f"""You are a professional B2B sales email expert. Generate a campaign-quality outreach email.

{_base_context(classification, icp)}
Tone: {tone}

Return STRICT JSON only:
{{"subject": "Professional subject line (8-12 words)", "body": "Complete email body, plain text, 180-250 words", "cta": "Brief CTA"}}
"""


def _build_linkedin_prompt(classification: Dict, icp: Dict, tone: str) -> str:
    return f"""You are a B2B LinkedIn outreach specialist. Create a connection strategy.

{_base_context(classification, icp)}
Tone: {tone}

Return STRICT JSON only:
{{"connectionMessage": "Initial connection request under 100 words", "followUpMessage": "Follow-up message after connection"}}
"""


def _build_call_prompt(classification: Dict, icp: Dict, tone: str) -> str:
    return f"""You are a B2B sales expert. Generate a structured call script.

{_base_context(classification, icp)}
Tone: {tone}

Return STRICT JSON only:
{{"opening_line": "", "rapport_building": "", "problem_exploration": "", "value_pitch": "", "objection_handling": "", "closing_cta": ""}}
"""


def _fallback_content(channel: str, icp: Dict, classification: Dict) -> Dict:
    """Fallback when LLM fails – rule-based content generation."""
    name = icp.get("name", "there")
    company = icp.get("company", "your organization")
    role = icp.get("role", "professional")
    industry = icp.get("industry", "your industry")
    pain = icp.get("pain_point_focus", "operational efficiency")

    if channel == "Email":
        body = f"""Dear {name},

I hope this email finds you well. As the {role} at {company}, a leading {industry} company, I understand the challenges of {pain}.

We help companies like yours streamline processes and improve efficiency. Would a brief 15-minute call next week make sense to explore how we can support {company}'s goals?

Best regards,
SalesFlow AI Team"""
        return {"subject": f"Quick intro – {company} growth opportunity", "body": body, "cta": "Schedule a call"}

    if channel == "LinkedIn":
        conn = f"Hi {name}, I've been following {company}'s growth in {industry}. Would love to connect and explore how we can support your team's goals."
        follow = f"Thanks for connecting! I noticed your focus on {pain}. Would a quick call be helpful to discuss solutions for companies like {company}?"
        return {"connectionMessage": conn, "followUpMessage": follow}

    # Call
    script = f"Hi {name}, this is [Your Name] from [Company]. I noticed {company}'s focus on {pain}. We help {industry} companies streamline operations. Do you have 3 minutes to discuss, or would tomorrow work better?"
    return {
        "opening_line": f"Hi {name}, this is [Your Name]. Thanks for taking my call.",
        "rapport_building": f"Reference {company}'s work in {industry}.",
        "problem_exploration": f"Understand their challenges with {pain}.",
        "value_pitch": f"Share how we help similar companies in {industry}.",
        "objection_handling": "Acknowledge concerns, offer to send details, suggest alternative timing.",
        "closing_cta": "Propose a 15-min call next week.",
    }


def content_generation_agent(state: Dict) -> Dict:
    """
    Agent 4 – Content Generation Agent.
    Generates platform-specific content for the channel selected by Agent 3.
    Output channels: LinkedIn (A4), Email (A5), Call (A6).
    """
    try:
        classification = state.get("classification", {})
        icp_list = state.get("icp_rankings", [])
        channel = state.get("selected_channel", "Email")

        if not icp_list:
            return {**state, "generated_content": {}}

        top_icp = icp_list[0]
        tone = decide_tone(
            classification.get("urgency", "Medium"),
            top_icp.get("priority", "Medium"),
        )

        if channel == "Email":
            prompt = _build_email_prompt(classification, top_icp, tone)
        elif channel == "LinkedIn":
            prompt = _build_linkedin_prompt(classification, top_icp, tone)
        else:
            prompt = _build_call_prompt(classification, top_icp, tone)

        response = call_llm(prompt)
        parsed = safe_json_parse(response)

        if not parsed:
            parsed = _fallback_content(channel, top_icp, classification)

        return {**state, "generated_content": parsed}

    except Exception as e:
        print("Content Generation Agent Error:", e)
        icp_list = state.get("icp_rankings", [])
        channel = state.get("selected_channel", "Email")
        if icp_list:
            fallback = _fallback_content(channel, icp_list[0], state.get("classification", {}))
            return {**state, "generated_content": fallback}
        return {**state, "generated_content": {}}
