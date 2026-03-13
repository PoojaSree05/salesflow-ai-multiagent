export interface StrategyResult {
  classification: {
    role: string;
    location: string;
    urgency: string;
    intent: string;
    businessBehavior: string;
  };
  icp: {
    name: string;
    company: string;
    email?: string;
    engagementScore: number;
    priorityLevel: "High" | "Medium" | "Low";
    similarityConfidence: number;
    rank: number;
  };
  channel: {
    selected: "Email" | "Call" | "LinkedIn";
    reasoning: string;
  };
  channel_reasoning?: string;
  execution:
  | {
    type: "Email";
    subject: string;
    body: string;
    cta: string;
  }
  | {
    type: "Call";
    script: string;
    keyPoints: string[];
  }
  | {
    type: "LinkedIn";
    connectionMessage: string;
    followUpMessage: string;
  };
  // Multi-ICP Campaign Meta
  total_sent?: number;
  success_count?: number;
  failed_count?: number;
  campaigns?: StrategyResult[];
}

export type PipelineStatus = "idle" | "loading" | "success" | "error";
