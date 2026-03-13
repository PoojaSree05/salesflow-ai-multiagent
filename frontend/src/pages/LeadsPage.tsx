import { useEffect, useSyncExternalStore } from "react";
import {
  loadLeads,
  invalidateLeadsStore,
  subscribeLeadsStore,
  getLeadsStoreSnapshot,
} from "@/lib/leadsStore";
import {
  Users,
  RefreshCw,
  Target,
  TrendingUp,
  Mail,
  MapPin,
  Building2,
  CheckCircle2,
  Star,
  AlertCircle,
  Loader2,
  Sparkles,
  ArrowRight,
} from "lucide-react";

export function LeadsPage() {
  // Subscribe to global store — re-renders automatically on store updates
  const store = useSyncExternalStore(subscribeLeadsStore, getLeadsStoreSnapshot);
  const { leads, totalQualified, hasRuns, status, error, lastFetchedAt } = store;

  // Fetch on mount (uses cache if available)
  useEffect(() => {
    loadLeads(false);
  }, []);

  const handleRefresh = () => {
    invalidateLeadsStore();
    loadLeads(true);
  };

  const isLoading = status === "loading";
  const updatedAt = lastFetchedAt
    ? new Date(lastFetchedAt).toLocaleTimeString()
    : null;

  // ── Pre-run empty state ────────────────────────────────────────────────────
  if (!hasRuns && status === "ready") {
    return (
      <div className="space-y-6 animate-fade-in">
        <LeadsHeader updatedAt={updatedAt} isLoading={isLoading} onRefresh={handleRefresh} />
        <div className="flex flex-col items-center justify-center py-24 gap-6 text-center">
          <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Target size={28} />
          </div>
          <div className="max-w-sm">
            <h2 className="text-base font-bold text-foreground">No leads yet</h2>
            <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
              The Leads page shows ICP leads matched against your strategy prompt. Run the multi-agent pipeline from the Dashboard to classify and surface matching leads.
            </p>
          </div>
          <a
            href="#"
            onClick={(e) => { e.preventDefault(); window.dispatchEvent(new CustomEvent("navigate", { detail: "dashboard" })); }}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary/10 border border-primary/20 text-primary text-sm font-semibold hover:bg-primary/20 transition-colors"
          >
            Go to Dashboard <ArrowRight size={14} />
          </a>
        </div>
      </div>
    );
  }

  // ── Spinner while first load ───────────────────────────────────────────────
  if (status === "loading" && leads.length === 0) {
    return (
      <div className="space-y-6 animate-fade-in">
        <LeadsHeader updatedAt={updatedAt} isLoading={true} onRefresh={handleRefresh} />
        <div className="flex flex-col items-center justify-center py-24 gap-4">
          <Loader2 size={28} className="text-primary animate-spin" />
          <p className="text-sm text-muted-foreground">Loading matched leads…</p>
        </div>
      </div>
    );
  }

  // ── Error state ────────────────────────────────────────────────────────────
  if (status === "error") {
    return (
      <div className="space-y-6 animate-fade-in">
        <LeadsHeader updatedAt={updatedAt} isLoading={false} onRefresh={handleRefresh} />
        <div className="flex flex-col items-center justify-center py-16 gap-4 text-center">
          <AlertCircle size={28} className="text-red-400" />
          <p className="text-sm text-muted-foreground">{error}</p>
          <button
            onClick={handleRefresh}
            className="px-4 py-2 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm font-semibold hover:bg-red-500/15 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* ── Header ── */}
      <LeadsHeader updatedAt={updatedAt} isLoading={isLoading} onRefresh={handleRefresh} />

      {/* ── Stats cards ── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <StatCard
          label="ICP Matched"
          value={totalQualified}
          sub="Prompt-matched leads"
          accent="indigo"
          icon={<CheckCircle2 size={16} />}
        />
        <StatCard
          label="High Priority"
          value={leads.filter((l) => l.priority === "High").length}
          sub="Priority scored by ICP Agent"
          accent="emerald"
          icon={<Star size={16} />}
        />
        <StatCard
          label="Unique Companies"
          value={new Set(leads.map((l) => l.company)).size}
          sub="Across matched leads"
          accent="purple"
          icon={<Building2 size={16} />}
        />
      </div>

      {/* ── Result summary ── */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <CheckCircle2 size={13} className="text-emerald-400" />
          <span>
            Showing <span className="font-bold text-foreground">{leads.length}</span> prompt-matched ICP leads
          </span>
          <span className="text-border">·</span>
          <span className="text-[10px] text-muted-foreground/60">sorted by Priority → Match Score</span>
        </div>
      </div>

      {/* ── Lead table ── */}
      {leads.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 gap-3 text-center">
          <Users size={24} className="text-muted-foreground/40" />
          <p className="text-sm text-muted-foreground">No leads matched. Try a different prompt.</p>
        </div>
      ) : (
        <div className="rounded-2xl border border-border/40 overflow-hidden">
          {/* Table head */}
          <div className="grid grid-cols-[auto_1fr_1fr_auto_auto_auto] gap-x-4 px-4 py-3 border-b border-border/40 bg-muted/10 text-[10px] uppercase tracking-widest text-muted-foreground font-bold">
            <span>#</span>
            <span className="flex items-center gap-1"><Users size={10} /> Lead</span>
            <span className="flex items-center gap-1"><Building2 size={10} /> Company</span>
            <span className="flex items-center gap-1"><Mail size={10} /> Email</span>
            <span className="flex items-center gap-1"><TrendingUp size={10} /> Score</span>
            <span>Priority</span>
          </div>

          {/* Table rows */}
          <div className="divide-y divide-border/20">
            {leads.map((lead, i) => (
              <LeadRow key={lead.email || i} rank={i + 1} lead={lead} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ─── LeadsHeader ──────────────────────────────────────────────────────────────

function LeadsHeader({
  updatedAt,
  isLoading,
  onRefresh,
}: {
  updatedAt: string | null;
  isLoading: boolean;
  onRefresh: () => void;
}) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-end gap-3">
      <div className="flex-1">
        <h1 className="text-xl font-bold text-foreground">ICP Matched Leads</h1>
        <p className="text-xs text-muted-foreground mt-0.5">
          Prompt-matched · ranked by ICP Intelligence Agent
        </p>
      </div>
      <div className="flex items-center gap-3">
        {updatedAt && (
          <span className="text-[10px] text-muted-foreground/60">Updated {updatedAt}</span>
        )}
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border/50 bg-muted/10 text-xs text-muted-foreground hover:text-foreground hover:border-border hover:bg-muted/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RefreshCw size={12} className={isLoading ? "animate-spin" : ""} />
          Refresh
        </button>
      </div>
    </div>
  );
}

// ─── StatCard ─────────────────────────────────────────────────────────────────

function StatCard({
  label,
  value,
  sub,
  accent,
  icon,
}: {
  label: string;
  value: number;
  sub: string;
  accent: "indigo" | "emerald" | "purple";
  icon: React.ReactNode;
}) {
  const colors = {
    indigo: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
    emerald: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    purple: "text-purple-400 bg-purple-500/10 border-purple-500/20",
  };
  return (
    <div className="rounded-2xl border border-border/40 bg-card/30 p-4">
      <div className={`w-8 h-8 rounded-lg border flex items-center justify-center mb-3 ${colors[accent]}`}>
        {icon}
      </div>
      <div className="text-2xl font-black text-foreground">{value}</div>
      <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide mt-0.5">{label}</div>
      <div className="text-[10px] text-muted-foreground/60 mt-0.5">{sub}</div>
    </div>
  );
}

// ─── LeadRow ──────────────────────────────────────────────────────────────────

function LeadRow({ rank, lead }: { rank: number; lead: import("@/lib/api").IcpLead }) {
  return (
    <div className="grid grid-cols-[auto_1fr_1fr_auto_auto_auto] gap-x-4 px-4 py-3 items-center hover:bg-muted/5 transition-colors group">
      {/* Rank */}
      <span className="text-[11px] font-bold text-muted-foreground/50 w-5 text-right">{rank}</span>

      {/* Lead name + role */}
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-full bg-indigo-500/15 border border-indigo-500/20 flex items-center justify-center text-indigo-300 text-[11px] font-bold flex-shrink-0">
            {(lead.name || "?")[0].toUpperCase()}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-foreground leading-tight truncate">{lead.name}</p>
            <p className="text-[10px] text-muted-foreground truncate">{lead.role}</p>
          </div>
        </div>
      </div>

      {/* Company + industry */}
      <div className="min-w-0">
        <p className="text-sm font-medium text-foreground truncate">{lead.company}</p>
        <p className="text-[10px] text-muted-foreground truncate">{lead.industry}</p>
      </div>

      {/* Email */}
      <div className="hidden sm:block min-w-0 max-w-[180px]">
        <a
          href={`mailto:${lead.email}`}
          className="text-[11px] text-primary/70 hover:text-primary transition-colors truncate block"
        >
          {lead.email}
        </a>
        {lead.location && (
          <div className="flex items-center gap-1 text-[10px] text-muted-foreground/60 mt-0.5">
            <MapPin size={9} />
            {lead.location}
          </div>
        )}
      </div>

      {/* Engagement + match score */}
      <div className="text-right min-w-[70px]">
        <div className="text-xs font-bold text-foreground">{lead.engagement_score}</div>
        <div className="w-16 h-1 bg-border/30 rounded-full mt-1 overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-emerald-500"
            style={{ width: `${Math.min(100, lead.engagement_score)}%` }}
          />
        </div>
      </div>

      {/* Priority badge */}
      <div>
        <span
          className={`text-[10px] font-bold px-2.5 py-1 rounded-full border ${lead.priority === "High"
              ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/25"
              : lead.priority === "Medium"
                ? "text-amber-400 bg-amber-500/10 border-amber-500/25"
                : "text-muted-foreground bg-muted/20 border-border/30"
            }`}
        >
          {lead.priority}
        </span>
      </div>
    </div>
  );
}
