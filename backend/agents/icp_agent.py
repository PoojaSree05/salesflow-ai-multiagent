import pandas as pd
import os
import random
from llm import call_llm


def find_best_matching_role(user_role, dataset_roles):
    """
    Uses a SINGLE LLM call to determine which dataset role
    is semantically closest to the user role.
    """

    # Safety check
    if not user_role or not dataset_roles:
        return ""

    role_list_text = "\n".join([f"- {role}" for role in dataset_roles])

    prompt = f"""
You are a semantic role matching engine.

User is looking for: "{user_role}"

From the following list of roles:

{role_list_text}

Return ONLY the single role from the list that is
most semantically similar to the user role.
Return exactly as written.
"""

    response = call_llm(prompt).strip()

    # Safety fallback
    if response not in dataset_roles:
        return dataset_roles[0]

    return response


def icp_agent(state):
    classification = state.get("classification", {})

    extracted_role = classification.get("role", "")
    extracted_location = classification.get("location", "")

    # Load dataset
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(BASE_DIR, "data", "mock_dataset.csv")

    df = pd.read_csv(file_path)

    if df.empty:
        return {"icp_rankings": []}

    # 🔹 Scoring logic using semantic matches and metadata
    scored_results = []

    # 🔹 Get unique roles from full dataset for LLM matching
    unique_roles = df["role"].dropna().unique().tolist()

    # 🔹 Fast path: exact or substring match (skip LLM)
    best_role_match = ""
    extracted_lower = (extracted_role or "").lower()
    for r in unique_roles:
        rl = str(r).lower()
        if extracted_lower in rl or rl in extracted_lower:
            best_role_match = r
            break
    # 🔹 Score rows with randomization for diversity
    for _, row in df.iterrows():
        score = 0
        row_role = str(row.get("role", "")).strip()
        # Role match scoring: Exact (60) or Substring (50)
        row_role_lower = row_role.lower()
        search_role_lower = str(extracted_role).strip().lower()

        if search_role_lower and row_role_lower == search_role_lower:
            score += 60
        elif search_role_lower and (search_role_lower in row_role_lower or row_role_lower in search_role_lower):
            score += 50
        elif "hr" in search_role_lower and "human resource" in row_role_lower:
            score += 50
        elif "human resource" in search_role_lower and "hr" in row_role_lower:
            score += 50

        # Location scoring (Soft match)
        row_loc = str(row.get("location", "")).lower()
        if extracted_location and str(extracted_location).lower() in row_loc:
            score += 30

        # Industry scoring (Soft match)
        row_ind = str(row.get("industry", "")).lower()
        ext_ind = str(classification.get("industry", "")).lower()
        if ext_ind and ext_ind in row_ind:
            score += 20

        # Engagement scoring
        engagement = row.get("engagement_score", 0)
        try:
            score += float(engagement) * 0.1
        except:
            pass

        # 🔹 Add random variance (±5 points) for lead diversity
        score += random.uniform(-5, 5)

        result_dict = row.to_dict()

        # Generate LinkedIn dynamically
        name = result_dict.get("name", "")
        linkedin_slug = name.lower().replace(" ", "")
        result_dict["linkedin_url"] = f"https://linkedin.com/in/{linkedin_slug}"

        if "linked_url" in result_dict:
            result_dict.pop("linked_url")

        result_dict["match_score"] = round(score, 2)

        scored_results.append(result_dict)

    # 🔹 Sort descending by score
        # 🔹 Sort descending by score
    scored_results.sort(key=lambda x: x["match_score"], reverse=True)

    # 🔹 Assign Priority Labels
    for icp in scored_results:
        if icp["match_score"] >= 90:
            icp["priority"] = "High"
        elif icp["match_score"] >= 75:
            icp["priority"] = "Medium"
        else:
            icp["priority"] = "Low"

    # 🔹 Return Top 5 only
    top_5 = scored_results[:5]

    return {
        "icp_rankings": top_5
    }