# backend/agents/content_agent.py

from typing import Dict
from llm import call_llm
from utils import safe_json_parse
import json


def decide_tone(urgency: str, priority: str) -> str:
    if urgency == "Immediate" and priority == "High":
        return "Direct and confident"
    elif priority == "High":
        return "Professional and persuasive"
    else:
        return "Conversational and relationship-building"


def build_prompt(channel: str, classification: Dict, icp: Dict, tone: str) -> str:

    base_context = f"""
Target Name: {icp['name']}
Target Role: {icp['role']}
Company: {icp['company']}
Location: {icp['location']}
Business Intent: {classification['business_behavior']}
Urgency: {classification['urgency']}
Pain Points: {icp['pain_point_focus']}
Tone: {tone}
"""

    if channel == "Call":
        return f"""
You are a B2B sales expert.

Generate a structured call script.

{base_context}

Return STRICT JSON in this format:

{{
    "opening_line": "",
    "rapport_building": "",
    "value_pitch": "",
    "objection_handler": "",
    "closing_cta": ""
}}

Return ONLY JSON.
"""

    elif channel == "Email":
        return f"""
You are a B2B sales expert.

Generate a professional outreach email.

{base_context}

Return STRICT JSON:

{{
    "subject": "",
    "body": "",
    "cta": ""
}}

Return ONLY JSON.
"""

    else:
        return f"""
You are a B2B sales expert.

Generate a LinkedIn outreach message.

{base_context}

Return STRICT JSON:

{{
    "message": "",
    "cta": ""
}}

Return ONLY JSON.
"""


def content_generation_agent(state: Dict) -> Dict:
    print("🔥 A4 CONTENT AGENT STARTED")

    try:
        classification = state.get("classification", {})
        icp_list = state.get("icp_rankings", [])

        if not icp_list:
            return {**state, "generated_content": {}}

        top_icp = icp_list[0]
        channel = state.get("selected_channel", "Email")

        tone = decide_tone(
            classification.get("urgency", ""),
            top_icp.get("priority", "")
        )

        prompt = build_prompt(channel, classification, top_icp, tone)

        # ✅ Use your project LLM wrapper
        response = call_llm(prompt)

        print("🔍 RAW LLM RESPONSE:", response)

        parsed_output = safe_json_parse(response)

        # If JSON parsing fails, return raw response instead of empty dict
        if not parsed_output:
            parsed_output = {"raw_content": response}

        return {
            **state,
            "generated_content": parsed_output
        }

    except Exception as e:
        print("❌ Content Agent Error:", e)
        raise e
