# How SalesFlow AI Classifies Leads & Selects Channels

## Simple Explanation (No Jargon)

### What We Do
When you type in a message (like "I'm looking for HR managers in London"), our system:
1. **Reads** what you wrote
2. **Understands** what you're looking for
3. **Finds** matching people in our database
4. **Picks** the best way to reach them (email, call, or LinkedIn)
5. **Writes** a personalized message for each person

---

## The 4 Steps Broken Down

### Step 1: Understanding Your Request (Classification)
**What happens:** We read your message and figure out:
- **Who** are you trying to reach? (e.g., HR managers, CTOs, product managers)
- **Where** are they located? (e.g., London, New York, Singapore)
- **How urgent** is this? (low, medium, or high priority)
- **What do** they care about? (e.g., hiring, scaling, research)

**How:** We use patterns in your words. If you say "hiring" or "recruitment," we know you want HR people. If you mention "scaling AI," we know it's technical folks.

**Example:** 
- You say: "I need to reach HR managers in London who are hiring"
- We understand: Role=HR Manager, Location=London, Urgency=High, Goal=Hiring

---

### Step 2: Finding Matching People (ICP Ranking)
**What happens:** We search our database for people that match what you're looking for.

**How:** We have a list of ~4000 people with:
- Their name, company, email
- Their job title and location
- How engaged they likely are (based on their industry and company)

We score each person based on how well they match your request.

**Example:**
- We find "Sallee Kilbey" at Vidoo (EdTech company in London) → HR Manager → Score: 98/100 ✅ Perfect match!
- We find "John Smith" at a Manufacturing company → Wrong industry → Score: 45/100 ❌ Skip

---

### Step 3: Picking the Best Way to Contact (Channel Selection)
**What happens:** Based on who the person is and how engaged they are, we decide:
- **Email** → For people we know are very engaged (like to read messages)
- **LinkedIn** → For hard-to-reach people (safer way to connect first)
- **Call** → For VIPs or very urgent situations (direct & personal)

**How:** Rules like:
- High engagement score + email address available = Send email
- Low engagement or no email = Try LinkedIn first
- VIP/CEO + urgent = Call script instead

**Example:**
- Sallee (engagement: 85%, has email) → Send email ✅
- John (engagement: 40%, no email) → LinkedIn message ✅
- CEO (engagement: unknown) → Call script ✅

---

### Step 4: Writing Personalized Messages
**What happens:** We write a custom message for each person based on:
- Their company
- Their role
- What they care about (extracted from their industry)
- The channel we chose

**How:** We use a smart writing system that:
1. Looks at their background ("You work at a fintech")
2. Guesses their pain points ("You're probably scaling fast")
3. Writes a relevant opening ("I help fintechs scale securely")
4. Adds a call-to-action ("Schedule a quick call?")

**Example Email:**
```
Subject: Talent acquisition strategy for Vidoo

Dear Sallee,

I noticed Vidoo is expanding its EdTech presence. We have insights on 
retaining great talent as you grow.

Could we schedule a 15-min call next week?

Best,
SalesFlow AI
```

---

## What Gets Stored for Each Lead

When we process a lead, we save:
- **Name, Company, Email**
- **Engagement Score** (0-100, how likely to respond)
- **Priority Level** (Low/Medium/High based on fit)
- **Selected Channel** (Email, LinkedIn, or Call)
- **Personalized Content** (the actual message we wrote)

---

## Key Points for Non-Technical People

✅ **We don't use your personal data** — just what you tell us  
✅ **We match patterns** — if you say "hiring," we find HR people  
✅ **We pick the safest channel** — based on who they are  
✅ **Every message is custom** — not "copy-paste" spam  
✅ **You can edit before sending** — nothing goes out without your approval  

---

## If They Ask "But How?"

**Simple answer:** 
> We read what you want, search our database for matches, pick the best contact method, and write a personalized note. It's like having a super-fast assistant who reads message in 5 seconds instead of 5 minutes.

**Medium answer:**
> We use pattern recognition (like a spam filter, but in reverse) to understand your message, then apply matching rules to find people, classify them by engagement, and generate personalized outreach for each channel.

**Technical answer (if they push):**
> We use LLM-powered classification agents to extract intent/role/location from user input, rank ICP candidates via embeddings, apply decision rules for channel selection, and generate prompt-based content via GPT-4o.

---

## The Database We Use

File: `backend/data/mock_dataset.csv`

Contains ~4000 sample records:
| Name | Company | Email | Role | Location | Industry | Engagement |
|------|---------|-------|------|----------|----------|-----------|
| Sallee Kilbey | Vidoo | skilbey@vidoo.com | HR Manager | London | EdTech | 85 |
| John Smith | TechCorp | j.smith@techcorp.com | CTO | New York | SaaS | 72 |
| ... | ... | ... | ... | ... | ... | ... |

When you search, we filter this by role/location and score each match.

---

## Bottom Line

**What we really do:**
1. Understand what you want
2. Find people who match
3. Decide the best way to reach them
4. Write something personalized

**That's it.** Everything else is just speed & automation.

