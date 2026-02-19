import json
import re
from llm import call_llm

# Role keywords for fallback when LLM unavailable
ROLE_KEYWORDS = [
    ("hr", "HR Manager"), ("human resource", "HR Manager"), ("recruitment", "HR Manager"),
    ("recruit", "HR Manager"), ("hiring", "HR Manager"), ("talent", "HR Manager"),
    ("cto", "CTO"), ("founder", "Founder"), ("marketing", "Marketing Head"),
    ("operations", "Operations Manager"), ("sales", "Sales Director"),
    ("healthcare", "Operations Manager"), ("research", "Product Manager"),
    ("researching", "Product Manager"), ("ai ", "Product Manager"),
    ("solutions", "Operations Manager"), ("technology", "CTO"),
]

# Industry keywords -> dataset industry values
INDUSTRY_KEYWORDS = [
    ("healthcare", "EdTech"), ("ai ", "AI"), ("technology", "AI"),
    ("saas", "SaaS"), ("fintech", "Fintech"), ("e-commerce", "E-commerce"),
    ("edtech", "EdTech"), ("manufacturing", "Manufacturing"),
]

# City names for fallback extraction
CITY_WORDS = ["london", "new york", "berlin", "mumbai", "singapore", "india", "uk", "usa"]


def extract_from_keywords(user_input):
    """Fallback: extract role/location/intent/industry from user input when LLM fails."""
    text = (user_input or "").lower()
    role, location, intent, industry = "", "", "", ""
    for kw, r in ROLE_KEYWORDS:
        if kw in text:
            role = r
            break
    for city in CITY_WORDS:
        if city in text:
            location = city.title()
            break
    if any(w in text for w in ["healthcare", "health"]):
        industry = "Healthcare"
    elif any(w in text for w in ["ai", "technology", "tech"]):
        industry = "AI"
    if any(w in text for w in ["research", "researching", "exploring", "looking"]):
        intent = "Researching solutions"
    elif any(w in text for w in ["healthcare", "ai", "technology"]):
        intent = "Evaluating AI/tech solutions"
    if not role and (industry or intent):
        role = "Product Manager"
    return {"role": role, "location": location, "urgency": "Medium", "time_context": "", "business_behavior": text[:80], "user_intent": intent, "industry": industry}


def safe_json_parse(text):
    """
    Safely extract JSON from LLM output.
    """
    if not text:
        return None

    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == -1:
        print("[WARN] No JSON boundaries found in LLM output.")
        return None

    json_str = text[start:end]

    # Fix only safe formatting issues
    json_str = json_str.replace("'", '"')  # single → double quotes
    json_str = re.sub(r",\s*}", "}", json_str)  # remove trailing commas

    try:
        parsed = json.loads(json_str)
        return parsed
    except Exception as e:
        print("[WARN] JSON parse failed:", e)
        print("Raw string was:", json_str)
        return None


def normalize_classification(data):
    """
    Normalize LLM output for consistency.
    """
    if not data:
        return None

    role = str(data.get("role", "")).strip()
    location = str(data.get("location", "")).strip()

    urgency_raw = str(data.get("urgency", "")).strip()
    urgency = urgency_raw if urgency_raw else ""  # leave empty if not mentioned

    time_context_raw = str(data.get("time_context", "")).strip()
    time_context = time_context_raw if time_context_raw else ""

    behavior = str(data.get("business_behavior", "")).strip()
    intent = str(data.get("user_intent", "")).strip()
    industry = str(data.get("industry", "")).strip()

    return {
        "role": role,
        "location": location,
        "industry": industry,
        "urgency": urgency,
        "time_context": time_context,
        "business_behavior": behavior,
        "user_intent": intent,
    }


def classification_agent(state):
    try:
        user_input = state.get("user_input", "")

        if not user_input:
            print("[WARN] Empty user_input, returning defaults.")
            return {
                "classification": {
                    "role": "",
                    "location": "",
                    "urgency": "",
                    "time_context": "",
                    "business_behavior": "",
                    "user_intent": ""
                }
            }

        prompt = f"""
You are a strict business data extraction engine.

Extract structured business information from the text below.

Text:
"{user_input}"

RULES:
- Return ONLY valid JSON.
- Do NOT explain anything.
- Do NOT add extra text.
- Role must be a clean job title only.
- Location must be ONLY the city name.
- Urgency must be ONE of: ["Low", "Medium", "High", "Immediate"]
- If urgency words like urgent, immediately, asap appear → use "Immediate"
- If urgency not mentioned → leave as empty string ""
- If field not present → use empty string ""

Return EXACTLY this JSON format:

{{
  "role": "",
  "location": "",
  "urgency": "",
  "time_context": "",
  "business_behavior": "",
  "user_intent": ""
}}
"""

        response = call_llm(prompt)
        print("LLM raw response:", response)

        classification_data = safe_json_parse(response)

        if not classification_data:
            print("[WARN] LLM did not return valid JSON, using keyword fallback.")
            classification_data = extract_from_keywords(user_input)

        classification_data = normalize_classification(classification_data)

        print("[OK] Final classification:", classification_data)
        return {"classification": classification_data}

    except Exception as e:
        print("Classification Agent Error:", e)
        user_input = state.get("user_input", "")
        return {"classification": extract_from_keywords(user_input)}