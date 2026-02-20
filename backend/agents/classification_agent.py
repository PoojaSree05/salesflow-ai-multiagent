import json
import re
from llm import call_llm


# Minimal fallback keywords (light only)
ROLE_KEYWORDS = [
    # HR
    ("hr manager", "HR Manager"),
    ("human resource", "HR Manager"),
    ("hr", "HR Manager"),
    ("recruitment", "HR Manager"),
    ("recruiter", "HR Manager"),
    ("talent", "HR Manager"),

    # Sales
    ("sales director", "Sales Director"),
    ("sales head", "Sales Director"),
    ("sales manager", "Sales Manager"),
    ("sales", "Sales Director"),

    # Tech
    ("cto", "CTO"),
    ("chief technology officer", "CTO"),
    ("tech head", "CTO"),
    ("technology head", "CTO"),

    # Marketing
    ("marketing head", "Marketing Head"),
    ("marketing manager", "Marketing Head"),
    ("marketing", "Marketing Head"),

    # Operations
    ("operations manager", "Operations Manager"),
    ("operations head", "Operations Manager"),
    ("operations", "Operations Manager"),

    # Founder / Leadership
    ("founder", "Founder"),
    ("co-founder", "Founder"),
    ("ceo", "Founder"),
]


CITY_WORDS = [
    "london",
    "new york",
    "newyork",
    "berlin",
    "mumbai",
    "singapore",
    "india",
    "uk",
    "usa",
    "united kingdom",
    "united states"
]


INDUSTRY_WORDS = [
    ("healthcare", "Healthcare"),
    ("ai", "AI"),
    ("technology", "AI"),
    ("saas", "SaaS"),
    ("fintech", "Fintech"),
    ("e-commerce", "E-commerce"),
    ("manufacturing", "Manufacturing"),
]


# ===============================
# Safe JSON Parser
# ===============================
def safe_json_parse(text):
    if not text:
        return None

    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == -1:
        return None

    json_str = text[start:end]

    try:
        return json.loads(json_str)
    except:
        return None


# ===============================
# Light Fallback
# ===============================
def fallback_extraction(user_input):
    text = user_input.lower().strip()
    role = ""
    location = ""
    industry = ""
    urgency = ""
    intent = ""

    # 🔹 Role detection
    for kw, value in ROLE_KEYWORDS:
        if kw in text:
            role = value
            break

    # 🔹 Location detection
    for city in CITY_WORDS:
        if city in text:
            location = city.title()
            break

    # 🔹 Industry detection
    for kw, ind in INDUSTRY_WORDS:
        if kw in text:
            industry = ind
            break

    # 🔹 Urgency detection
    if any(word in text for word in ["urgent", "immediately", "asap", "right now"]):
        urgency = "Immediate"
    elif any(word in text for word in ["soon", "quickly", "this week"]):
        urgency = "High"
    elif any(word in text for word in ["low priority", "later"]):
        urgency = "Low"

    # 🔹 Intent detection
    if any(word in text for word in ["hire", "hiring", "need"]):
        intent = "Hiring intent"
    elif any(word in text for word in ["research", "exploring", "looking"]):
        intent = "Researching solutions"
    elif role:
        intent = "Looking for contact"

    return {
        "role": role,
        "location": location,
        "industry": industry,
        "urgency": urgency,
        "time_context": "",
        "business_behavior": "",
        "user_intent": intent
    }


# ===============================
# Classification Agent
# ===============================
def classification_agent(state):
    try:
        user_input = state.get("user_input", "")

        if not user_input:
            return {"classification": fallback_extraction("")}

        # Short + structured prompt (Phi-3 friendly)
        prompt = f"""
Extract business information.

Text:
{user_input}

Return ONLY JSON:

{{
 "role": "",
 "location": "",
 "industry": "",
 "urgency": "",
 "time_context": "",
 "business_behavior": "",
 "user_intent": ""
}}
 
Rules:
- Role = job title mentioned
- Location = city only
- Urgency = Low | Medium | High | Immediate
- If not present use ""
"""

        response = call_llm(prompt)

        classification_data = safe_json_parse(response)

        # If LLM fails → fallback
        if not classification_data:
            classification_data = fallback_extraction(user_input)

        # If role missing → fallback role only
        if not classification_data.get("role"):
            fallback_data = fallback_extraction(user_input)
            classification_data["role"] = fallback_data["role"]
            classification_data["location"] = fallback_data["location"]
            classification_data["industry"] = fallback_data["industry"]

        return {"classification": classification_data}

    except Exception:
        return {"classification": fallback_extraction(state.get("user_input", ""))}
