import pandas as pd
import os
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

    # 🔹 Location pre-filter
    if extracted_location:
        df = df[df["location"].str.lower().str.contains(str(extracted_location).lower(), na=False)]

    if df.empty:
        return {"icp_rankings": []}

    # 🔹 Get unique roles from filtered dataset
    unique_roles = df["role"].dropna().unique().tolist()

    # 🔹 Single LLM call to find best role
    best_role_match = find_best_matching_role(extracted_role, unique_roles)

    scored_results = []

    # 🔹 Score rows
    for _, row in df.iterrows():
        score = 0
        row_role = str(row.get("role", "")).strip()

        # Role match scoring
        if best_role_match and row_role.lower() == best_role_match.strip().lower():
            score += 60

        # Location scoring (already filtered)
        score += 30

        # Engagement scoring
        engagement = row.get("engagement_score", 0)
        try:
            score += float(engagement) * 0.1
        except:
            pass

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

    
    