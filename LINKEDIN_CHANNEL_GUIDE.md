# LinkedIn Channel Selection Criteria
## Data Schema & Characteristics for Dataset Extension

---

## Quick Answer: When to Use LinkedIn

LinkedIn is selected when:
1. **Engagement Score < 40** (low interest signals) 
2. **Priority Level = "Low"** (weak match to your criteria)
3. **Business Behavior = "Exploratory"** (researching, not urgent)
4. **Urgency = "Low" or "Medium"** (not time-critical)
5. **Company Size = "Large Enterprise"** (harder to reach decision makers directly)

---

## Channel Selection Decision Tree

```
START
  ↓
Is Urgency High/Immediate?
  YES → CALL (direct, time-sensitive)
  NO ↓
Is Engagement ≥ 75?
  YES → EMAIL (strong interest)
  NO ↓
Is Engagement < 40?
  YES → LINKEDIN ✅ (low interest, soft approach)
  NO ↓
Is Priority Level = "High"?
  YES → EMAIL (worth personalized effort)
  NO ↓
Is Business Behavior = "Active/Hiring"?
  YES → EMAIL
  NO → LINKEDIN ✅ (exploratory, soft)
```

---

## Data Points to Add to Your CSV

### Current Schema
```csv
name,company,email,role,location,industry,engagement_score,pain_point_focus
```

### Extended Schema (Recommended for Better Channel Selection)

Add these columns to make LinkedIn selection smarter:

```csv
name,company,email,role,location,industry,company_size,engagement_score,
reachability,decision_maker,business_behavior,hiring_status,growth_stage,
linkedin_url,contact_quality
```

---

## LinkedIn-Suitable Prospect Profiles

### Profile 1: Early-Stage Curious Prospect
```csv
Name: Michael Chen
Company: StartupXYZ
Email: m.chen@startupxyz.com
Role: Product Manager
Location: San Francisco
Industry: AI
Company Size: 10-50
Engagement Score: 35          ← LOW (< 40)
Reachability: MEDIUM          ← Not easy to reach
Decision Maker: NO            ← Influencer only
Business Behavior: Exploring  ← Early interest
Hiring Status: Not Hiring
Growth Stage: Series A
LinkedIn URL: https://linkedin.com/in/michaelchen
Contact Quality: Warm lead
```

**Why LinkedIn?**
- Engagement = 35 (< 40) → Low interest signal
- Not a decision maker → LinkedIn is non-threatening
- Exploring solutions → LinkedIn message shows you're open
- Email might be ignored, LinkedIn = softer touchpoint

---

### Profile 2: Large Enterprise Prospect (Gatekeeper)
```csv
Name: Sarah Johnson
Company: Acme Corp
Email: sarah.johnson@acme-corp.com
Role: Sales Manager (Team Lead - not VP)
Location: London
Industry: FinTech
Company Size: 5000+         ← LARGE (harder to reach)
Engagement Score: 50         ← MEDIUM (not high)
Reachability: HARD           ← Gatekeepers screen emails
Decision Maker: NO           ← Reports to VP
Business Behavior: Active
Hiring Status: Yes
Growth Stage: Mature
LinkedIn URL: https://linkedin.com/in/sarahjohnson
Contact Quality: Cold lead
```

**Why LinkedIn?**
- Large company → gatekeepers block emails
- Reachability = HARD → LinkedIn is direct approach
- Not decision maker → Email to them gets filtered
- LinkedIn DM bypasses email filters

---

### Profile 3: Passive Prospect (Not Actively Hiring)
```csv
Name: David Kumar
Company: TechGlobal
Email: d.kumar@techglobal.com
Role: HR Director
Location: Singapore
Industry: SaaS
Company Size: 500-1000
Engagement Score: 38         ← LOW (< 40)
Reachability: MEDIUM
Decision Maker: YES
Business Behavior: Passive   ← Not actively looking
Hiring Status: Maybe (Future)
Growth Stage: Growth
LinkedIn URL: https://linkedin.com/in/davidkumar
Contact Quality: Prospect
```

**Why LinkedIn?**
- Engagement = 38 (< 40) → Not actively looking
- Email might go to spam folder
- LinkedIn message = "just checking in" (non-pushy)
- Can nurture relationship first

---

