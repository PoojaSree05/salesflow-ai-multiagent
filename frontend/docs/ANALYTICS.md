Analytics Page — Working Logic

Overview

The Analytics page is a visualization layer derived entirely from the backend pipeline output. The frontend must NOT change backend behaviour; instead it transforms and visualizes the returned payload.

Expected backend payload (examples)
- classification: { role, location, urgency, intent, businessBehavior }
- icp_rankings: [ { name, company, email?, engagement_score, priority, similarity_score, rank }, ... ]
- selected_channel: string | { selected/type, reasoning }
- execution: object (email/call/linkedin)

Note: the backend may also already return the frontend-friendly `StrategyResult` shape. The client transforms whichever shape it receives into the UI model.

Transformation rules (frontend)
- If payload already contains `icp` and `classification`, the payload is used directly.
- If payload contains `icp_rankings` (array):
  - Map each ranking entry into a `StrategyResult`-like object where the `icp` fields are:
    - `name`: r.name || r.profile_name || "Unknown"
    - `company`: r.company || r.organization || ""
    - `engagementScore`: Number(r.engagement_score || r.engagementScore || 0) || 0
    - `priorityLevel`: r.priority || r.priorityLevel || "Low"
    - `similarityConfidence`: Number(r.similarity_score || r.similarityConfidence || 0) || 0
    - `rank`: Number(r.rank || 0) || 0
  - The top-ranked item is exposed as the root `result.icp` (used for single-ICP views).
  - The full mapped array is returned as `result.campaigns` for portfolio/multi views.
- If payload contains a single `icp` object, map its fields similarly.
- Channel mapping supports either a bare string (`"Email"`) or an object with `selected`/`type` + `reasoning`.

Analytics computations (visualization layer)

All analytics are computed in the frontend from the transformed `StrategyResult` or `result.campaigns`:

1) Portfolio Insights
- Matched Profiles: `icp_rankings.length` -> exposed as `portfolioStats.total` (if multi) or 1 for single
- High Priority Count: count where `icp.priorityLevel === "High"`
- Medium Priority Count: count where `icp.priorityLevel === "Medium"`
- Low Priority Count: count where `icp.priorityLevel === "Low"`
- Average Match Score: average of `icp.similarityConfidence` across the set. Protect against division by zero by dividing by `(total || 1)` and ensuring Number coercion.

2) Priority Distribution Chart
- Use counts for High/Medium/Low
- Build pie slices and filter zero-value slices to avoid rendering empty segments
- Display percentages computed from counts / total (ensure total > 0)

3) ICP Match Score Chart
- Map each ICP into `{ name, score: similarityConfidence }`
- Sort descending by `score`
- Render as horizontal bar chart with x-domain [0,100]

4) Lead Deep Dive
- Uses the root `icp` (first item for multi campaigns or the single icp)
- Show `Similarity Confidence` (`icp.similarityConfidence`)
- Compute `Open Probability` as a weighted blend of `engagementScore` and `similarityConfidence` (frontend heuristic), then round and cap properly
- Urgency Signal: derived from `classification.urgency` mapped to numeric values (High => 90, Medium => 60, Low => 35)
- Location, Intent, Behavior: from `classification`

5) Channel Decision Reasoning
- Display `channel.selected`
- Display `channel.reasoning` (falls back to `channel_reasoning` when present)

Important client-side safeguards
- Always coerce numeric fields with `Number(...) || 0` to avoid NaN and ensure charts display.
- When computing averages or percentages, guard division by zero: use `(total || 1)` or conditional early-return for empty lists.
- When building arrays for charts, filter out undefined names or null scores.
- Provide sensible defaults when fields are missing (e.g., "Unknown" for names, 0 for scores, "Low" for priority).

Developer notes
- The transformation logic lives in `src/lib/api.ts` inside `runStrategy()` and ensures the Analytics page receives a stable `StrategyResult`-like object.
- The visualization logic is implemented in `src/pages/AnalyticsPage.tsx` and expects `result` to have either a top-level `icp` + optional `campaigns` array or be null.
- If you need to add new charts or metrics, always update the transformer to surface required fields from backend payloads.

Troubleshooting
- If the ICP score appears empty in the UI:
  - Confirm the backend returned `icp_rankings` or `icp` with numeric `similarity_score` or `similarityConfidence` properties.
  - Check browser console for `NaN` or parsing errors; the transformer converts strings to numbers safely.
  - Inspect network response in devtools to see the raw pipeline payload and validate field names.

This document is intended to be a concise reference for developers maintaining the Analytics page and its mapping logic.
