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
    if urgency in ["immediate", "immediately", "high", "urgent"]:
        return "Call"
    
    # ==========================================
    # PRIORITY 2: INTENT-BASED OVERRIDE (Soft Approach)
    # ==========================================
    # If the user explicitly wants to explore/research, stay on LinkedIn
    # regardless of engagement score (calling a researcher is intrusive)
    is_exploratory = "exploratory" in business_behavior or "research" in str(classification.get("user_intent", "")).lower()
    if is_exploratory:
        return "LinkedIn"

    # ==========================================
    # PRIORITY 3: HIGH-VALUE LEADS (Top Tier)
    # ==========================================
    # Very high engagement deserves a direct call
    if engagement_score >= 90:
        return "Call"
    
    # ==========================================
    # PRIORITY 4: STANDARD ENGAGEMENT
    # ==========================================
    # High engagement (80-89) → Email (personalized outreach)
    if engagement_score >= 80:
        return "Email"
    
    # Low engagement (<50) → LinkedIn (soft, non-intrusive approach)
    if engagement_score < 50:
        return "LinkedIn"
    
    # ==========================================
    # PRIORITY 5: ICP PRIORITY & BEHAVIOR
    # ==========================================
    # Medium engagement (50-79) → Check Priority
    if icp_priority == "low":
        return "LinkedIn"
    
    if icp_priority == "high" or "active" in business_behavior:
        return "Email"
    
    # Default fallback
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
        # 1. Check rules first for deterministic overrides (like Urgency)
        rule_channel = decide_channel_with_rules(classification, icp)
        
        # 2. If rules say "Call", it's likely due to Urgency or High Engagement - prioritize this
        if rule_channel == "Call":
            selected_channel = "Call"
        else:
            # 3. Otherwise, use LLM for decision for better variety
            selected_channel = decide_channel_with_llm(classification, icp)
            
            # Double check validity
            if selected_channel not in ["Email", "LinkedIn", "Call"]:
                selected_channel = rule_channel
            
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
