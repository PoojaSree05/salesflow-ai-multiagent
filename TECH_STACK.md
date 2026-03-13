# SalesFlow AI - Tech Stack

## Overview

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React + TypeScript | User interface |
| **Backend** | Python + Flask | API & business logic |
| **Orchestration** | LangGraph | Multi-agent workflow |
| **LLM** | OpenAI GPT-4o | Classification, content generation |
| **Database** | Pandas + CSV | Lead data storage |
| **Email** | Gmail SMTP | Outreach delivery |
| **Styling** | Tailwind CSS | UI design |
| **Build Tool** | Vite | Frontend bundling |
| **Package Manager** | npm (frontend), pip (backend) | Dependency management |

---

## Frontend Stack

### Core
- **React 18** – UI framework
- **TypeScript** – Type safety
- **Vite** – Lightning-fast bundler
- **React Router** – Page navigation

### Styling
- **Tailwind CSS** – Utility-first CSS framework
- **PostCSS** – CSS transformation
- **Lucide Icons** – SVG icon library

### UI Components
- **Shadcn/ui** – Pre-built accessible components (accordion, alert, button, card, dialog, form, modal, etc.)
- **Sonner** – Toast notifications
- **Recharts** – Analytics charts

### Development
- **ESLint** – Code quality
- **Vitest** – Unit testing
- **Bun** – Fast JavaScript runtime (package manager)

### File Structure
```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── dashboard/    # Dashboard cards (agents, execution)
│   │   ├── layout/       # Sidebar, layout structure
│   │   └── ui/           # Shadcn/ui components
│   ├── pages/            # Full pages (Dashboard, Campaigns, Leads, Analytics, Settings)
│   ├── hooks/            # Custom React hooks (useTheme, useToast, useMobile)
│   ├── lib/              # Utilities (API calls, helpers)
│   ├── types/            # TypeScript types
│   └── main.tsx          # Entry point
├── package.json          # Dependencies
├── vite.config.ts        # Vite configuration
├── tailwind.config.ts    # Tailwind configuration
└── tsconfig.json         # TypeScript configuration
```

---

## Backend Stack

### Core Framework
- **Flask** – Lightweight Python web framework
- **Flask-CORS** – Cross-origin request handling
- **Python 3.13** – Runtime environment

### AI & Agents
- **LangGraph** – Multi-agent orchestration framework
- **OpenAI API** – LLM integration (GPT-4o)
  - Classification (extract role, location, urgency)
  - Content generation (email, LinkedIn, call scripts)

### Data Processing
- **Pandas** – DataFrames for lead database
- **CSV** – Data storage format

### Email Integration
- **smtplib** – Python SMTP client
- **Gmail SMTP** – Email delivery service
- **MIMEText/MIMEMultipart** – Email message formatting

### Routing & APIs
- **@flask_app.route** – API endpoint definitions
- **Request/Response** – JSON handling

### File Structure
```
backend/
├── main.py                    # Flask app, endpoints, email logic
├── llm.py                     # LLM API calls (GPT-4o wrapper)
├── utils.py                   # Helper functions
├── requirements.txt           # Python dependencies
├── .env                       # Configuration (SMTP, API keys)
├── agents/
│   ├── classification_agent.py   # Extract: role, location, industry, urgency
│   ├── icp_agent.py             # Find & score matching leads
│   ├── platform_agent.py        # Decide: Email/LinkedIn/Call
│   ├── content_agent.py         # Generate personalized content
│   ├── email_agent.py           # Email formatting
│   ├── linkedin_agent.py        # LinkedIn message formatting
│   ├── call_agent.py            # Call script generation
│   └── __init__.py
├── graph/
│   ├── workflow.py         # LangGraph orchestration (connects agents)
│   └── __init__.py
└── data/
    └── mock_dataset.csv    # ~4,000 prospect records
```

---

## Key Libraries & Versions

### Frontend (package.json)
```json
{
  "react": "^18.x",
  "typescript": "^5.x",
  "vite": "^5.x",
  "tailwindcss": "^3.x",
  "lucide-react": "latest",
  "recharts": "^2.x",
  "sonner": "^1.x"
}
```

### Backend (requirements.txt)
```
flask==2.3.x
flask-cors==4.0.x
pandas==2.x
python-dotenv==1.0.x
requests==2.31.x
openai==1.x
langgraph==0.x
langchain==0.x
```

---

## API Architecture

### Endpoints

```
POST /run-strategy
├── Input: { input, campaignMode: "single" | "multi" }
├── Process: Classification → ICP Ranking → Channel Selection → Content Generation
└── Output: StrategyResult (classification, icp, channel, execution)

POST /send-email
├── Input: { to, subject, body }
├── Process: SMTP via Gmail (with BCC to monitoring address)
└── Output: { success: true/false }

GET /campaigns
├── Process: Return all campaign history
└── Output: Array<StrategyResult>

GET /health
└── Output: { status: "ok" }
```

---

## Data Flow

