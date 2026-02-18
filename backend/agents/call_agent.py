from llm import call_llm
from utils import safe_json_parse


def call_agent(state):
    classification = state.get("classification", {})
    icps = state.get("icp_rankings", [])

    if not icps:
        return {**state, "generated_content": {}}

    icp = icps[0]

    prompt = f"""
You are an expert B2B sales call strategist. Create a personalized, high-impact call script.

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

CALL SCRIPT STRUCTURE:
1. Professional opening with prospect name and your company
2. Brief reason for the call (specific to their industry/pain points)
3. Acknowledge their role and company
4. Reference their engagement/activity signals
5. Ask 1-2 qualifying questions about their needs
6. Position your solution value
7. Handle potential objections
8. Clear closing CTA with specific next steps
9. Professional goodbye

INSTRUCTIONS:
- Create a natural, conversational script (not robotic)
- Show understanding of their specific pain points
- Be genuine and consultative
- Include specific company/industry references
- Keep it concise but comprehensive
- Format as plain text paragraphs

Return STRICT JSON:

{{
  "opening_line": "Professional greeting with prospect name and your company",
  "rapport_building": "2-3 sentences about their company/industry to build credibility",
  "problem_exploration": "2-3 natural questions to understand their specific needs",
  "value_pitch": "2-3 sentences positioning your solution for their pain points",
  "objection_handling": "How to address common concerns about implementing new solutions",
  "closing_cta": "Specific ask - meeting time, next step, or demo"
}}

Return ONLY valid JSON. No explanation.
"""

    try:
        response = call_llm(prompt)
        parsed = safe_json_parse(response)

        if not parsed:
            parsed = {
                "opening_line": f"Hi {icp.get('name')}, this is [Your Name] calling regarding solutions for {icp.get('company')}.",
                "rapport_building": f"I noticed {icp.get('company')} is active in {icp.get('industry', 'your industry')}.",
                "problem_exploration": "What are your current biggest challenges with staffing and talent retention?",
                "value_pitch": "We help companies like yours streamline hiring and reduce costs by 30%.",
                "objection_handling": "Many clients had the same concerns initially, but our solution integrates seamlessly.",
                "closing_cta": "Would next Tuesday or Wednesday work better for a 15-minute call to explore this further?"
            }

    except Exception as e:
        print("Call Agent Error:", e)
        parsed = {}

    return {
        **state,
        "generated_content": parsed
    }