### Profile 4: Influencer / Advisor (Not Decision Maker)
```csv
Name: Emma Wilson
Company: VentureLab
Email: emma@venturelab.com
Role: Operations Consultant
Location: Berlin
Industry: EdTech
Company Size: 100+
Engagement Score: 42        ← BORDERLINE LOW
Reachability: MEDIUM
Decision Maker: NO          ← Advisor/Influencer
Business Behavior: Network Building
Hiring Status: N/A
Growth Stage: N/A
LinkedIn URL: https://linkedin.com/in/emmawilson
Contact Quality: Influencer
```

**Why LinkedIn?**
- Not a decision maker → Email = waste
- Influencer → LinkedIn = native platform
- Engagement = 42 → LinkedIn nurture first
- Goal: build relationship, ask for intro later

---

## CSV Column Definitions (For Extension)

### New Columns to Add

#### 1. `company_size`
**Values:** "1-10", "10-50", "50-200", "200-1000", "1000-5000", "5000+"

**LinkedIn Trigger:**
```
company_size in ["5000+", "1000-5000"]
OR (company_size >= "200" AND decision_maker == "NO")
→ Use LinkedIn (hard to reach directly)
```

**Why:** Large companies have gatekeepers; LinkedIn DMs bypass email filters

---

#### 2. `reachability`
**Values:** "EASY", "MEDIUM", "HARD"

**LinkedIn Trigger:**
```
reachability == "HARD"
→ Use LinkedIn (direct message approach)
```

**How to Score:**
- EASY: direct email available, no gatekeeper
- MEDIUM: email exists but sometimes screened
- HARD: only LinkedIn visible, email is corporate (likely filtered)

**Examples:**
- `reachability=EASY`: startup founder (email: founder@startup.com)
- `reachability=MEDIUM`: HR manager (email: hr.manager@company.com)
- `reachability=HARD`: VP at Fortune 500 (no public email, only LinkedIn visible)

---

#### 3. `decision_maker`
**Values:** "YES", "NO"

**LinkedIn Trigger:**
```
decision_maker == "NO"
→ Use LinkedIn (influencer/connector approach)
```

**Why:** 
- If they can't decide, don't waste email personalization
- LinkedIn allows "soft" inquiry without commitment
- Gives them time to influence decision maker

**Examples:**
- YES: CEO, VP, Director-level roles
- NO: Manager, Lead, Specialist, Consultant roles

---

#### 4. `business_behavior`
**Values:** "Hiring", "Scaling", "Active", "Exploring", "Research Mode", "Passive", "Window Shopping"

**LinkedIn Triggers:**
```
business_behavior in ["Exploring", "Research Mode", "Passive", "Window Shopping"]
→ Use LinkedIn

business_behavior in ["Hiring", "Scaling", "Active"]
→ Use EMAIL
```

**Why:**
- Active searchers: email = professional, direct
- Passive explorers: LinkedIn = serendipity, non-threatening
- Research mode: LinkedIn = education-first approach

**Examples:**
```csv
business_behavior: "Hiring" → EMAIL (they need solutions now)
business_behavior: "Exploring" → LINKEDIN (just browsing options)
business_behavior: "Passive" → LINKEDIN (not looking, so soft touch)
```

---

#### 5. `hiring_status`
**Values:** "Yes", "No", "Maybe", "Unknown"

**LinkedIn Trigger (Combined with other factors):**
```
hiring_status == "No" AND engagement_score < 50
→ Use LinkedIn (they're not active, keep it light)

hiring_status == "Yes" AND engagement_score >= 75
→ Use EMAIL (they're ready to hear from you)
```

**Why:** 
- If not hiring + low engagement = LinkedIn (future nurture)
- If hiring + high engagement = Email (time-sensitive demand)

---

#### 6. `growth_stage`
**Values:** "Seed", "Series A", "Series B", "Growth", "Mature", "Enterprise"

**LinkedIn Trigger:**
```
growth_stage == "Seed" 
AND engagement_score < 50
→ Use LinkedIn (bootstrap founders, limited budget for outreach)

growth_stage == "Mature" 
AND company_size >= "1000"
→ Use LinkedIn (traditional, formal comms preferred)
```

**Why:**
- Early-stage: founder might prefer LinkedIn over email
- Mature: formal structures, LinkedIn = professional network approach

---

#### 7. `contact_quality`
**Values:** "Warm", "Prospect", "Cold", "Stale"

**LinkedIn Trigger:**
```
contact_quality == "Cold"
→ Use LinkedIn (cold email = spam folder, LinkedIn = direct)

contact_quality == "Warm"
→ Use EMAIL (relationship exists)
```

