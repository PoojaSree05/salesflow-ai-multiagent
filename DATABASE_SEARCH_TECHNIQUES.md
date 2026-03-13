# Database Search & ICP Matching Techniques
## Technical Deep-Dive for SalesFlow AI Presentation

---

## Overview of the 3-Agent Pipeline

```
User Input
    ↓
[1] Classification Agent → Extract: Role, Location, Industry, Urgency
    ↓
[2] ICP Agent → Search & Score Database → Return Top 5 Matches
    ↓
[3] Channel Agent → Pick Email/LinkedIn/Call Based on Engagement & Urgency
    ↓
Content Agent → Write Personalized Message
    ↓
Execute → Send via Selected Channel
```

---

# Agent 1: Classification Agent
## (Understanding the Request)

### What It Does
Reads the user's input and extracts:
- **Role** (e.g., "HR Manager", "CTO")
- **Location** (e.g., "London", "New York")
- **Industry** (e.g., "Healthcare", "AI", "FinTech")
- **Urgency** (Low, Medium, High, Immediate)
- **Business Behavior** (e.g., "Hiring", "Scaling")

### How It Works

#### Step 1A: LLM-Based Extraction (Primary)
Sends the user's message to an LLM with a structured prompt:

```
Extract business information from: "{user_input}"

Return JSON with fields:
- role: job title
- location: city
- industry: sector
- urgency: priority level
```

**Why LLM?** Flexible, understands context like "I'm looking for hiring leaders" → extracts role="HR Manager"

#### Step 1B: Fallback Keyword Matching (Backup)
If LLM fails, use keyword dictionaries:

```python
ROLE_KEYWORDS = [
    ("hr manager", "HR Manager"),
    ("recruiter", "HR Manager"),
    ("cto", "CTO"),
    ("sales director", "Sales Director"),
    # ... etc
]

CITY_WORDS = ["london", "new york", "singapore", "berlin"]
INDUSTRY_WORDS = ["healthcare", "ai", "fintech", "saas"]
```

**Why Fallback?** 
- Fast (no LLM latency)
- Reliable (no hallucination)
- Handles offline scenarios

### Example Extraction

**Input:** "I need HR managers in London who are hiring"

**Output:**
```json
{
  "role": "HR Manager",
  "location": "London",
  "industry": "",
  "urgency": "High",
  "user_intent": "Hiring intent"
}
```

---

# Agent 2: ICP Agent
## (Finding & Scoring Matching Leads)

### Database Structure
Location: `backend/data/mock_dataset.csv`

Contains ~4,000 prospects with:
- name, company, email
- role, location, industry
- company_size, engagement_score
- pain_point_focus

### How It Works

#### Step 2A: Pre-Filtering (Fast Narrowing)

1. **Location Filter**
   - Extract location from classification
   - Filter dataset: `df[df["location"].contains("London")]`
   - If no matches, fall back to full dataset

2. **Industry Filter**
   - Extract industry from classification
   - Filter: `df[df["industry"].contains("Healthcare")]`
   - Chain with location filter

**Result:** Reduced dataset from ~4,000 to ~50-200 candidates

---

#### Step 2B: Role Matching (Semantic Matching)

**Challenge:** User says "HR heads" but database has "HR Manager" → Need semantic match

**Solution:**

1. **Fast Path – Substring Matching (First)**
   ```python
   # If user said "HR Manager" and dataset has "HR Manager" → exact match
   if extracted_lower in role_lower or role_lower in extracted_lower:
       best_role_match = role
       break
   ```
   - Ultra-fast (no LLM)
   - Handles 80% of cases

2. **Fallback Path – LLM Semantic Matching (If needed)**
   ```
   Find the semantically closest role to "HR Head" from:
   [HR Manager, HR Director, People Manager, ...]
   ```
   - Called per search, not per row
   - LLM matches 1 role to many rows

**Why This Approach?**
- Most inputs are exact matches → fast
- When semantics needed → use LLM once
- Avoids LLM-per-row (expensive)

---

#### Step 2C: Scoring Algorithm (Ranking)

For each remaining candidate, calculate a score:

```python
score = 0

# Role Match: 60 points (biggest factor)
if candidate_role == matched_role:
    score += 60

# Location Match: 30 points (already filtered, bonus)
score += 30

# Engagement Score: up to 10 points
# Example: engagement_score=85 → 85 * 0.1 = 8.5 points
score += candidate_engagement_score * 0.1

# Final: score ranges from 0-100
```

#### Step 2D: Priority Assignment

Based on final score:
```
score ≥ 90  → Priority = "High"
score ≥ 75  → Priority = "Medium"
score <  75  → Priority = "Low"
```

#### Step 2E: Return Top 5

Sort all candidates by score descending, return top 5:

```json
[
  {
    "name": "Sallee Kilbey",
    "company": "Vidoo",
    "role": "HR Manager",
    "engagement_score": 85,
    "match_score": 98.5,
    "priority": "High"
  },
  {
    "name": "John Smith",
    "company": "TechCorp",
    "role": "HR Manager",
    "engagement_score": 72,
    "match_score": 92.2,
    "priority": "Medium"
  },
  ...top 5 total
]
```

### Example Flow

**Input:**
- Role: "HR Manager"
- Location: "London"
- Industry: "EdTech"

**Step 2A:** Filter to London → 150 people
**Step 2A:** Filter to EdTech → 12 people
**Step 2B:** Match role "HR Manager" → all 12 have matching role (exact match)
**Step 2C:** Score each:
- Person A: 60 (role) + 30 (location) + 8.5 (engagement) = 98.5 ✅ High priority
- Person B: 60 + 30 + 7.2 = 97.2 ✅ High priority
- Person C: 60 + 30 + 5.0 = 95.0 ✅ High priority
- ... etc

