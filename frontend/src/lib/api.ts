import type { StrategyResult } from "@/types/strategy";

const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

function transformToStrategyResult(payload: any): StrategyResult {
  // If it already looks like a StrategyResult, return as-is
  if (payload && payload.icp && payload.classification) {
    return payload as StrategyResult;
  }

  const classification = payload.classification ?? {
    role: "",
    location: "",
    urgency: "",
    intent: "",
    businessBehavior: "",
  };

  const selectedChannel = (() => {
    if (payload.channel) return payload.channel;
    if (payload.selected_channel) {
      if (typeof payload.selected_channel === "string") {
        return { selected: payload.selected_channel, reasoning: payload.channel_reasoning ?? "" };
      }
      return {
        selected: payload.selected_channel.selected ?? payload.selected_channel.type ?? "Email",
        reasoning: payload.selected_channel.reasoning ?? payload.channel_reasoning ?? "",
      };
    }
    return { selected: "Email", reasoning: payload.channel_reasoning ?? "" };
  })();

  const execution = payload.execution ?? payload.execution_object ?? {};

  if (Array.isArray(payload.icp_rankings) && payload.icp_rankings.length > 0) {
    const campaigns = payload.icp_rankings.map((r: any) => ({
      classification,
      icp: {
        name: r.name ?? r.profile_name ?? "Unknown",
        company: r.company ?? r.organization ?? "",
        email: r.email,
        engagementScore: Number(r.engagement_score ?? r.engagementScore ?? 0) || 0,
        priorityLevel: (r.priority ?? r.priorityLevel ?? "Low") as any,
        similarityConfidence: Number(r.similarity_score ?? r.similarityConfidence ?? 0) || 0,
        rank: Number(r.rank ?? 0) || 0,
      },
      channel: selectedChannel,
      execution: execution as any,
    }));

    const root = campaigns[0];
    return {
      ...root,
      campaigns,
    } as StrategyResult;
  }

  const icpRaw = payload.icp ?? {};
  const icp = {
    name: icpRaw.name ?? icpRaw.profile_name ?? "Unknown",
    company: icpRaw.company ?? "",
    email: icpRaw.email,
    engagementScore: Number(icpRaw.engagementScore ?? icpRaw.engagement_score ?? 0) || 0,
    priorityLevel: (icpRaw.priorityLevel ?? icpRaw.priority ?? "Low") as any,
    similarityConfidence: Number(icpRaw.similarityConfidence ?? icpRaw.similarity_score ?? 0) || 0,
    rank: Number(icpRaw.rank ?? 0) || 0,
  };

  return {
    classification,
    icp,
    channel: selectedChannel,
    execution: execution as any,
  } as StrategyResult;
}

export async function runStrategy(input: string, campaignMode: "single" | "multi" = "single"): Promise<StrategyResult> {
  const response = await fetch(`${API_BASE}/run-strategy`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input, campaignMode }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ error: response.statusText }));
    throw new Error(err.error ?? `Request failed: ${response.status}`);
  }

  const raw = await response.json();
  return transformToStrategyResult(raw);
}

export async function sendEmail(data: {
  subject: string;
  body: string;
  recipient: string;
}): Promise<{ success: boolean }> {
  const response = await fetch(`${API_BASE}/send-email`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      to: data.recipient,
      subject: data.subject,
      body: data.body,
    }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ error: response.statusText }));
    throw new Error(err.error ?? `Request failed: ${response.status}`);
  }

  return response.json();
}
export type IcpLead = {
  name: string;
  company: string;
  email: string;
  role: string;
  industry: string;
  location: string;
  engagement_score: number;
  priority: "High" | "Medium" | "Low";
  icp_match: boolean;
  match_score: number;
  pain_point: string;
  tier: string;
  run_at?: string;
};

export type LeadsResponse = {
  /** true once at least one strategy run has been made */
  has_runs: boolean;
  total_qualified: number;
  leads: IcpLead[];
};

export async function getLeads(): Promise<LeadsResponse> {
  const response = await fetch(`${API_BASE}/leads`);
  if (!response.ok) {
    throw new Error(`Failed to fetch leads: ${response.status}`);
  }
  const data = await response.json();
  return {
    has_runs: data.has_runs ?? false,
    total_qualified: data.total_qualified ?? 0,
    leads: Array.isArray(data.leads) ? data.leads : [],
  };
}

export async function getCampaigns(): Promise<Array<StrategyResult & { created_at: string; status: string }>> {
  const response = await fetch(`${API_BASE}/campaigns`);
  if (!response.ok) {
    throw new Error(`Failed to fetch campaigns: ${response.status}`);
  }
  const raw = await response.json();

  if (!Array.isArray(raw)) return [];

  return raw.map((item: any) => {
    const r = transformToStrategyResult(item);
    return {
      ...r,
      created_at: item.created_at ?? item.createdAt ?? "",
      status: item.status ?? "",
    };
  });
}
