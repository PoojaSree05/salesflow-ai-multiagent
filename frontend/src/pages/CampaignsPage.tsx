import { useState, useEffect, useMemo } from "react";
import { Mail, Phone, Linkedin, Calendar, User, Building2, CheckCircle2, XCircle, Clock, Copy, BarChart3, TrendingUp, Zap, SendHorizonal, Download } from "lucide-react";
import type { StrategyResult } from "@/types/strategy";
import { getCampaigns } from "@/lib/api";

type CampaignEntry = StrategyResult & { created_at: string; status: string };

export function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<CampaignEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const analytics = useMemo(() => {
    if (!campaigns.length) return { total: 0, emails: 0, linkedin: 0, calls: 0, successRate: 0, today: 0 };

    const today = new Date().toDateString();
    return {
      total: campaigns.length,
      emails: campaigns.filter(c => c.execution.type === "Email").length,
      linkedin: campaigns.filter(c => c.execution.type === "LinkedIn").length,
      calls: campaigns.filter(c => c.execution.type === "Call").length,
      successRate: Math.round((campaigns.filter(c => c.status === "Sent").length / campaigns.length) * 100),
      today: campaigns.filter(c => new Date(c.created_at).toDateString() === today).length
    };
  }, [campaigns]);

  const fetchCampaigns = async () => {
    setLoading(true);
    try {
      const data = await getCampaigns();
      setCampaigns(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load campaigns");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCampaigns();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-80 space-y-4">
        <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-muted-foreground">Loading campaign history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-80 space-y-4 text-center">
        <div className="p-4 rounded-full bg-destructive/10 text-destructive">
          <XCircle size={32} />
        </div>
        <h2 className="text-lg font-semibold text-foreground">Failed to Load History</h2>
        <p className="text-sm text-muted-foreground max-w-xs">{error}</p>
        <button
          onClick={fetchCampaigns}
          className="mt-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-lg transition-all"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (campaigns.length === 0) {
    return (
      <EmptyState
        icon={<Calendar size={48} strokeWidth={1} className="text-muted-foreground/30" />}
        title="No campaigns have been sent yet."
        description="Run a multi-agent strategy from the dashboard to start generating outreach."
      />
    );
  }

  const handleExport = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(campaigns, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "campaign-history.json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Campaign History</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Review and track all your generated multi-agent outreach campaigns.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleExport}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-all shadow-lg shadow-indigo-500/20"
            title="Export to JSON"
          >
            <Download size={14} />
            Export History
          </button>
          <button
            onClick={fetchCampaigns}
            className="p-2 rounded-lg bg-muted/50 hover:bg-muted text-muted-foreground transition-all border border-border/50"
            title="Refresh History"
          >
            <Clock size={16} />
          </button>
        </div>
      </div>

      {/* Matched leads panel for most recent multi-lead run */}
      {campaigns.length > 1 && (() => {
        // Group contiguous recent campaigns from the top that were created
        // within a short time window. This captures multi-ICP runs where
        // each ICP was appended with slightly different timestamps.
        const THRESHOLD_MS = 60 * 1000; // 60 seconds
        const recentGroup: CampaignEntry[] = [campaigns[0]];
        for (let i = 1; i < campaigns.length; i++) {
          try {
            const prevTs = new Date(campaigns[i - 1].created_at).getTime();
            const currTs = new Date(campaigns[i].created_at).getTime();
            if (isNaN(prevTs) || isNaN(currTs)) break;
            if (prevTs - currTs <= THRESHOLD_MS) {
              recentGroup.push(campaigns[i]);
            } else {
              break; // stop at first non-contiguous entry
            }
          } catch (e) {
            break;
          }
        }

        if (recentGroup.length > 1) {
          return (
            <div className="glass-card p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-foreground">Matched Leads (Most Recent Multi-Lead Run)</h3>
                <p className="text-xs text-muted-foreground">{recentGroup.length} leads</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {recentGroup.map((c, i) => (
                  <div key={i} className="p-3 rounded-lg border border-border/40 bg-muted/10 flex items-start gap-3">
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <div className="text-sm font-semibold text-foreground">{c.icp?.name ?? 'Unknown'}</div>
                        <div className="text-xs text-muted-foreground">{c.icp?.engagementScore ?? ''}%</div>
                      </div>
                      <div className="text-xs text-muted-foreground">{c.icp?.company}</div>
                      <div className="text-xs text-muted-foreground">{c.icp?.email}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        }
        return null;
      })()}

      {/* Analytics Dashboard */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard
          icon={<BarChart3 size={18} />}
          label="Total Campaigns"
          value={analytics.total.toString()}
          color="blue"
        />
        <StatCard
          icon={<Mail size={18} />}
          label="Emails Sent"
          value={analytics.emails.toString()}
          color="indigo"
        />
        <StatCard
          icon={<Linkedin size={18} />}
          label="LinkedIn Sent"
          value={analytics.linkedin.toString()}
          color="sky"
        />
        <StatCard
          icon={<Phone size={18} />}
          label="Calls Scheduled"
          value={analytics.calls.toString()}
          color="emerald"
        />
        <StatCard
          icon={<TrendingUp size={18} />}
          label="Success Rate"
          value={`${analytics.successRate}%`}
          color="amber"
        />
        <StatCard
          icon={<Calendar size={18} />}
          label="Sent Today"
          value={analytics.today.toString()}
          color="rose"
        />
      </div>

      <div className="pt-4">
        <div className="flex items-center gap-2 mb-4">
          <SendHorizonal size={16} className="text-muted-foreground" />
          <h2 className="text-sm font-bold text-foreground">Outreach History</h2>
        </div>
        <div className="grid gap-4">
          {campaigns.map((campaign, idx) => (
            <CampaignCard key={campaign.created_at + idx} campaign={campaign} />
          ))}
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: string; color: string }) {
  const colorMap: Record<string, string> = {
    blue: "text-blue-500 bg-blue-500/10 border-blue-500/20",
    indigo: "text-indigo-500 bg-indigo-500/10 border-indigo-500/20",
    sky: "text-sky-500 bg-sky-500/10 border-sky-500/20",
    emerald: "text-emerald-500 bg-emerald-500/10 border-emerald-500/20",
    amber: "text-amber-500 bg-amber-500/10 border-amber-500/20",
    rose: "text-rose-500 bg-rose-500/10 border-rose-500/20",
  };

  return (
    <div className="glass-card p-4 flex flex-col gap-3 group hover:border-white/20 transition-all border border-white/5">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center border ${colorMap[color]}`}>
        {icon}
      </div>
      <div>
        <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider">{label}</p>
        <p className="text-xl font-bold text-foreground mt-0.5">{value}</p>
      </div>
    </div>
  );
}

function CampaignCard({ campaign }: { campaign: CampaignEntry }) {
  const { execution, icp, channel, created_at, status } = campaign;

  // Format the date
  const dateStr = new Date(created_at).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  // Extract preview and title based on type
  let title = "";
  let preview = "";

  if (execution.type === "Email") {
    title = execution.subject;
    preview = execution.body;
  } else if (execution.type === "Call") {
    title = "Call Script Strategy";
    preview = execution.script;
  } else if (execution.type === "LinkedIn") {
    title = "LinkedIn Outreach Chain";
    preview = execution.connectionMessage;
  }

  // Truncate preview to ~3 lines (approx)
  const truncatedPreview = preview.split('\n').slice(0, 3).join('\n');

  return (
    <div className="glass-card hover:border-indigo-500/30 transition-all group overflow-hidden">
      <div className="p-5 flex flex-col md:flex-row gap-5 items-start">
        {/* Left Column: Icon & Metas */}
        <div className="flex flex-col gap-3 min-w-[140px]">
          {/* Use execution type as the source of truth for what happened */}
          <ChannelBadge channel={execution.type as "Email" | "Call" | "LinkedIn"} />

          <div className="space-y-1.5 pt-1">
            <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
              <Clock size={12} />
              {dateStr}
            </div>
            <StatusBadge status={status} />
          </div>
        </div>

        {/* Center: Content Preview */}
        <div className="flex-1 space-y-3 min-w-0">
          <div className="space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[10px] uppercase font-bold text-indigo-400 tracking-widest">Subject</span>
              <h3 className="text-base font-bold text-foreground truncate">{title}</h3>
            </div>

            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <div className="flex items-center gap-1.5">
                <User size={12} />
                <span className="font-medium text-foreground/80">{icp?.name}</span>
              </div>
              {icp?.company && (
                <div className="flex items-center gap-1.5">
                  <Building2 size={12} />
                  <span className="text-muted-foreground">{icp.company}</span>
                </div>
              )}
            </div>
          </div>

          <div className="p-3 bg-muted/20 rounded-xl border border-white/5">
            <p className="text-xs text-muted-foreground leading-relaxed whitespace-pre-wrap line-clamp-3">
              {truncatedPreview}...
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const isSent = status === "Sent";
  return (
    <div className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${isSent ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20" : "bg-zinc-500/10 text-zinc-400 border border-zinc-500/20"
      }`}>
      {isSent ? <CheckCircle2 size={10} /> : <XCircle size={10} />}
      {status}
    </div>
  );
}


function LinkedInMessageCard({
  title,
  message,
  copyKey,
  copied,
  onCopy,
}: {
  title: string;
  message: string;
  copyKey: string;
  copied: string | null;
  onCopy: (text: string, key: string) => void;
}) {
  return (
    <div className="glass-card p-6 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Linkedin size={16} className="text-primary" />
          <h2 className="text-sm font-semibold text-foreground">{title}</h2>
        </div>
        <button
          onClick={() => onCopy(message, copyKey)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-all"
        >
          {copied === copyKey ? <CheckCircle2 size={12} className="text-status-online" /> : <Copy size={12} />}
          {copied === copyKey ? "Copied!" : "Copy"}
        </button>
      </div>
      <div className="rounded-xl border border-border/60 bg-muted/30 p-4 text-sm text-foreground/85 leading-relaxed">
        {message}
      </div>
    </div>
  );
}

function ChannelBadge({ channel }: { channel: "Email" | "Call" | "LinkedIn" }) {
  // console.log("Rendering ChannelBadge for:", channel); // Debug log
  const icons = { Email: Mail, Call: Phone, LinkedIn: Linkedin };
  const Icon = icons[channel] || Mail; // Fallback to Mail
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full btn-gradient text-white text-xs font-semibold">
      <Icon size={13} />
      {channel}
    </div>
  );
}

function EmptyState({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-80 space-y-3 text-center">
      {icon}
      <h2 className="text-lg font-semibold text-foreground">{title}</h2>
      <p className="text-sm text-muted-foreground max-w-xs">{description}</p>
    </div>
  );
}
