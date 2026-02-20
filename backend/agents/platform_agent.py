from llm import call_llm


def decide_channel_with_rules(classification, icp):
    """
    Channel selection using priority-based decision tree:
    
    PRIORITY ORDER (most important first):
    1. URGENCY (Immediate/High → Call, Medium/Low → continue)
    2. ENGAGEMENT SCORE (High ≥75 → Email, Medium 40-74 → Email, Low <40 → LinkedIn)
    3. ICP PRIORITY LEVEL (High priority → Email, Low → LinkedIn)
    4. BUSINESS BEHAVIOR (Active → Email, Exploratory → LinkedIn)
    
    Default: Email (most professional and scalable)
    """
    # Extract all decision factors (support both snake_case and camelCase from different sources)
    urgency = str(classification.get("urgency") or "").lower()
    engagement_score = int(icp.get("engagement_score", 50))
    icp_priority = str(icp.get("priority", "Medium")).lower()
    business_behavior = str(classification.get("business_behavior") or classification.get("businessBehavior", "")).lower()
    
    # ==========================================
    # PRIORITY 1: URGENCY (First Constraint)
    # ==========================================
    # Immediate/High urgency → Always Call (time-sensitive, direct)
    if urgency in ["immediate", "high"]:
        return "Call"
    
    # ==========================================
    # PRIORITY 2: ENGAGEMENT SCORE (Second Constraint)
    # ==========================================
    # High engagement (≥75) → Email (they're interested, personalized outreach)
    if engagement_score >= 75:
        return "Email"
    
    # Low engagement (<40) → LinkedIn (soft, non-intrusive approach)
    if engagement_score < 40:
        return "LinkedIn"
    
    # ==========================================
    # PRIORITY 3: ICP PRIORITY LEVEL (Third Constraint)
    # ==========================================
    # Medium engagement (40-74) → Check ICP Priority
    if icp_priority == "high":
        return "Email"  # High priority ICP → Email (worth personalized effort)
    
    if icp_priority == "low":
        return "LinkedIn"  # Low priority ICP → LinkedIn (exploratory)
    
    # ==========================================
    # PRIORITY 4: BUSINESS BEHAVIOR (Fourth Constraint)
    # ==========================================
    # Medium engagement + Medium priority → Check behavior
    active_keywords = ["active", "urgent", "hiring", "expansion", "scaling", "immediate"]
    exploratory_keywords = ["exploring", "exploratory", "interested", "future", "considering"]
    
    if any(keyword in business_behavior for keyword in active_keywords):
        return "Email"  # Active behavior → Email
    
    if any(keyword in business_behavior for keyword in exploratory_keywords):
        return "LinkedIn"  # Exploratory → LinkedIn
    
    # ==========================================
    # DEFAULT: Email (most professional and scalable)
    # ==========================================
    return "Email"


def decide_channel_with_llm(classification, icp):
    prompt = f"""
You are an AI communication strategy agent.

User Classification:
Role Needed: {classification.get("role")}
Location: {classification.get("location")}
Urgency: {classification.get("urgency")}
Business Behavior: {classification.get("business_behavior") or classification.get("businessBehavior")}
User Intent: {classification.get("user_intent") or classification.get("intent")}

ICP Profile:
Role: {icp.get("role")}
Company Size: {icp.get("company_size")}
Industry: {icp.get("industry")}
Engagement Score: {icp.get("engagement_score")}
Priority Level: {icp.get("priority")}

CHANNEL SELECTION RULES (Priority Order):
1. URGENCY: Immediate/High → Call (time-sensitive, direct)
2. ENGAGEMENT SCORE: 
   - High (≥75) → Email
   - Low (<40) → LinkedIn
   - Medium (40-74) → Check ICP Priority
3. ICP PRIORITY: High → Email, Low → LinkedIn
4. BUSINESS BEHAVIOR: Active → Email, Exploratory → LinkedIn
5. DEFAULT: Email (professional, scalable)

Return ONLY one word:
Call, Email, or LinkedIn
"""

    try:
        channel = call_llm(prompt).strip()

        if channel in ["Call", "Email", "LinkedIn"]:
            return channel
        return "Email"  # Default fallback

    except:
        return "Email"


def get_channel_reasoning(classification, icp, selected_channel):
    urgency = str(classification.get("urgency") or "").lower()
    engagement_score = int(icp.get("engagement_score", 50))
    icp_priority = str(icp.get("priority", "Medium"))
    business_behavior = str(classification.get("business_behavior") or "").lower()

    reason_parts = []

    # 🔹 Urgency explanation
    if urgency in ["immediate", "high"]:
        reason_parts.append(
            f"You indicated urgency ('{urgency}'), suggesting time-sensitive action."
        )

    # 🔹 Engagement explanation
    if engagement_score >= 75:
        reason_parts.append(
            f"The lead has a strong engagement score ({engagement_score}), showing high interest."
        )
    elif engagement_score < 40:
        reason_parts.append(
            f"The engagement score is low ({engagement_score}), indicating early-stage interest."
        )
    else:
        reason_parts.append(
            f"The engagement score is moderate ({engagement_score})."
        )

    # 🔹 ICP Priority explanation
    reason_parts.append(
        f"This prospect is classified as {icp_priority} priority."
    )

    # 🔹 Final recommendation sentence
    if selected_channel == "Call":
        conclusion = "Therefore, a direct call is recommended to act quickly."
    elif selected_channel == "Email":
        conclusion = "Therefore, sending a personalized email is the most effective approach."
    else:  # LinkedIn
        conclusion = "Therefore, a LinkedIn message is recommended as a softer outreach strategy."

    full_reason = " ".join(reason_parts) + " " + conclusion

    return full_reason

def platform_decision_agent(state):
    classification = state.get("classification", {})
    icps = state.get("icp_rankings", [])

    if not icps:
        return {**state}

    for icp in icps:
        selected_channel = decide_channel_with_rules(classification, icp)
        icp["recommended_channel"] = selected_channel
        icp["channel_reasoning"] = get_channel_reasoning(classification, icp, selected_channel)

    top_icp = icps[0]
    selected_channel = top_icp["recommended_channel"]
    reasoning = top_icp.get("channel_reasoning", "Recommended based on prospect engagement and urgency signals.")

    return {
        **state,
        "icp_rankings": icps,
        "selected_channel": selected_channel,
        "channel_reasoning": reasoning
    }
