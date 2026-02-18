import json
import re
from llm import call_llm


def safe_json_parse(text):
    """
    Safely extract JSON from LLM output.
    """

    if not text:
        return None

    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == -1:
        return None

    json_str = text[start:end]

    # Fix only safe formatting issues
    json_str = json_str.replace("'", '"')  # single → double quotes
    json_str = re.sub(r",\s*}", "}", json_str)  # remove trailing commas

    try:
        return json.loads(json_str)
    except Exception:
        return None


def normalize_classification(data):
    """
    Stabilize and normalize LLM output.
    """

    if not data:
        return None

    # 🔹 Role
    role = str(data.get("role", "")).strip()

    # 🔹 Location (keep only first word if sentence)
    location = str(data.get("location", "")).strip()
    if location:
        location = location.split()[0]

    # 🔹 Urgency Normalization
    urgency_raw = str(data.get("urgency", "")).lower()

    if any(word in urgency_raw for word in ["urgent", "immediate", "asap"]):
        urgency = "Immediate"
    elif "high" in urgency_raw:
        urgency = "High"
    elif "low" in urgency_raw:
        urgency = "Low"
    else:
        urgency = "Medium"

    # 🔹 Time Context Auto-Fix
    time_context_raw = str(data.get("time_context", "")).strip()

    if time_context_raw:
        time_context = time_context_raw
    elif urgency == "Immediate":
        time_context = "Immediate"
    elif urgency == "High":
        time_context = "Short-term"
    elif urgency == "Low":
        time_context = "Long-term"
    else:
        time_context = "Short-term"

    # 🔹 Behavior with fallback
    behavior = str(data.get("business_behavior", "")).strip()
    if not behavior:
        behavior = "Active Interest"

    # 🔹 Intent with fallback
    intent = str(data.get("user_intent", "")).strip()
    if not intent:
        intent = "Business Growth"

    return {
        "role": role,
        "location": location,
        "urgency": urgency,
        "timeContext": time_context,
        "businessBehavior": behavior,
        "intent": intent,
    }


def classification_agent(state):
    try:
        user_input = state.get("user_input", "")

        if not user_input:
            return {
                "classification": {
                    "role": "",
                    "location": "",
                    "urgency": "Medium",
                    "time_context": "Short-term",
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
- If unclear → use "Medium"
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

        # 🔹 Call LLM
        try:
            response = call_llm(prompt)
        except Exception as e:
            print("LLM call failed:", e)
            response = ""

        classification_data = safe_json_parse(response)

        # 🔹 Always apply keyword-based extraction as enrichment/fallback
        if not classification_data:
            classification_data = {}

        # Extract missing fields from keywords if not populated by LLM
        user_input_lower = user_input.lower()

        # Role extraction (if empty or missing)
        if not classification_data.get("role"):
            role_match = re.search(
                r"(HR Director|HR Manager|Human Resource Manager|Sales Director|CTO|Founder|Marketing Head|Product Manager|Operations Manager|VP Sales)",
                user_input,
                re.IGNORECASE,
            )
            if role_match:
                classification_data["role"] = role_match.group(0)

        # Location extraction (if empty or missing)
        if not classification_data.get("location"):
            location_match = re.search(r"(?:in|at)\s+(?:a\s+)?([A-Za-z]+)", user_input)
            if not location_match:
                location_match = re.search(r"(UK|US|London|New York|Manchester|Birmingham|Leeds|Glasgow|Edinburgh|Berlin|Singapore|Mumbai)", user_input)
            if location_match:
                classification_data["location"] = location_match.group(1) if location_match.lastindex else location_match.group(0)

        # Urgency extraction (if empty or missing)
        if not classification_data.get("urgency"):
            urgency = "Medium"
            if re.search(r"(urgent|immediately|asap|right now|urgent need)", user_input_lower):
                urgency = "Immediate"
            elif re.search(r"(high|priority|quickly|soon)", user_input_lower):
                urgency = "High"
            elif re.search(r"(next quarter|future|exploring|interested)", user_input_lower):
                urgency = "Low"
            classification_data["urgency"] = urgency

        # Intent extraction (if empty or missing)
        if not classification_data.get("user_intent"):
            intent = "Growth"
            if re.search(r"(hiring|recruit|expand|staffing|need)", user_input_lower):
                intent = "Hiring"
            elif re.search(r"(sales|lead|revenue|growth|expanding|scaling)", user_input_lower):
                intent = "Sales Growth"
            elif re.search(r"(retain|retention|engagement|culture|turnover)", user_input_lower):
                intent = "Retention"
            classification_data["user_intent"] = intent

        # Behavior extraction (if empty or missing) - KEY FIX
        if not classification_data.get("business_behavior"):
            behavior = "General Interest"
            if re.search(r"(actively|actively hiring|recruiting|posting|urgent.*hiring|immediately.*hire)", user_input_lower):
                behavior = "Active recruitment"
            elif re.search(r"(high turnover|churn|employee loss|turnover|attrition)", user_input_lower):
                behavior = "High employee turnover"
            elif re.search(r"(expansion|scaling|growth|expanding|scale|rapid)", user_input_lower):
                behavior = "Business expansion"
            elif re.search(r"(optimization|efficiency|improve|streamline)", user_input_lower):
                behavior = "Process optimization"
            elif re.search(r"(future|exploring|interested|opportunities)", user_input_lower):
                behavior = "Exploratory interest"
            classification_data["business_behavior"] = behavior

        # 🔹 Normalize final output
        classification_data = normalize_classification(classification_data)

        return {"classification": classification_data}

    except Exception as e:
        print("Classification Agent Error:", e)

        return {
            "classification": {
                "role": "",
                "location": "",
                "urgency": "Medium",
                "time_context": "Short-term",
                "business_behavior": "",
                "user_intent": ""
            }
        }
