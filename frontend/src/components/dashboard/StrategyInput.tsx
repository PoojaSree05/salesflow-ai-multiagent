import { useState } from "react";
import { Sparkles, Loader2, Target, Globe } from "lucide-react";

interface StrategyInputProps {
  onRun: (input: string, campaignMode: "single" | "multi") => void;
  isLoading: boolean;
}

export function StrategyInput({ onRun, isLoading }: StrategyInputProps) {
  const [input, setInput] = useState("");
  const [campaignMode, setCampaignMode] = useState<"single" | "multi">("single");

  const handleSubmit = () => {
    if (!input.trim() || isLoading) return;
    // Current execution logic remains unchanged, state is stored but not passed to backend yet
    onRun(input.trim(), campaignMode);
  };

  return (
    <div className="glass-card p-6 space-y-6">
      {/* Card header */}
      <div className="flex items-center gap-2">
        <div className="flex items-center justify-center w-7 h-7 rounded-lg btn-gradient">
          <Sparkles size={14} className="text-white" />
        </div>
        <div>
          <h2 className="text-sm font-semibold text-foreground">Strategy Input</h2>
          <p className="text-xs text-muted-foreground">Define your target to activate the agent pipeline</p>
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-bold text-foreground uppercase tracking-wider opacity-70">
          Target Business Description
        </label>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Example: HR Director in UK manufacturing company with high hiring urgency and strong recruitment activity."
          rows={4}
          disabled={isLoading}
          className="w-full resize-none rounded-lg border border-border bg-background/60 px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary/60 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-sans"
        />
      </div>

      {/* Campaign Mode Selector */}
      <div className="space-y-3 pt-2">
        <label className="text-xs font-bold text-foreground uppercase tracking-wider opacity-70">
          Campaign Mode
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <label className={`relative flex items-center gap-3 p-3.5 rounded-xl border cursor-pointer transition-all duration-300 group ${campaignMode === 'single'
            ? 'border-primary/40 bg-primary/5 shadow-[0_0_15px_-5px_hsl(var(--primary)/0.2)]'
            : 'border-border/40 bg-muted/10 hover:border-border/80'
            }`}>
            <input
              type="radio"
              name="campaignMode"
              value="single"
              checked={campaignMode === 'single'}
              onChange={() => setCampaignMode('single')}
              className="sr-only"
            />
            <div className={`flex items-center justify-center w-5 h-5 rounded-full border-2 transition-all duration-300 ${campaignMode === 'single' ? 'border-primary bg-primary shadow-[0_0_8px_hsl(var(--primary)/0.6)]' : 'border-muted-foreground/30'
              }`}>
              {campaignMode === 'single' && <div className="w-1.5 h-1.5 rounded-full bg-white scale-110 animate-in zoom-in duration-300" />}
            </div>
            <div className="flex flex-col">
              <span className={`text-xs font-bold transition-colors ${campaignMode === 'single' ? 'text-foreground' : 'text-muted-foreground'}`}>
                Single Target
              </span>
              <span className="text-[10px] text-muted-foreground/70 font-medium">
                Send to Top ICP
              </span>
            </div>
            {campaignMode === 'single' && (
              <div className="absolute right-3 text-primary/30">
                <Target size={14} />
              </div>
            )}
          </label>

          <label className={`relative flex items-center gap-3 p-3.5 rounded-xl border cursor-pointer transition-all duration-300 group ${campaignMode === 'multi'
            ? 'border-primary/40 bg-primary/5 shadow-[0_0_15px_-5px_hsl(var(--primary)/0.2)]'
            : 'border-border/40 bg-muted/10 hover:border-border/80'
            }`}>
            <input
              type="radio"
              name="campaignMode"
              value="multi"
              checked={campaignMode === 'multi'}
              onChange={() => setCampaignMode('multi')}
              className="sr-only"
            />
            <div className={`flex items-center justify-center w-5 h-5 rounded-full border-2 transition-all duration-300 ${campaignMode === 'multi' ? 'border-primary bg-primary shadow-[0_0_8px_hsl(var(--primary)/0.6)]' : 'border-muted-foreground/30'
              }`}>
              {campaignMode === 'multi' && <div className="w-1.5 h-1.5 rounded-full bg-white scale-110 animate-in zoom-in duration-300" />}
            </div>
            <div className="flex flex-col">
              <span className={`text-xs font-bold transition-colors ${campaignMode === 'multi' ? 'text-foreground' : 'text-muted-foreground'}`}>
                Multi-Lead Campaign
              </span>
              <span className="text-[10px] text-muted-foreground/70 font-medium">
                Send to Multiple Matched ICPs
              </span>
            </div>
            {campaignMode === 'multi' && (
              <div className="absolute right-3 text-primary/30">
                <Globe size={14} />
              </div>
            )}
          </label>
        </div>
      </div>

      <div className="pt-2">
        <button
          onClick={handleSubmit}
          disabled={isLoading || !input.trim()}
          className="btn-gradient w-full sm:w-auto flex items-center justify-center gap-2 px-7 py-3 rounded-xl text-sm disabled:transform-none"
        >
          {isLoading ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              <span>Orchestrating Agents…</span>
            </>
          ) : (
            <>
              <Sparkles size={16} />
              <span>Run Multi-Agent Strategy</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
