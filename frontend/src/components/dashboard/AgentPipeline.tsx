import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { ChevronRight, Sparkles, Activity, Target, Zap, Bot, CheckCircle2 } from "lucide-react";
import { ClassificationCard, IcpCard, ChannelCard } from "./AgentCards";
import { ExecutionCard } from "./ExecutionCard";
import type { StrategyResult, PipelineStatus } from "@/types/strategy";

interface AgentPipelineProps {
  result: StrategyResult | null;
  status: PipelineStatus;
  errorMessage: string | null;
  onAnimationComplete?: () => void;
}

export function AgentPipeline({ result, status, errorMessage, onAnimationComplete }: AgentPipelineProps) {
  const [activeStep, setActiveStep] = useState(-1);
  const [showFullSweep, setShowFullSweep] = useState(false);

  useEffect(() => {
    if (status === "loading") {
      setShowFullSweep(false);
      setActiveStep(0);
      // Sequential activation matches ExecutionOverlay timing
      const timer = setInterval(() => {
        setActiveStep((prev) => {
          if (prev < 3) return prev + 1;
          clearInterval(timer);
          return prev;
        });
      }, 1000); // 1s per step for professional feel
      return () => clearInterval(timer);
    } else if (status === "success") {
      setActiveStep(4);
      setShowFullSweep(true);
      const timer = setTimeout(() => setShowFullSweep(false), 2000);
      return () => clearTimeout(timer);
    } else {
      setActiveStep(-1);
      setShowFullSweep(false);
    }
  }, [status]);

  const getCardStatus = (index: number): PipelineStatus => {
    if (status === "idle") return "idle";
    if (status === "error") return "error";
    if (status === "success") return "success";

    if (activeStep > index) return "success";
    if (activeStep === index) return "loading";
    return "idle";
  };

  const statuses = [0, 1, 2, 3].map(getCardStatus);

  return (
    <div className="space-y-8 py-4">
      {/* Horizontal Stepper (always present) */}
      <PipelineStepper status={status} />

      {/* Vertical Execution Overlay (Modal) */}
      <ExecutionOverlay status={status} onComplete={onAnimationComplete} />

      {/* Main Orchestrator Interface */}
      <div className="pipeline-orchestrator-container animate-fade-in w-full overflow-hidden relative">
        {/* Success Sweep Overlay */}
        {showFullSweep && (
          <div className="absolute inset-0 z-50 pointer-events-none overflow-hidden rounded-[2.5rem]">
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent skew-x-12 animate-sweep" />
          </div>
        )}

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-2xl bg-primary/10 border border-primary/20 text-primary shadow-inner">
              <Bot size={20} />
            </div>
            <div>
              <h2 className="text-lg font-bold text-foreground tracking-tight">AI Agent Orchestrator</h2>
              <p className="text-[10px] text-muted-foreground/80 font-medium tracking-tight">Neural nodes collaborating in real-time</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {status === "idle" && (
              <span className="text-[10px] uppercase tracking-widest text-muted-foreground/50 font-bold bg-muted/20 px-4 py-1.5 rounded-full border border-border/30 italic">Awaiting Activation</span>
            )}
            {status === "loading" && <ProcessingMessages />}
            {status === "success" && (
              <div className="flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-status-online/10 border border-status-online/30 text-status-online animate-fade-in shadow-sm">
                <CheckCircle2 size={13} />
                <span className="text-[10px] uppercase tracking-widest font-extrabold">Nodes Synchronized</span>
              </div>
            )}
            {status === "error" && (
              <span className="text-[10px] uppercase tracking-widest text-status-error font-extrabold bg-status-error/10 px-4 py-1.5 rounded-full border border-status-error/30">System Error</span>
            )}
          </div>
        </div>

        {/* Error alert */}
        {status === "error" && errorMessage && (
          <div className="mb-10 flex items-center gap-4 px-6 py-4 rounded-[1.5rem] border border-destructive/30 bg-destructive/5 text-destructive text-sm animate-fade-in backdrop-blur-md shadow-lg shadow-destructive/5">
            <div className="p-2 rounded-xl bg-destructive/10">
              <Activity size={18} />
            </div>
            <div className="flex-1">
              <p className="font-bold tracking-tight">Pipeline Exception</p>
              <p className="text-xs opacity-70 font-medium">{errorMessage}</p>
            </div>
          </div>
        )}

        {/* Responsive Grid - No Scrollbar */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 items-stretch">
          {/* Classification Card */}
          <div className={`relative min-w-0 transition-all duration-500 ${statuses[0] === "loading" ? "agent-active-glow rounded-[1.25rem] scale-[1.02] z-10" : ""}`}>
            <ClassificationCard data={result?.classification} status={statuses[0]} />
            <div className="hidden lg:flex absolute -right-5 top-1/2 -translate-y-1/2 z-20 pointer-events-none">
              <PipelineConnector active={statuses[0] === "success" || statuses[1] === "loading"} />
            </div>
          </div>

          {/* ICP Card */}
          <div className={`relative min-w-0 transition-all duration-500 ${statuses[1] === "loading" ? "agent-active-glow rounded-[1.25rem] scale-[1.02] z-10" : ""}`}>
            <IcpCard data={result?.icp} status={statuses[1]} />
            <div className="hidden lg:flex absolute -right-5 top-1/2 -translate-y-1/2 z-20 pointer-events-none">
              <PipelineConnector active={statuses[1] === "success" || statuses[2] === "loading"} />
            </div>
          </div>

          {/* Channel Card */}
          <div className={`relative min-w-0 transition-all duration-500 ${statuses[2] === "loading" ? "agent-active-glow rounded-[1.25rem] scale-[1.02] z-10" : ""}`}>
            <ChannelCard
              data={result?.channel}
              status={statuses[2]}
              fullReasoning={result?.channel_reasoning}
              urgency={result?.classification?.urgency}
              engagementScore={result?.icp?.engagementScore}
              icpPriority={result?.icp?.priorityLevel}
            />
            <div className="hidden lg:flex absolute -right-5 top-1/2 -translate-y-1/2 z-20 pointer-events-none">
              <PipelineConnector active={statuses[2] === "success" || statuses[3] === "loading"} />
            </div>
          </div>

          {/* Execution Card */}
          <div className={`min-w-0 transition-all duration-500 ${statuses[3] === "loading" ? "agent-active-glow rounded-[1.25rem] scale-[1.02] z-10" : ""}`}>
            <ExecutionCard data={result?.execution} status={statuses[3]} icp={result?.icp} emailAutoSent={(result as { emailAutoSent?: boolean })?.emailAutoSent} />
          </div>
        </div>
      </div>
    </div>
  );
}

function PipelineStepper({ status }: { status: PipelineStatus }) {
  const [activeStep, setActiveStep] = useState(-1);
  const [isComplete, setIsComplete] = useState(false);
  const [showSweep, setShowSweep] = useState(false);

  const steps = [
    { label: "Classification", icon: <Activity size={14} /> },
    { label: "ICP Analysis", icon: <Target size={14} /> },
    { label: "Channel Decision", icon: <Zap size={14} /> },
    { label: "Execution", icon: <Bot size={14} /> },
  ];

  useEffect(() => {
    if (status === "loading") {
      setIsComplete(false);
      setShowSweep(false);
      setActiveStep(0);
      const interval = setInterval(() => {
        setActiveStep((prev) => (prev < 3 ? prev + 1 : prev));
      }, 1000);
      return () => clearInterval(interval);
    } else if (status === "success") {
      setShowSweep(true);
      const timer = setTimeout(() => {
        setIsComplete(true);
        setActiveStep(4);
      }, 1500);
      return () => clearTimeout(timer);
    } else if (status === "idle") {
      setActiveStep(-1);
      setIsComplete(false);
      setShowSweep(false);
    }
  }, [status]);

  return (
    <div className="relative mb-2 mt-1 pb-1">
      {/* Connector Line */}
      <div className="absolute top-[18px] left-[10%] right-[10%] h-[1px] bg-border/40 -z-10" />

      {/* Sweep Animation Overlay */}
      {showSweep && (
        <div className="absolute top-0 left-0 w-full h-9 bg-status-online/5 animate-sweep -z-20 rounded-full blur-md" />
      )}

      <div className="flex justify-between items-start px-2 sm:px-10 max-w-4xl mx-auto">
        {steps.map((step, idx) => {
          const isActive = activeStep === idx;
          const isDone = activeStep > idx || isComplete;

          return (
            <div key={idx} className="flex flex-col items-center gap-2.5">
              <div
                className={`w-9 h-9 rounded-xl flex items-center justify-center border transition-all duration-500 ${isDone
                  ? "bg-status-online/10 border-status-online/50 text-status-online shadow-[0_0_15px_rgba(34,197,94,0.15)]"
                  : isActive
                    ? "bg-primary/20 border-primary text-primary animate-pulse shadow-[0_0_15px_rgba(79,70,229,0.2)]"
                    : "bg-muted/40 border-border/40 text-muted-foreground"
                  }`}
              >
                {isDone ? <CheckCircle2 size={16} strokeWidth={2.5} /> : step.icon}
              </div>
              <span
                className={`text-[10px] font-bold uppercase tracking-[0.1em] transition-colors duration-300 ${isDone
                  ? "text-status-online"
                  : isActive
                    ? "text-primary"
                    : "text-muted-foreground/50"
                  }`}
              >
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function PipelineConnector({ active }: { active?: boolean }) {
  return (
    <div className={`pipeline-connector ${active ? 'pipeline-connector-active' : ''}`}>
      <div className="pipeline-connector-dot" />
      <div className="pipeline-connector-dot !delay-700" style={{ animationDelay: '0.7s' }} />
      <div className="pipeline-connector-dot !delay-1000" style={{ animationDelay: '1.4s' }} />
    </div>
  );
}

function ProcessingMessages() {
  const messages = [
    "Analyzing lead signals...",
    "Selecting optimal channel...",
    "Generating personalized content...",
    "Finalizing campaign..."
  ];

  const [index, setIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((prev) => (prev < messages.length - 1 ? prev + 1 : prev));
    }, 1200); // 1.2s per step for better readability
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex items-center gap-2 ml-1">
      <div className="flex items-center justify-center w-4 h-4 rounded-full bg-primary/10 text-primary animate-pulse shrink-0">
        <Sparkles size={10} />
      </div>
      <div key={messages[index]} className="flex items-center gap-2 animate-fade-in">
        <span className="text-xs font-semibold text-primary/90">
          — {messages[index]}
        </span>
        <div className="flex gap-0.5">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-1 h-1 rounded-full bg-primary/40 animate-bounce"
              style={{ animationDelay: `${i * 150}ms` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function ExecutionOverlay({ status, onComplete }: { status: PipelineStatus; onComplete?: () => void }) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [showSweep, setShowSweep] = useState(false);

  const steps = [
    { label: "Classification", desc: "Analyzing intent and business domain", icon: <Activity size={18} /> },
    { label: "ICP Analysis", desc: "Profiling target and calculating fit", icon: <Target size={18} /> },
    { label: "Channel Decision", desc: "Selecting optimal outreach pathway", icon: <Zap size={18} /> },
    { label: "Execution", desc: "Generating content and launching campaign", icon: <Bot size={18} /> },
  ];

  useEffect(() => {
    if (status === "loading") {
      setIsOpen(true);
      setIsComplete(false);
      setShowSweep(false);
      setActiveStep(0);

      const interval = setInterval(() => {
        setActiveStep((prev) => {
          if (prev < 3) return prev + 1;
          clearInterval(interval);
          // When we reach the last step (Execution), wait a bit then complete
          setTimeout(() => {
            if (onComplete) onComplete();
          }, 800);
          return 3;
        });
      }, 1000);

      return () => clearInterval(interval);
    } else if (status === "success" && isOpen) {
      setShowSweep(true);
      const timer = setTimeout(() => {
        setIsComplete(true);
        setActiveStep(4);

        // Auto-close after 1.5s of success
        setTimeout(() => {
          setIsOpen(false);
        }, 1500);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (status === "idle" || status === "error") {
      setIsOpen(false);
    }
  }, [status, isOpen]);

  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      {/* Blurred Backdrop */}
      <div className="absolute inset-0 bg-background/60 backdrop-blur-md animate-fade-in" />

      {/* Modal Content */}
      <div className="relative glass-card w-full max-w-lg overflow-hidden p-8 animate-scale-in flex flex-col gap-8 shadow-2xl border-white/10">

        {/* Success Sweep Bar */}
        {showSweep && (
          <div className="absolute top-0 left-0 w-full h-[3px] bg-status-online shadow-[0_0_15px_rgba(34,197,94,0.5)] animate-sweep" />
        )}

        <div className="space-y-1.5">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-[10px] font-bold uppercase tracking-widest">
            <Sparkles size={12} className="animate-pulse" />
            Agent Orchestrator
          </div>
          <h2 className="text-2xl font-bold text-foreground">Running Multi-Agent Orchestration</h2>
          <p className="text-sm text-muted-foreground">Collaborating across specialized AI agents to optimize your strategy.</p>
        </div>

        {/* Vertical Stepper */}
        <div className="space-y-6">
          {steps.map((step, idx) => {
            const isActive = activeStep === idx;
            const isDone = activeStep > idx || isComplete;

            return (
              <div key={idx} className="flex gap-4 group">
                <div className="relative flex flex-col items-center">
                  <div
                    className={`w-10 h-10 rounded-2xl flex items-center justify-center border transition-all duration-500 z-10 ${isDone
                      ? "bg-status-online/10 border-status-online/50 text-status-online shadow-[0_0_15px_rgba(34,197,94,0.1)]"
                      : isActive
                        ? "bg-primary border-primary text-white shadow-[0_0_20px_rgba(79,70,229,0.3)] scale-110"
                        : "bg-muted/30 border-border/40 text-muted-foreground"
                      }`}
                  >
                    {isDone ? <CheckCircle2 size={18} strokeWidth={2.5} /> : step.icon}
                  </div>
                  {idx < steps.length - 1 && (
                    <div className={`w-0.5 flex-1 my-1 transition-colors duration-500 ${isDone ? "bg-status-online/40" : "bg-border/20"}`} />
                  )}
                </div>

                <div className="flex-1 py-1">
                  <h3 className={`text-sm font-bold transition-colors duration-300 ${isDone ? "text-status-online" : isActive ? "text-primary" : "text-muted-foreground"}`}>
                    {step.label}
                  </h3>
                  <p className={`text-xs transition-colors duration-300 ${isDone ? "text-status-online/70" : isActive ? "text-muted-foreground" : "text-muted-foreground/40"}`}>
                    {step.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Status Message Footer */}
        <div className="pt-2">
          {isComplete ? (
            <div className="flex items-center justify-center gap-3 py-3 px-4 rounded-xl bg-status-online/5 border border-status-online/20 text-status-online animate-fade-in">
              <CheckCircle2 size={18} />
              <span className="text-sm font-bold">All agents completed successfully.</span>
            </div>
          ) : (
            <div className="flex items-center justify-center gap-3 py-2 text-muted-foreground italic text-xs">
              <div className="flex gap-1">
                <span className="w-1 h-1 rounded-full bg-primary animate-bounce delay-0" />
                <span className="w-1 h-1 rounded-full bg-primary animate-bounce delay-150" />
                <span className="w-1 h-1 rounded-full bg-primary animate-bounce delay-300" />
              </div>
              <span className="ml-1">Orchestrating specialized workflows...</span>
            </div>
          )}
        </div>
      </div>
    </div>,
    document.body
  );
}