```
User Input
   ↓
[Frontend] React Form → API Call to /run-strategy
   ↓
[Backend] Flask Router
   ↓
[LangGraph] Multi-Agent Workflow
   ├── Step 1: Classification Agent (LLM)
   │   └── Output: role, location, industry, urgency
   ├── Step 2: ICP Agent (Pandas + CSV Search)
   │   └── Output: Top 5 matching leads with scores
   ├── Step 3: Platform Agent (Decision Rules)
   │   └── Output: Selected channel (Email/LinkedIn/Call)
   └── Step 4: Content Agent (LLM)
       └── Output: Personalized message
   ↓
[Backend] Transform to frontend format
   ↓
JSON Response to Frontend
   ↓
[Frontend] Display in Dashboard
   └── User can edit and send via /send-email
```

---

## Database (Mock Data)

### Format
- **File:** `backend/data/mock_dataset.csv`
- **Size:** ~4,000 prospects
- **Columns:**
  - name, company, email
  - role, location, industry
  - company_size, engagement_score
  - pain_point_focus, business_behavior

### Query Logic
```
1. Extract classification from user input (LLM)
2. Filter by location (Pandas)
3. Filter by industry (Pandas)
4. Match role (substring or LLM semantic match)
5. Score by: role_match(60) + location(30) + engagement(10)
6. Sort by score, return top 5
```

---

## External Services

### OpenAI API
- **Model:** GPT-4o
- **Usage:**
  - Classification (extract intent from user input)
  - Content generation (write emails, LinkedIn messages, call scripts)
- **Cost:** Per-token pricing (~$0.003-0.015 per 1K tokens)

### Gmail SMTP
- **Service:** Gmail App Password
- **Usage:** Send real emails with BCC to monitoring address
- **Config:** Stored in `.env` file (SMTP_PASSWORD, SMTP_USERNAME)

---

## Deployment Ready

### Frontend Build
```bash
npm run build
# Output: dist/ directory (static files)
# Hosting: Vercel, Netlify, or any static server
```

### Backend Deployment
```bash
pip install -r requirements.txt
python main.py
# Runs on localhost:8000 (or cloud platform port)
# Consider: Docker, Heroku, AWS Lambda, or bare VM
```

### Environment Variables Required
```
# Backend (.env)
OPENAI_API_KEY=sk-...
SMTP_PASSWORD=xxxx-xxxx-xxxx
SMTP_USERNAME=email@gmail.com
DEFAULT_TO_EMAIL=monitoring@company.com
ENABLE_REAL_EMAIL=true
```

---

## Why These Choices?

| Choice | Reason |
|--------|--------|
| **React + TypeScript** | Type-safe, fast, large ecosystem |
| **Tailwind** | Rapid UI development, consistent design |
| **Flask** | Lightweight, fast to build, Python-friendly |
| **LangGraph** | Orchestrates multi-agent workflows elegantly |
| **GPT-4o** | State-of-art LLM, best classification & content |
| **Pandas + CSV** | Simple, no DB setup needed, easy to scale later |
| **Gmail SMTP** | Free, reliable, easy to configure |
| **Vite** | 10x faster builds than Webpack |

---

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| **User Input → Response** | ~2-3 seconds | Includes LLM calls (classification + content) |
| **Database Search** | ~500ms | Pre-filter 4,000 → 100, then score |
| **LLM Classification** | ~1 second | Single LLM call |
| **Content Generation** | ~1 second | Per-ICP LLM call |
| **Email Send** | ~500ms | Gmail SMTP |

---

## Scalability Roadmap

As you grow, consider:

| Component | Current | Next Step |
|-----------|---------|-----------|
| **Database** | CSV (4K records) | PostgreSQL (100K+ records) |
| **LLM** | GPT-4o (expensive at scale) | Mixtral or Llama 2 (self-hosted) |
| **Caching** | In-memory | Redis (for frequently matched roles) |
| **Storage** | Local files | S3 (for campaign history) |
| **Frontend Hosting** | Local dev | Vercel/Netlify CI/CD |
| **Backend Hosting** | Local Flask | Docker + Kubernetes or Lambda |

---

## Open Source & Dependencies

| Library | License | Why Used |
|---------|---------|----------|
| React | MIT | Core framework |
| Tailwind CSS | MIT | Styling |
| LangGraph | MIT | Agent orchestration |
| Pandas | BSD | Data processing |
| Flask | BSD | Web framework |
| OpenAI | Proprietary | LLM access |

---

## Security Considerations

✅ **What's Secured**
- SMTP credentials in `.env` (not in code)
- Email BCC for audit trail
- CORS enabled (Flask-CORS)

⚠️ **What Needs Hardening (for production)**
- API authentication (currently open)
- Rate limiting (prevent spam)
- HTTPS enforcement
- Input validation
- Secret management (vault, not .env)

---

## Presentation Summary

**"Our entire stack is modern, lightweight, and purpose-built for AI agents:"**

- **Frontend:** React + TypeScript with Vite (fast builds, type-safe)
- **Backend:** Python Flask (simple, powerful)
- **Orchestration:** LangGraph (multi-agent workflows)
- **AI:** OpenAI GPT-4o (best-in-class LLM)
- **Data:** Pandas + CSV (scalable later)
- **Messaging:** Gmail SMTP (reliable)
- **UI:** Tailwind CSS + Shadcn (beautiful, accessible)

**Total startup time:** ~5 minutes to run locally, ~30 seconds to deploy frontend.

