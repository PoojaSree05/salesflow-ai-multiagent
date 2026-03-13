import { useMemo } from "react";
import {
  BarChart2, TrendingUp, Target, Zap,
  PieChart as PieChartIcon, BarChart as BarChartIcon,
  Users, Award, ShieldCheck, Activity, SendHorizonal
} from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend
} from "recharts";
import type { StrategyResult } from "@/types/strategy";

interface AnalyticsPageProps {
  result: StrategyResult | null;
}

export function AnalyticsPage({ result }: AnalyticsPageProps) {
  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center h-80 space-y-3 text-center">
        <BarChart2 size={40} strokeWidth={1.2} className="text-muted-foreground" />
        <h2 className="text-lg font-semibold text-foreground">No analytics yet</h2>
        <p className="text-sm text-muted-foreground max-w-xs">
          Run a strategy from the Dashboard to see engagement metrics and confidence scores.
        </p>
      </div>
    );
  }

  const isMulti = result.campaigns && result.campaigns.length > 0;
  const allIcps = isMulti ? result.campaigns! : [result];

  const portfolioStats = useMemo(() => {
    const total = allIcps.length;
    const high = allIcps.filter(c => c.icp.priorityLevel === "High").length;
    const med = allIcps.filter(c => c.icp.priorityLevel === "Medium").length;
    const low = allIcps.filter(c => c.icp.priorityLevel === "Low").length;
    const avgScore = allIcps.reduce((acc, c) => acc + c.icp.similarityConfidence, 0) / (total || 1);

    const pieData = [
      { name: "High", value: high, color: "#10b981" },
      { name: "Medium", value: med, color: "#f59e0b" },
      { name: "Low", value: low, color: "#6b7280" },
    ].filter(d => d.value > 0);

    const barData = allIcps
      .map(c => ({
        name: c.icp.name,
        score: c.icp.similarityConfidence,
      }))
      .sort((a, b) => b.score - a.score);

    return { total, high, med, low, avgScore, pieData, barData };
  }, [allIcps]);

  const { icp, channel, classification } = result;

  const openProbability = Math.round((icp.engagementScore * 0.8 + icp.similarityConfidence * 0.2) / 10) * 10;
  const urgencyScore = classification.urgency === "High" ? 90 : classification.urgency === "Medium" ? 60 : 35;

  const confidenceMetrics = [
    {
      label: "Engagement Score",
      value: icp.engagementScore,
      max: 100,
      color: "primary",
      icon: <TrendingUp size={18} />,
      description: "Historical engagement likelihood for this ICP profile",
    },
    {
      label: "Similarity Confidence",
      value: icp.similarityConfidence,
      max: 100,
      color: "secondary",
      icon: <Target size={18} />,
      description: "How closely this lead matches the ideal customer profile",
    },
    {
      label: "Open Probability",
      value: openProbability,
      max: 100,
      color: "primary",
      icon: <BarChart2 size={18} />,
      description: "Predicted likelihood of message being opened or responded to",
    },
    {
      label: "Urgency Signal",
      value: urgencyScore,
      max: 100,
      color: "secondary",
      icon: <Zap size={18} />,
      description: "Strength of the buying urgency signal detected from the input",
    },
  ];

  return (
    <div className="space-y-8 animate-fade-in pb-10">
      {/* Page Title */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">AI Lead Intelligence Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">
          {isMulti ? "Enterprise-wide lead portfolio analysis and engagement metrics." : `Detailed intelligence report for ${icp.name}.`}
        </p>
      </div>

      {/* ICP Portfolio Insights Section */}
      <div className="space-y-6">
        <div className="flex items-center gap-2">
          <PieChartIcon size={20} className="text-primary" />
          <h2 className="text-lg font-bold text-foreground">Portfolio Insights</h2>
        </div>

        {/* Aggregate Stat Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <StatCard label="Matched Profiles" value={portfolioStats.total.toString()} icon={<Users size={16} />} />
          <StatCard label="Campaigns Executed" value={isMulti ? portfolioStats.total.toString() : "1"} color="indigo" icon={<SendHorizonal size={16} />} />
          <StatCard label="High Priority" value={portfolioStats.high.toString()} color="emerald" icon={<Award size={16} />} />
          <StatCard label="Medium Priority" value={portfolioStats.med.toString()} color="amber" icon={<Activity size={16} />} />
          <StatCard label="Low Priority" value={portfolioStats.low.toString()} color="slate" icon={<ShieldCheck size={16} />} />
          <StatCard label="Avg Match" value={`${portfolioStats.avgScore.toFixed(1)}%`} icon={<Target size={16} />} />
        </div>

        {/* Visual Distribution row */}
        {isMulti ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="glass-card p-6 h-[350px] flex flex-col">
              <h3 className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-4">Priority Distribution</h3>
              <div className="flex-1">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={portfolioStats.pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {portfolioStats.pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ backgroundColor: "#1e293b", border: "none", borderRadius: "8px", fontSize: "12px" }}
                      itemStyle={{ color: "#fff" }}
                    />
                    <Legend verticalAlign="bottom" height={36} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="glass-card p-6 h-[350px] flex flex-col">
              <h3 className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-4">ICP Match Scores</h3>
              <div className="flex-1">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={portfolioStats.barData} layout="vertical" margin={{ left: 20, right: 30 }}>
                    <XAxis type="number" domain={[0, 100]} hide />
                    <YAxis
                      dataKey="name"
                      type="category"
                      axisLine={false}
                      tickLine={false}
                      fontSize={11}
                      width={100}
                    />
                    <Tooltip
                      cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                      contentStyle={{ backgroundColor: "#1e293b", border: "none", borderRadius: "8px", fontSize: "12px" }}
                      itemStyle={{ color: "#fff" }}
                    />
                    <Bar dataKey="score" radius={[0, 4, 4, 0]}>
                      {portfolioStats.barData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.score >= 80 ? "#6366f1" : "#818cf8"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        ) : (
          <div className="glass-card p-10 flex flex-col items-center justify-center text-center">
            <Target size={32} className="text-muted-foreground/40 mb-3" />
            <p className="text-sm text-muted-foreground">Single ICP campaign — Portfolio distribution insights limited.</p>
          </div>
        )}
      </div>

      <div className="border-t border-border/40 pt-8 space-y-8">
        <div className="flex items-center gap-2">
          <Activity size={20} className="text-indigo-500" />
          <h2 className="text-lg font-bold text-foreground">Lead Deep-Dive: {icp.name}</h2>
        </div>

        {/* Current target KPI row */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard label="Global Rank" value={`#${icp.rank}`} sub="Relative lead power" />
          <KpiCard label="Priority Level" value={icp.priorityLevel} sub="Outreach urgency" highlight={icp.priorityLevel === "High"} />
          <KpiCard label="Recommended Channel" value={channel.selected} sub={`Optimal: ${channel.selected}`} />
          <KpiCard label="Detected Intent" value={classification.intent} sub="User goal mapping" />
        </div>

        {/* Confidence metrics and breakdown side-by-side on desktop */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          <div className="lg:col-span-3 glass-card p-6 space-y-6">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-1 h-4 rounded-full bg-indigo-500" />
              <h2 className="text-sm font-bold uppercase tracking-wider text-foreground">Confidence Matrix</h2>
            </div>
            <div className="grid gap-6">
              {confidenceMetrics.map((m) => (
                <MetricBar key={m.label} {...m} />
              ))}
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            <div className="glass-card p-6 space-y-4">
              <div className="flex items-center gap-2">
                <div className="w-1 h-4 rounded-full bg-indigo-500" />
                <h2 className="text-sm font-bold uppercase tracking-wider text-foreground">Classification Details</h2>
              </div>
              <div className="grid gap-3">
                {[
                  { label: "Detected Role", value: classification.role },
                  { label: "Target Location", value: classification.location },
                  { label: "Urgency Level", value: classification.urgency },
                  { label: "Behavior Pulse", value: classification.businessBehavior },
                ].map(({ label, value }) => (
                  <div key={label} className="p-3 rounded-xl border border-border/40 bg-muted/20">
                    <p className="text-[10px] uppercase font-bold text-muted-foreground mb-0.5">{label}</p>
                    <p className="text-sm font-medium text-foreground">{value || "Not detected"}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card p-6 space-y-4">
              <div className="flex items-center gap-2">
                <div className="w-1 h-4 rounded-full bg-indigo-500" />
                <h2 className="text-sm font-bold uppercase tracking-wider text-foreground">Channel Logic</h2>
              </div>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full btn-gradient text-white uppercase">
                    {channel.selected}
                  </span>
                  <span className="text-[10px] text-muted-foreground uppercase font-semibold">Recommended Path</span>
                </div>
                <p className="text-sm text-foreground/80 leading-relaxed italic border-l-2 border-indigo-500/20 pl-3">
                  "{channel.reasoning}"
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon, color }: { label: string; value: string; icon: React.ReactNode; color?: string }) {
  const colorClasses: Record<string, string> = {
    emerald: "text-emerald-500 bg-emerald-500/10 border-emerald-500/20",
    amber: "text-amber-500 bg-amber-500/10 border-amber-500/20",
    slate: "text-slate-400 bg-slate-400/10 border-slate-400/20",
    default: "text-primary bg-primary/10 border-primary/20",
    indigo: "text-indigo-500 bg-indigo-500/10 border-indigo-500/20"
  };

  const selectedColor = color ? colorClasses[color] : colorClasses.default;

  return (
    <div className="glass-card p-5 group hover:border-indigo-500/30 transition-all border border-white/5 space-y-3">
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center border ${selectedColor}`}>
        {icon}
      </div>
      <div>
        <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest">{label}</p>
        <p className="text-xl font-bold text-foreground mt-0.5">{value}</p>
      </div>
    </div>
  );
}

function MetricBar({
  label,
  value,
  max,
  icon,
  description,
}: {
  label: string;
  value: number;
  max: number;
  color: string;
  icon: React.ReactNode;
  description: string;
}) {
  const pct = Math.min(100, Math.round((value / max) * 100));
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
          <span className="text-indigo-500">{icon}</span>
          {label}
        </div>
        <span className="text-sm font-bold text-foreground font-mono">{value}<span className="text-muted-foreground text-xs ml-1 font-sans">/{max}</span></span>
      </div>
      <div className="h-2 rounded-full bg-muted overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-indigo-600 to-indigo-400 shadow-[0_0_8px_rgba(99,102,241,0.5)] transition-all duration-1000"
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="text-[10px] text-muted-foreground leading-snug">{description}</p>
    </div>
  );
}

function KpiCard({ label, value, sub, highlight = false }: { label: string; value: string; sub: string; highlight?: boolean }) {
  return (
    <div className="glass-card p-5 border border-white/5 hover:border-indigo-500/20 transition-all">
      <p className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold mb-1.5">{label}</p>
      <p className={`text-xl font-bold leading-none ${highlight ? "text-indigo-500" : "text-foreground"}`}>{value}</p>
      <p className="text-[11px] text-muted-foreground mt-2 inline-block px-2 py-0.5 rounded bg-muted/50">{sub}</p>
    </div>
  );
}
