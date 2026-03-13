import { useState } from "react";
import { Bot, MapPin, Zap, Target, Activity, Info } from "lucide-react";
import type { StrategyResult } from "@/types/strategy";
import type { PipelineStatus } from "@/types/strategy";

interface ClassificationCardProps {
  data?: StrategyResult["classification"];
  status: PipelineStatus;
}

export function ClassificationCard({ data, status }: ClassificationCardProps) {
  const rows = [
    { icon: <Target size={14} />, label: "Target Role", value: data?.role },
    { icon: <MapPin size={14} />, label: "Headquarters", value: data?.location },
    { icon: <Zap size={14} />, label: "Urgency Level", value: data?.urgency },
    { icon: <Activity size={14} />, label: "Buying Intent", value: data?.intent },
    { icon: <Bot size={14} />, label: "Engagement Pattern", value: data?.businessBehavior },
  ];

  return (
    <AgentCardShell
      number={1}
      title="Classification Engine"
      status={status}
    >
      {status === "loading" && <SkeletonRows count={5} />}
      {status === "success" && data && (
        <div className="space-y-3">
          {rows.map((row) => (
            <div key={row.label} className="flex gap-3 items-start">
              <span className="flex-shrink-0 mt-1 text-primary/60">{row.icon}</span>
              <div className="min-w-0">
                <span className="text-[10px] uppercase tracking-[0.1em] text-muted-foreground font-bold block mb-0.5 opacity-60">{row.label}</span>
                <span className="text-xs font-semibold text-foreground break-words leading-tight">{row.value}</span>
              </div>
            </div>
          ))}
        </div>
      )}
      {status === "idle" && <EmptyState />}
    </AgentCardShell>
  );
}

import { Star, BarChart2 } from "lucide-react";

interface IcpCardProps {
  data?: StrategyResult["icp"];
  status: PipelineStatus;
}

export function IcpCard({ data, status }: IcpCardProps) {
  return (
    <AgentCardShell number={2} title="ICP Intelligence Engine" status={status}>
      {status === "loading" && <SkeletonRows count={5} />}
      {status === "success" && data && (
        <div className="space-y-5">
          {/* Rank badge */}
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1 text-[12px] font-extrabold px-3 py-1 rounded-full btn-gradient text-white shadow-md shadow-primary/20">
              <Star size={11} fill="currentColor" />
              Rank #{data.rank}
            </span>
            <span className={data.priorityLevel === "High" ? "badge-priority-high" : "badge-priority-medium"}>
              {data.priorityLevel} Priority
            </span>
          </div>

          <div className="space-y-3">
            <DataRow label="Ideal Lead Name" value={data.name} />
            <DataRow label="Target Organization" value={data.company} />
            <DataRow label="System Priority" value={data.priorityLevel} />
          </div>

          {/* Scores */}
          <div className="space-y-4 pt-2">
            <ScoreBar label="Engagement Score" value={data.engagementScore} max={100} />
            <ScoreBar label="Similarity Confidence" value={data.similarityConfidence} max={100} suffix="%" />
          </div>
        </div>
      )}
      {status === "idle" && <EmptyState />}
    </AgentCardShell>
  );
}

import { createPortal } from "react-dom";
import { Mail, Phone, Linkedin, X } from "lucide-react";

interface ChannelCardProps {
  data?: StrategyResult["channel"];
  status: PipelineStatus;
  fullReasoning?: string;
  urgency?: string;
  engagementScore?: number;
  icpPriority?: string;
}

const channelIcons: Record<string, React.ReactNode> = {
  Email: <Mail size={32} strokeWidth={1.5} />,
  Call: <Phone size={32} strokeWidth={1.5} />,
  LinkedIn: <Linkedin size={32} strokeWidth={1.5} />,
};