**Why:**
- Warm = existing relationship → email is personal
- Cold = unknown → LinkedIn = safer exploration
- Stale = old contact → LinkedIn = "reconnect" message

---

#### 8. `reachability_notes` (Optional)
**Type:** Text field

**Examples:**
```
"Corporate email likely screened, LinkedIn DM worked before"
"Direct email not published, LinkedIn messaging only option"
"Manager-level prospect, email might go to assistant"
"Influencer, not decision maker, use for introductions"
```

---

## Sample Extended CSV (10 Rows)

```csv
name,company,email,role,location,industry,company_size,engagement_score,decision_maker,business_behavior,hiring_status,contact_quality,reachability,estimated_channel
Michael Chen,StartupXYZ,m.chen@startup.com,Product Manager,San Francisco,AI,10-50,35,NO,Exploring,Maybe,Prospect,MEDIUM,LinkedIn
Sarah Johnson,Acme Corp,sarah.johnson@acme.com,Sales Manager,London,FinTech,5000+,50,NO,Active,Yes,Cold,HARD,LinkedIn
David Kumar,TechGlobal,d.kumar@tech.com,HR Director,Singapore,SaaS,500-1000,38,YES,Passive,Maybe,Prospect,MEDIUM,LinkedIn
Emma Wilson,VentureLab,emma@venture.com,Ops Consultant,Berlin,EdTech,100+,42,NO,Active,N/A,Influencer,MEDIUM,LinkedIn
John Smith,TechCorp,john@techcorp.com,CTO,New York,Cloud,200-500,82,YES,Hiring,Yes,Warm,EASY,Email
Lisa Park,DataInc,lisa.park@datainc.com,VP Analytics,Boston,AI,1000-5000,28,YES,Passive,No,Cold,HARD,LinkedIn
Robert Brown,FinServe,r.brown@finserve.com,Head of HR,Chicago,Banking,5000+,45,YES,Active,Yes,Prospect,HARD,LinkedIn
Amy Zhang,GrowthCo,amy@growth.co,Founder,Austin,SaaS,1-10,88,YES,Scaling,Yes,Warm,EASY,Email
Mark Davis,EnterpriseX,m.davis@enterprise.com,Director Sales,Los Angeles,Enterprise,5000+,35,NO,Research,No,Cold,HARD,LinkedIn
Patricia Lee,HealthTech,p.lee@health.com,Chief Medical Officer,Boston,Healthcare,50-200,75,YES,Hiring,Yes,Prospect,MEDIUM,Email
```

---

## Channel Selection Logic (Updated Code)

```python
def decide_channel_with_rules(classification, icp):
    """
    Enhanced channel selection using extended dataset fields
    """
    urgency = str(classification.get("urgency") or "").lower()
    engagement_score = int(icp.get("engagement_score", 50))
    company_size = str(icp.get("company_size", "")).lower()
    decision_maker = str(icp.get("decision_maker", "YES")).lower()
    reachability = str(icp.get("reachability", "MEDIUM")).lower()
    business_behavior = str(icp.get("business_behavior", "")).lower()
    contact_quality = str(icp.get("contact_quality", "")).lower()
    
    # PRIORITY 1: Urgency
    if urgency in ["immediate", "high"]:
        return "Call"
    
    # PRIORITY 2: High Engagement
    if engagement_score >= 75:
        return "Email"
    
    # PRIORITY 3: LinkedIn Indicators
    if engagement_score < 40:
        return "LinkedIn"  ← Low engagement
    
    if reachability == "hard":
        return "LinkedIn"  ← Hard to reach
    
    if decision_maker == "no":
        return "LinkedIn"  ← Influencer, not decision maker
    
    if business_behavior in ["exploring", "passive", "research mode"]:
        return "LinkedIn"  ← Early-stage interest
    
    if contact_quality == "cold":
        return "LinkedIn"  ← Cold outreach
    
    # PRIORITY 4: Medium-tier
    if engagement_score >= 50:
        return "Email"
    
    # DEFAULT
    return "LinkedIn"  ← Fallback to safer approach
```

---

## Dataset Extension Checklist

### Phase 1: Add Must-Have Fields (Minimal)
- [ ] `company_size`
- [ ] `engagement_score` (already have)
- [ ] `decision_maker`
- [ ] `business_behavior`

### Phase 2: Add Nice-to-Have Fields (Enhanced)
- [ ] `reachability`
- [ ] `hiring_status`
- [ ] `contact_quality`
- [ ] `growth_stage`

