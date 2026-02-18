from llm import call_llm
from utils import safe_json_parse


def linkedin_agent(state):
    classification = state.get("classification", {})
    icps = state.get("icp_rankings", [])

    if not icps:
        return {**state, "generated_content": {}}

    icp = icps[0]  # Top ICP only

    prompt = f"""
You are an expert B2B LinkedIn outreach specialist. Create a personalized connection strategy.

PROSPECT DETAILS:
Name: {icp.get("name")}
Role: {icp.get("role")}
Company: {icp.get("company")}
Industry: {icp.get("industry")}
Location: {classification.get("location")}
Engagement Score: {icp.get("engagement_score")}
Pain Points: {icp.get("pain_point_focus")}

BUSINESS CONTEXT:
Intent: {classification.get("intent")}
Behavior: {classification.get("businessBehavior")}
Urgency: {classification.get("urgency")}

CONNECTION MESSAGE STRUCTURE:
- Personalized opening with their name
- Show genuine interest in their profile/role
- Reference their company and industry context
- Mention something relevant to their pain points
- Soft invitation to connect
- Keep it under 100 words

FOLLOW-UP MESSAGE (after connection):
- Thank them for connecting
- Reference their recent activity or role
- Share relevant insight or resource
- Suggest a value-add conversation
- Specific but flexible meeting proposal
- Keep it helpful, not salesy

INSTRUCTIONS:
- Be genuine and consultative
- Show you've researched them
- Focus on value-add, not selling
- Professional but personable tone
- Plain text format (no markdown)

Return STRICT JSON:

{{
  "connectionMessage": "Initial connection request message (under 100 words)",
  "followUpMessage": "Follow-up message that references your conversation and adds specific value"
}}

Return ONLY valid JSON. No explanation.
"""

    try:
        response = call_llm(prompt)
        parsed = safe_json_parse(response)

        if not parsed:
            parsed = {
                "connectionMessage": f"Hi {icp.get('name')}, I've been following {icp.get('company')}'s growth in {icp.get('industry')}. Would love to connect and explore how we can support your team's goals.",
                "followUpMessage": f"Thanks for connecting! I noticed your focus on {icp.get('pain_point_focus', 'talent acquisition')}. I recently came across a case study on streamlining this for companies like {icp.get('company')}. Would a quick call be helpful?"
            }

    except Exception as e:
        print("LinkedIn Agent Error:", e)
        parsed = {}

    return {
        **state,
        "generated_content": parsed
    }
