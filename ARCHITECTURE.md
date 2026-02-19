# Multi-Agent Intelligent Content Generation and Decision System

## Assessment Task 2 – System Architecture

### Workflow Summary

```
User Input → A1 Classification → A2 ICP → A3 Platform Decision → A4 Content Generation → Output Channel
```

---

## Agent Overview

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| **A1 Classification** | Classify user data by context and behavior | User input | Time, Location, Business behavior, User intent |
| **A2 ICP Module** | Identify target audience from classified data | A1 output | Priority-based ICP (demographic + behavioral attributes) |
| **A3 Platform Decision** | Select communication channel | A1 + A2 output | LinkedIn, Email, or Call |
| **A4 Content Generation** | Generate platform-optimized content | A1 + A2 + channel | Structured content for selected channel |

---

## Agent Details

### Agent 1 – Classification Agent (A1)
- **Input:** User-provided business description
- **Parameters:** Time, Location, Business behavior, User intent
- **Output:** Structured classification passed to ICP module

### Agent 2 – ICP Module (Ideal Customer Profile)
- **Input:** Classified data from A1
- **Functions:** Analyze category, match ICP datasets, enrich profiles
- **Output:** Priority-ranked ICP (most likely to buy)

### Agent 3 – Platform Decision Agent
- **Input:** Classification, ICP, urgency, engagement
- **Decision Factors:** Task urgency, ICP preferences, business objectives, engagement data
- **Output Channels:** LinkedIn (A4), Email (A5), Call (A6)

### Agent 4 – Content Generation Agent
- **Input:** Classification (A1), ICP (A2), selected channel (A3), engagement strategy
- **Processing:** Prompt engineering, context-aware generation, tone adaptation
- **Output:** Platform-specific content (LinkedIn, Email, or Call format)

---

## Output Channel Modules

### LinkedIn Module (A4)
- Professional, conversational tone
- Engagement-focused messaging
- Networking-optimized CTA

### Email Module (A5)
- Structured subject line and body
- Personalization tokens
- Follow-up and sequencing support

### Call Module (A6)
- Call script generation
- Objection handling recommendations
- Lead qualification checklist

---

## Data Security & AI Governance

- Role-based access control (RBAC)
- Encrypted data storage
- Prompt logging and audit trails
- Compliance with data protection policies

---

## File Structure

```
backend/
├── main.py                 # Flask API, transform, fallback
├── graph/workflow.py       # LangGraph: A1 → A2 → A3 → A4
└── agents/
    ├── classification_agent.py  # A1
    ├── icp_agent.py            # A2
    ├── platform_agent.py       # A3
    ├── content_agent.py        # A4 (LinkedIn, Email, Call)
    └── ...
```