### Phase 3: Add Optional Fields (Advanced)
- [ ] `reachability_notes`
- [ ] `linkedin_url`
- [ ] `preferred_channel` (for manual override)

---

## Sample Data Values by Channel

### LinkedIn-Optimal Prospects
```
┌─────────────────────────────────────────────────────┐
│ LINKEDIN CHANNEL PROFILE                            │
├─────────────────────────────────────────────────────┤
│ Engagement Score:      20-50 (LOW)                  │
│ Company Size:          5000+ or 1-50                │
│ Decision Maker:        NO                            │
│ Reachability:          HARD or MEDIUM               │
│ Business Behavior:     Exploring, Passive, Research │
│ Contact Quality:       COLD                          │
│ Hiring Status:         NO or MAYBE                   │
│ Growth Stage:          Seed or Mature/Enterprise    │
│                                                     │
│ Profile: Early-stage curious or large-company      │
│ gatekeeper who's not actively searching             │
└─────────────────────────────────────────────────────┘
```

### Email-Optimal Prospects
```
┌─────────────────────────────────────────────────────┐
│ EMAIL CHANNEL PROFILE                               │
├─────────────────────────────────────────────────────┤
│ Engagement Score:      70+ (HIGH)                    │
│ Company Size:          50-1000                       │
│ Decision Maker:        YES                           │
│ Reachability:          EASY                          │
│ Business Behavior:     Hiring, Scaling, Active      │
│ Contact Quality:       WARM or PROSPECT             │
│ Hiring Status:         YES                           │
│ Growth Stage:          Growth, Series B+            │
│                                                     │
│ Profile: Active decision maker actively hiring     │
└─────────────────────────────────────────────────────┘
```

### Call-Optimal Prospects
```
┌─────────────────────────────────────────────────────┐
│ CALL CHANNEL PROFILE                                │
├─────────────────────────────────────────────────────┤
│ Engagement Score:      50+ (MEDIUM+)                 │
│ Company Size:          50-500                        │
│ Decision Maker:        YES                           │
│ Reachability:          EASY or MEDIUM               │
│ Business Behavior:     Hiring, Urgent, Scaling     │
│ Contact Quality:       WARM                          │
│ Hiring Status:         YES                           │
│ Growth Stage:          Series A-B                    │
│ URGENCY:               High or Immediate            │
│                                                     │
│ Profile: Active decision maker, time-sensitive    │
└─────────────────────────────────────────────────────┘
```

---

## Migration Script (Add to Existing CSV)

If you have existing data, add these columns:

```python
import pandas as pd

df = pd.read_csv("mock_dataset.csv")

# Add new columns with sensible defaults
df["company_size"] = df["company_size"].fillna("200-1000")
df["decision_maker"] = df["role"].apply(
    lambda r: "YES" if any(x in str(r).lower() for x in ["ceo", "cto", "vp", "director", "head"])
    else "NO"
)
df["reachability"] = "MEDIUM"  # Default
df["business_behavior"] = "Active"  # Default
df["hiring_status"] = "Yes"  # Default
df["contact_quality"] = "Prospect"  # Default
df["growth_stage"] = "Growth"  # Default

df.to_csv("mock_dataset_extended.csv", index=False)
```

---

## Quick Reference: LinkedIn Signals

| Signal | Value | Channel |
|--------|-------|---------|
| Engagement | < 40 | **LinkedIn** |
| Decision Maker | NO | **LinkedIn** |
| Reachability | HARD | **LinkedIn** |
| Business Behavior | Exploring/Passive/Research | **LinkedIn** |
| Company Size | 5000+ | **LinkedIn** |
| Hiring Status | NO or MAYBE | **LinkedIn** |
| Contact Quality | COLD | **LinkedIn** |
| | | |
| Engagement | ≥ 75 | **Email** |
| Decision Maker | YES | **Email** |
| Business Behavior | Hiring/Scaling | **Email** |
| Contact Quality | WARM/PROSPECT | **Email** |
| Urgency | HIGH/IMMEDIATE | **Call** |

---

## Presentation Script

**"How do you decide when to use LinkedIn?"**

> "When someone scores low on engagement (under 40), isn't making the decision themselves, or is in a large company where emails get screened, we switch to LinkedIn. It's a softer approach—like a professional network touch rather than a direct sales pitch. We also use LinkedIn for people who are passively exploring rather than actively hiring. It's lower-pressure and works better as a first touch in those scenarios."

