import { StrategyInput } from "@/components/dashboard/StrategyInput";
import { AgentPipeline } from "@/components/dashboard/AgentPipeline";
import { Sparkles, Target, TrendingUp, Zap, Star, BarChart2 } from "lucide-react";
import type { StrategyResult, PipelineStatus } from "@/types/strategy";

interface DashboardPageProps {
  onRun: (input: string, campaignMode: "single" | "multi") => void;
  pipelineStatus: PipelineStatus;
  result: StrategyResult | null;
  errorMessage: string | null;
  onAnimationComplete?: () => void;
}

export function DashboardPage({
  onRun,
  pipelineStatus,
  result,
  errorMessage,
  onAnimationComplete,
}: DashboardPageProps) {

  return (
    <div className="space-y-4 animate-fade-in">
      {/* ── Page header ── */}
      <div className="flex flex-col sm:flex-row sm:items-end gap-3">
        <div className="flex-1">
          <h1 className="text-xl font-bold text-foreground">Dashboard</h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            Define your target and activate the multi-agent pipeline.
          </p>
        </div>
        {/* Quick stats — only after a run */}
        {result && (
          <div className="flex items-center gap-2 flex-wrap">
            <QuickStat icon={<Target size={12} />} label="ICP Rank" value={`#${result.icp.rank}`} />
            <QuickStat icon={<TrendingUp size={12} />} label="Engagement" value={`${result.icp.engagementScore}%`} />
            <QuickStat icon={<Zap size={12} />} label="Channel" value={result.channel.selected} />
          </div>
        )}
      </div>

      {/* ── Strategy Input ── */}
      <div className="w-full pt-1">
        <StrategyInput onRun={onRun} isLoading={pipelineStatus === "loading"} />
      </div>

      {/* ── Strategy Summary (compact) — only after a successful run ── */}
      {result && pipelineStatus === "success" && (
        <div className="space-y-3 w-full transition-all duration-500 animate-in fade-in">
          {result.total_sent ? (
            <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
                  <Sparkles size={20} />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-foreground">Multi-ICP Campaign Successful</h2>
                  <p className="text-xs text-muted-foreground">
                    Orchestrated {result.total_sent} personalized campaigns. {result.success_count} sent,{" "}
                    {result.failed_count} skipped.
                  </p>
                </div>
              </div>
              <div className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-500 text-[10px] font-bold uppercase tracking-wider border border-emerald-500/20">
                Active
              </div>
            </div>
          ) : (
            <div className="rounded-xl border border-border/40 bg-muted/10 p-3 flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-7 h-7 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                  <Sparkles size={14} />
                </div>
                <h2 className="text-[10px] font-bold text-foreground uppercase tracking-wider">
                  Strategy Insight
                </h2>
              </div>
              <div className="flex items-center gap-6">
                {[
                  { label: "Role", value: result.classification.role },
                  { label: "Company", value: result.icp.company },
                  { label: "Priority", value: result.icp.priorityLevel },
                  { label: "Channel", value: result.channel.selected },
                ].map(({ label, value }) => (
                  <div key={label} className="flex flex-col">
                    <span className="text-[8px] uppercase tracking-tighter text-muted-foreground font-bold">
                      {label}
                    </span>
                    <span className="text-xs font-bold text-foreground whitespace-nowrap">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── Agent Pipeline ── */}
      <div className="mt-4">
        <AgentPipeline
          result={result}
          status={pipelineStatus}
          errorMessage={errorMessage}
          onAnimationComplete={onAnimationComplete}
        />
      </div>
    </div>
  );
}

// ── MetricPill ────────────────────────────────────────────────────────────────

function MetricPill({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  color: "indigo" | "emerald" | "amber";
}) {
  const colors = { indigo: "text-indigo-400", emerald: "text-emerald-400", amber: "text-amber-400" };
  return (
    <div className="flex flex-col items-center gap-0.5">
      <div className={`flex items-center gap-1 text-xs font-bold ${colors[color]}`}>
        <span className={colors[color]}>{icon}</span>
        {value}
      </div>
      <span className="text-[9px] text-muted-foreground uppercase tracking-wider">{label}</span>
    </div>
  );
}

// ── QuickStat ─────────────────────────────────────────────────────────────────

function QuickStat({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border bg-card/60 text-xs">
      <span className="text-primary">{icon}</span>
      <span className="text-muted-foreground">{label}:</span>
      <span className="font-semibold text-foreground">{value}</span>
    </div>
  );
}
