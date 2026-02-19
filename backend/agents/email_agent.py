from llm import call_llm
from utils import safe_json_parse


def email_agent(state):
    classification = state.get("classification", {})
    icps = state.get("icp_rankings", [])

    if not icps:
        return {**state, "generated_content": {}}

    icp = icps[0]

    # Derive tone / intensity from urgency + priority
    urgency = classification.get("urgency", "Medium")
    priority = icp.get("priority", "Medium")
    engagement = icp.get("engagement_score", 0)

    if str(urgency).lower() in ["immediate", "high"] and str(priority).lower() == "high":
        tone = "direct, confident and time-sensitive"
    elif str(priority).lower() == "high" or engagement >= 80:
        tone = "professional, persuasive and results-focused"
    else:
        tone = "consultative, warm and relationship-building"

    prompt = f"""
You are a professional B2B sales email expert writing campaign-quality outreach emails.

PROSPECT INFORMATION:
- Name: {icp.get("name")}
- Role: {icp.get("role")}
- Company: {icp.get("company")}
- Industry: {icp.get("industry")}
- Location: {classification.get("location")}
- Company Size: {icp.get("company_size")}
- Engagement / Interest Score: {icp.get("engagement_score")}
- Priority Level: {icp.get("priority")}
- Primary Pain Points: {icp.get("pain_point_focus")}

BUSINESS CONTEXT:
- Intent: {classification.get("user_intent") or classification.get("intent")}
- Behavior: {classification.get("business_behavior") or classification.get("businessBehavior")}
- Urgency: {classification.get("urgency")}
- Tone: {tone}

CRITICAL: You MUST follow this EXACT professional email template structure:

---
EMAIL STRUCTURE (MANDATORY):

1. GREETING (Line 1):
   "Dear {icp.get("name")},"

2. OPENING COURTESY (Line 2):
   "I hope this email finds you well."

3. FIRST PARAGRAPH (3-4 sentences):
   Start with: "As the {icp.get("role")} at {icp.get("company")}, a leading {icp.get("industry")} company in {classification.get("location")}, I understand that your role involves managing various aspects of [role-specific responsibilities based on their role - e.g., 'human resources, including recruitment, employee relations, and policy development' OR 'technology strategy, including digital transformation, security, and scaling infrastructure' OR 'marketing operations, including lead generation, brand positioning, and customer acquisition']."

4. SECOND PARAGRAPH (2-3 sentences):
   "I'm writing to introduce our innovative [solution type - e.g., 'HR solution' OR 'technology platform' OR 'marketing platform'] designed specifically for {icp.get("industry")} industries. With an interest score of {icp.get("engagement_score")} and your role as a decision-maker, it appears that you might be in the market for such a service."

5. VALUE PROPOSITION (2-3 sentences):
   "Our platform can help streamline {icp.get("pain_point_focus")} and [mention 1-2 specific benefits relevant to their pain points]. We've seen companies in {icp.get("industry")} achieve [generic positive outcome - e.g., 'significant improvements in efficiency' OR 'better alignment between teams' OR 'reduced operational costs']."

6. CLOSING PARAGRAPH (2 sentences):
   "I would welcome the opportunity to discuss how we can support {icp.get("company")}'s goals. Would you be available for a brief 15-20 minute call next week to explore this further?"

7. SIGN-OFF:
   "Best regards,
   [Your Name]
   SalesFlow AI Team"

---
REQUIREMENTS:
- Professional, clear, and campaign-quality
- Total length: 180-250 words
- Plain text only (NO markdown, NO asterisks, NO emojis, NO special formatting)
- Sound natural and consultative, not salesy
- Use the exact engagement score number provided: {icp.get("engagement_score")}
- Adapt role-specific responsibilities based on their actual role
- Keep solution type generic (e.g., "HR solution", "technology platform", "marketing solution")
- Do NOT invent specific numbers or metrics - keep it professional and believable

RETURN FORMAT (STRICT JSON ONLY):
{{
  "subject": "Professional subject line mentioning their role/company/benefit (8-12 words max)",
  "body": "Complete email body following the EXACT structure above, ready to send",
  "cta": "Brief CTA suggestion (e.g., 'Schedule a 15-minute call next week')"
}}

Return ONLY valid JSON. No explanation, no extra text.
"""

    try:
        response = call_llm(prompt)
        parsed = safe_json_parse(response)

        if not parsed:
            # Professional fallback template matching the exact structure
            name = icp.get("name", "")
            role = icp.get("role", "professional")
            company = icp.get("company", "your organization")
            industry = icp.get("industry", "your industry")
            location = classification.get("location", "")
            engagement = icp.get("engagement_score", 0)
            pain_points = icp.get("pain_point_focus", "operational efficiency")
            
            # Determine role-specific responsibilities
            role_responsibilities = {
                "hr": "human resources, including recruitment, employee relations, and policy development",
                "cto": "technology strategy, including digital transformation, security, and scaling infrastructure",
                "marketing": "marketing operations, including lead generation, brand positioning, and customer acquisition",
            }
            responsibilities = role_responsibilities.get(role.lower()[:3], "key operational areas and strategic initiatives")
            
            location_text = f" in {location}" if location else ""
            
            fallback_body = f"""Dear {name},

I hope this email finds you well. As the {role} at {company}, a leading {industry} company{location_text}, I understand that your role involves managing various aspects of {responsibilities}.

I'm writing to introduce our innovative solution designed specifically for {industry} industries. With an interest score of {engagement} and your role as a decision-maker, it appears that you might be in the market for such a service.

Our platform can help streamline {pain_points} and improve operational efficiency. We've seen companies in {industry} achieve significant improvements in their core processes.

I would welcome the opportunity to discuss how we can support {company}'s goals. Would you be available for a brief 15-20 minute call next week to explore this further?

Best regards,
[Your Name]
SalesFlow AI Team"""
            
            parsed = {
                "subject": f"Exploring {role} solutions for {company}",
                "body": response if response else fallback_body,
                "cta": "Schedule a 15-minute call next week to explore this further"
            }

    except Exception as e:
        print("Email Agent Error:", e)
        parsed = {}

    return {
        **state,
        "generated_content": parsed
    }