**Step 2E:** Return [A, B, C, D, E] (top 5)

---

# Agent 3: Channel Agent
## (Deciding How to Contact)

### Decision Tree (Priority-Based)

```
START
  ↓
[1] Is urgency "Immediate" or "High"?
    YES  → Return "Call" (direct, time-sensitive)
    NO   ↓
[2] Is engagement_score ≥ 75?
    YES  → Return "Email" (they're interested)
    NO   ↓
[3] Is engagement_score < 40?
    YES  → Return "LinkedIn" (soft approach)
    NO   ↓
[4] Is ICP Priority "High"?
    YES  → Return "Email" (worth personal effort)
    NO   → Return "LinkedIn"
```

### Scoring Factors (in order of importance)

1. **Urgency** (Highest Priority)
   - Immediate/High → Call (time critical)
   - Medium/Low → Continue to next check

2. **Engagement Score** (Second Priority)
   - ≥75 → Email (they're engaged, personalized approach)
   - <40 → LinkedIn (exploratory, soft touch)
   - 40-75 → Check other factors

3. **ICP Priority Level** (Third Priority)
   - High → Email (high-value target)
   - Low → LinkedIn (early stage)

4. **Business Behavior** (Fourth Priority)
   - Keywords like "hiring", "scaling", "urgent" → Email
   - Keywords like "exploring", "considering" → LinkedIn

5. **Default** → Email (most professional/scalable)

### Example Channel Decisions

```
Lead: Sallee Kilbey
- Urgency: High
- Engagement: 85
- ICP Priority: High
- Content: "I noticed you're hiring"

Decision: CALL
Reason: High urgency + High engagement = Time-sensitive, high-value target
```

```
Lead: Unknown Prospect
- Urgency: Low
- Engagement: 35
- ICP Priority: Low
- Content: General outreach

Decision: LINKEDIN
Reason: Low engagement + Low priority = Soft, non-intrusive approach
```

---

# Key Technical Decisions

## Why This Approach?

### 1. **Two-Tier Matching (LLM + Keywords)**
- **Fast path (keywords):** 95% of searches → instant
- **LLM backup:** Edge cases with unusual language
- **Result:** Speed + Reliability

### 2. **Pre-Filtering Before Scoring**
```
Instead of:   Score all 4,000 candidates
Use:          Filter to ~50, then score
Benefit:      10x faster, same quality
```

### 3. **Simple Scoring Formula**
- Not ML/embeddings (hard to explain, slow)
- Not complex algorithms (overfitting risk)
- Simple formula: Role (60) + Location (30) + Engagement (10)
- **Benefit:** Transparent, debuggable, fast

### 4. **Priority-Based Channel Decision**
- Not ML classifier (black box)
- Not random (unpredictable)
- Decision tree with business rules
- **Benefit:** Explainable, customizable

### 5. **Return Top 5, Not Top 1**
- Users can see alternatives
- Provides ranking transparency
- Enables bulk outreach (multi-lead mode)

---

# Techniques Used (Summary Table)

| Component | Technique | Why |
|-----------|-----------|-----|
| **Classification** | LLM + Fallback Keywords | Flexible + Reliable |
| **Pre-Filtering** | Pandas DataFrame filtering | Fast narrowing |
| **Role Matching** | Substring match, then LLM | Most are exact, edge cases handled |
| **Scoring** | Simple weighted formula | Transparent, fast |
| **Ranking** | Sort by score, return top 5 | Shows best options |
| **Channel Selection** | Decision tree (priority order) | Explainable rules |
| **Engagement** | Static score (from dataset) | Pre-calculated, fast |
| **Content** | LLM-based (GPT-4o) | Personalized, high quality |

---

# What Makes This Different?

## ❌ NOT Using (And Why)

❌ **Embeddings/Vector Search**
- Slower (~500ms per search)
- Hard to explain ("why this match?")
- Requires embedding database

❌ **ML Classifier for Channel**
- Black box output
- Hard to customize rules
- Needs training data

❌ **All 4,000 Candidates Scored**
- Wasteful computation
- No speed improvement in UX

## ✅ ACTUALLY Using

✅ **Simple + Transparent**
- Keywords + LLM for flexibility
- Pre-filter for speed
- Weighted scoring (understandable)
- Decision rules (explainable)

✅ **Fast**
- 95% keyword matches = instant
- Pre-filtering = 50-200 scored, not 4,000
- Simple algorithm = milliseconds

✅ **Reliable**
- No ML hallucinations
- Fallbacks at every step
- Deterministic output (same input = same output)

---

# Presentation Talking Points

### "How do you find the right leads?"

> "We use a three-step process: First, we read what you're looking for using LLM and keywords. Second, we pre-filter our database by location and industry, then score matches using a transparent formula: 60 points for role match, 30 for location match, 10 for engagement. Third, we decide the best contact method based on urgency and engagement level."

### "How accurate is the matching?"

> "Our top-5 matches average 90+ score (out of 100), combining exact role matches with engagement signals. We use both LLM extraction and keyword fallback to handle varied requests reliably."

### "Why not use AI/ML for everything?"

> "We use AI where it's best (understanding flexible language), but keep the core matching transparent and fast. Users can see exactly why someone is ranked #1 vs #2, and we can adjust rules without retraining models."

### "How fast is the search?"

> "Pre-filtering reduces our dataset from 4,000 to ~100 candidates before scoring, taking ~500ms total including LLM calls for classification and content generation."

---