export function ChannelCard({
  data,
  status,
  fullReasoning,
  urgency,
  engagementScore,
  icpPriority
}: ChannelCardProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <AgentCardShell number={3} title="Channel Decision Engine" status={status}>
      {status === "loading" && <SkeletonRows count={3} />}
      {status === "success" && data && (
        <>
          <div className="space-y-5">
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center w-16 h-16 rounded-2xl btn-gradient text-white shadow-xl shadow-primary/20">
                {channelIcons[data.selected]}
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground font-bold opacity-60">Selected Channel</p>
                <p className="text-xl font-black text-foreground">{data.selected}</p>
              </div>
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground font-bold mb-2 opacity-60">Strategic Reasoning</p>
              <p className="text-xs text-muted-foreground leading-relaxed line-clamp-3 font-medium">{data.reasoning}</p>
            </div>

            <button
              onClick={() => setIsModalOpen(true)}
              className="flex items-center gap-2 text-[11px] font-bold text-primary hover:text-primary/80 transition-all mt-2 group/btn"
            >
              <Info size={14} className="group-hover/btn:scale-110 transition-transform" />
              Detailed Decision Logic
            </button>
          </div>

          {/* Reasoning Overlay - Portal to Root */}
          {isModalOpen && createPortal(
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
              <div className="relative bg-card border border-white/10 rounded-2xl shadow-2xl max-w-2xl w-[90%] overflow-hidden p-6 animate-in zoom-in-95 duration-300">

                {/* Close Button */}
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="absolute top-4 right-4 p-2 rounded-full hover:bg-white/5 text-muted-foreground hover:text-foreground transition-all z-10"
                >
                  <X size={20} />
                </button>

                <div className="space-y-6">
                  {/* Header */}
                  <div>
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[10px] font-bold uppercase tracking-widest mb-2">
                      <Zap size={10} />
                      Decision Analysis
                    </div>
                    <h2 className="text-2xl font-bold text-foreground">Channel Decision Analysis</h2>
                  </div>

                  {/* Recommendation Pathway */}
                  <div className="p-4 rounded-xl bg-indigo-600/5 border border-indigo-500/10 flex items-center gap-5">
                    <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-indigo-600 text-white shrink-0 shadow-lg shadow-indigo-600/20">
                      {channelIcons[data.selected]}
                    </div>
                    <div>
                      <div className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">Recommended Pathway</div>
                      <div className="text-xl font-bold text-foreground">{data.selected}</div>
                    </div>
                  </div>

                  {/* Metrics Grid */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="p-3 rounded-xl bg-muted/30 border border-border/50">
                      <div className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold mb-1">Urgency</div>
                      <div className="text-sm font-bold text-foreground flex items-center gap-1.5">
                        <Activity size={12} className="text-amber-400" />
                        {urgency || "Normal"}
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-muted/30 border border-border/50">
                      <div className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold mb-1">Score</div>
                      <div className="text-sm font-bold text-foreground flex items-center gap-1.5">
                        <Star size={12} className="text-indigo-400" fill="currentColor" />
                        {engagementScore || 0}%
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-muted/30 border border-border/50">
                      <div className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold mb-1">Priority</div>
                      <div className="text-sm font-bold text-foreground flex items-center gap-1.5">
                        <Target size={12} className="text-emerald-400" />
                        {icpPriority || "N/A"}
                      </div>
                    </div>
                  </div>

                  {/* Logical Reasoning */}
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="h-px flex-1 bg-border/50" />
                      <span className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold">Logic</span>
                      <div className="h-px flex-1 bg-border/50" />
                    </div>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {fullReasoning || data.reasoning}
                    </p>
                  </div>

                  {/* Footer */}
                  <div className="pt-2">
                    <button
                      onClick={() => setIsModalOpen(false)}
                      className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl transition-all shadow-lg shadow-indigo-600/10 active:scale-[0.98]"
                    >
                      Dismiss Analysis
                    </button>
                  </div>
                </div>
              </div>
            </div>,
            document.body
          )}
        </>
      )}
      {status === "idle" && <EmptyState />}
    </AgentCardShell>
  );
}

// ── Shared primitives ─────────────────────────────────────────────────────────

function AgentCardShell({
  number,
  title,
  status,
  children,
}: {
  number: number;
  title: string;
  status: PipelineStatus;
  children: React.ReactNode;
}) {
  const dotClass =
    status === "success"
      ? "status-dot status-dot-success"
      : status === "loading"
        ? "status-dot status-dot-loading"
        : status === "error"
          ? "status-dot status-dot-error"
          : "status-dot status-dot-idle";

  return (
    <div
      className={`glass-card p-6 flex flex-col gap-4 min-w-0 w-full animate-slide-in agent-card-${number} transition-all duration-300 hover:translate-y-[-4px] hover:border-primary/20 ${status === "loading" ? "opacity-90 ring-1 ring-primary/20" : ""
        }`}
    >
      <div className="flex items-center justify-between pb-2 border-b border-border/40">
        <div className="flex items-center gap-3">
          <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-primary/10 text-primary font-mono border border-primary/20">
            A{number}
          </span>
          <h3 className="text-sm font-bold text-foreground leading-tight tracking-tight">{title}</h3>
        </div>
        <span className={`${dotClass} scale-125`} />
      </div>
      <div className="flex-1 pt-1">{children}</div>
    </div>
  );
}

function DataRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</span>
      <p className="text-xs font-medium text-foreground">{value}</p>
    </div>
  );
}

function ScoreBar({ label, value, max, suffix = "" }: { label: string; value: number; max: number; suffix?: string }) {
  return (
    <div>
      <div className="flex justify-between mb-1">
        <span className="text-[10px] text-muted-foreground">{label}</span>
        <span className="text-[10px] font-semibold text-foreground">
          {value}{suffix}
        </span>
      </div>
      <div className="score-bar">
        <div className="score-bar-fill" style={{ width: `${(value / max) * 100}%` }} />
      </div>
    </div>
  );
}

function SkeletonRows({ count }: { count: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="space-y-1">
          <div className="skeleton-pulse h-2 w-16 rounded" />
          <div className="skeleton-pulse h-3 rounded" style={{ width: `${60 + (i % 3) * 15}%` }} />
        </div>
      ))}
    </div>
  );
}

function EmptyState() {
  return (
    <p className="text-[11px] text-muted-foreground italic text-center py-4">Awaiting activation…</p>
  );
}
