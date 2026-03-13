import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { Send, CheckCircle2, Loader2, ChevronRight, X, Clock, User, Mail, MessageSquare, Phone, Linkedin, Zap } from "lucide-react";
import type { StrategyResult } from "@/types/strategy";
import type { PipelineStatus } from "@/types/strategy";
import { sendEmail } from "@/lib/api";
import { toast } from "sonner";

interface ExecutionCardProps {
  data?: StrategyResult["execution"];
  status: PipelineStatus;
  icp?: StrategyResult["icp"];
  emailAutoSent?: boolean;
}

export function ExecutionCard({ data, status, icp, emailAutoSent }: ExecutionCardProps) {
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [wasLoading, setWasLoading] = useState(false);

  useEffect(() => {
    if (status === "loading") {
      setWasLoading(true);
    }
  }, [status]);

  useEffect(() => {
    // Auto-open review modal ONLY when transitioning from loading to success
    // This prevents the modal from reopening when navigating back to the dashboard
    if (status === "success" && wasLoading && !sent && !sending && !showReviewModal) {
      if (data?.type === "Email" || data?.type === "Call" || data?.type === "LinkedIn") {
        setShowReviewModal(true);
        setWasLoading(false); // Reset to prevent multiple triggers
      }
    }
  }, [status, wasLoading, data?.type, sent, sending, showReviewModal]);

  const handleSend = async () => {
    if (!data || data.type !== "Email") return;
    setSending(true);
    setSendError(null);
    setShowReviewModal(false);
    try {
      await sendEmail({
        subject: data.subject,
        body: data.body,
        recipient: icp?.email ?? "prospect@example.com",
      });
      setSent(true);
      toast.success("Email sent successfully.");
    } catch {
      setSendError("Failed to send email. Please try again.");
      toast.error("Failed to send email.");
    } finally {
      setSending(false);
    }
  };

  return (
    <>
      <div className={`glass-card p-6 flex flex-col gap-5 min-w-0 w-full animate-slide-in agent-card-4 ${status === "loading" ? "opacity-80" : ""}`}>
        {/* Header */}
        <div className="flex items-center justify-between pb-2 border-b border-border/40">
          <div className="flex items-center gap-3">
            <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-primary/10 text-primary font-mono border border-primary/20">A4</span>
            <h3 className="text-sm font-bold text-foreground leading-tight tracking-tight">Execution Agent</h3>
          </div>
          <span
            className={`status-dot scale-125 ${status === "success" ? "status-dot-success" : status === "loading" ? "status-dot-loading" : "status-dot-idle"
              }`}
          />
        </div>

        {/* States */}
        {status === "idle" && (
          <p className="text-[11px] text-muted-foreground/60 italic text-center py-4">Awaiting activation…</p>
        )}

        {status === "loading" && (
          <div className="space-y-2">
            {[80, 65, 90, 55, 75].map((w, i) => (
              <div key={i} className="skeleton-pulse h-3 rounded" style={{ width: `${w}%` }} />
            ))}
          </div>
        )}

        {status === "success" && data && (
          <>
            {data.type === "Email" && (
              <div className="space-y-3">
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">Subject</p>
                  <p className="text-xs font-bold text-foreground leading-snug">{data.subject}</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">Body</p>
                  <div className="max-h-36 overflow-y-auto rounded-lg border border-border/50 bg-muted/40 p-3 text-[11px] text-foreground/80 leading-relaxed whitespace-pre-wrap font-sans scrollbar-thin">
                    {data.body}
                  </div>
                </div>
                <div className="flex items-center gap-2 px-3 py-2 rounded-lg border border-primary/30 bg-primary/5">
                  <ChevronRight size={13} className="text-primary" />
                  <span className="text-xs font-semibold text-primary">{data.cta}</span>
                </div>

                {sent ? (
                  <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-status-online/10 border border-status-online/30 animate-fade-in shadow-sm shadow-status-online/5">
                    <CheckCircle2 size={14} className="text-status-online" />
                    <span className="text-xs font-bold text-status-online uppercase tracking-wider">
                      Email Sent Successfully
                    </span>
                  </div>
                ) : (
                  <button
                    onClick={() => setShowReviewModal(true)}
                    disabled={sending}
                    className="btn-gradient w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-xs disabled:transform-none select-none"
                  >
                    {sending ? (
                      <>
                        <Loader2 size={13} className="animate-spin" />
                        Sending…
                      </>
                    ) : (
                      <>
                        <Send size={13} />
                        Send Email
                      </>
                    )}
                  </button>
                )}

                {sendError && (
                  <p className="text-[11px] text-destructive text-center font-medium">{sendError}</p>
                )}
              </div>
            )}

            {data.type === "Call" && (
              <div className="space-y-3">
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">Call Script</p>
                  <div className="max-h-32 overflow-y-auto rounded-lg border border-border/50 bg-muted/40 p-3 text-[11px] text-foreground/80 leading-relaxed font-sans">
                    {data.script}
                  </div>
                </div>
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-2">Key Talking Points</p>
                  <ul className="space-y-1.5">
                    {data.keyPoints.map((point, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="flex-shrink-0 w-4 h-4 rounded-full btn-gradient flex items-center justify-center text-[9px] text-white font-bold mt-0.5">
                          {i + 1}
                        </span>
                        <span className="text-[11px] text-foreground/80">{point}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {data.type === "LinkedIn" && (
              <div className="space-y-3">
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">Connection Message</p>
                  <div className="rounded-lg border border-border/50 bg-muted/40 p-3 text-[11px] text-foreground/80 leading-relaxed">
                    {data.connectionMessage}
                  </div>
                </div>
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">Follow-up Message</p>
                  <div className="max-h-28 overflow-y-auto rounded-lg border border-border/50 bg-muted/40 p-3 text-[11px] text-foreground/80 leading-relaxed">
                    {data.followUpMessage}
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {showReviewModal && data?.type === "Email" && (
        <EmailReviewModal
          data={data}
          recipient={icp?.email ?? "prospect@example.com"}
          onCancel={() => setShowReviewModal(false)}
          onConfirm={handleSend}
        />
      )}

      {showReviewModal && (data?.type === "Call" || data?.type === "LinkedIn") && (
        <GenericExecutionModal
          data={data}
          icp={icp}
          onClose={() => setShowReviewModal(false)}
        />
      )}
    </>
  );
}

function GenericExecutionModal({
  data,
  icp,
  onClose
}: {
  data: Extract<StrategyResult["execution"], { type: "Call" | "LinkedIn" }>;
  icp?: StrategyResult["icp"];
  onClose: () => void;
}) {
  const isCall = data.type === "Call";
  const title = isCall ? "Personalized Call Script" : "LinkedIn Connection Strategy";
  const Icon = isCall ? Phone : Linkedin;

  return createPortal(
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-background/80 backdrop-blur-md animate-fade-in" onClick={onClose} />

      {/* Modal */}
      <div className="relative glass-card w-full max-w-xl overflow-hidden animate-scale-in shadow-2xl border-white/10 flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-6 pb-4 border-b border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-primary/10 text-primary">
              <Icon size={18} />
            </div>
            <div>
              <h2 className="text-xl font-bold text-foreground">{title}</h2>
              <p className="text-xs text-muted-foreground">
                {isCall ? "Tailored script for direct outreach" : "Custom message for platform engagement"}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-white/5 text-muted-foreground transition-all">
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 scrollbar-thin">
          <div className="space-y-4">
            <div className="flex gap-4">
              <div className="flex-1 space-y-1.5">
                <div className="flex items-center gap-2 text-[10px] uppercase tracking-widest text-muted-foreground font-bold">
                  <User size={12} />
                  Target Prospect
                </div>
                <div className="px-3 py-2 rounded-xl bg-muted/30 border border-border/50 text-sm font-medium text-foreground">
                  {icp?.name} — {icp?.role} at {icp?.company}
                </div>
              </div>
            </div>

            {isCall ? (
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 text-[10px] uppercase tracking-widest text-muted-foreground font-bold text-primary">
                    <CheckCircle2 size={12} />
                    Call Narrative
                  </div>
                  <div className="rounded-2xl border border-primary/20 bg-primary/5 p-5 space-y-4">
                    {(data as any).script ? (
                      <p className="text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap font-sans">
                        {(data as any).script}
                      </p>
                    ) : (
                      <div className="space-y-3">
                        <p className="text-sm text-foreground/90 italic">LLM generated call structure:</p>
                        <div className="space-y-2 text-sm text-foreground/80">
                          <p><strong>Opening:</strong> {(data as any).opening_line || "Hi, this is..."}</p>
                          <p><strong>Context:</strong> {(data as any).rapport_building}</p>
                          <p><strong>Problem:</strong> {(data as any).problem_exploration}</p>
                          <p><strong>Value:</strong> {(data as any).value_pitch}</p>
                          <p><strong>CTA:</strong> {(data as any).closing_cta}</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                {data.keyPoints && data.keyPoints.length > 0 && (
                  <div className="space-y-1.5">
                    <p className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold">Strategic Notes</p>
                    <div className="grid gap-2">
                      {data.keyPoints.map((point, i) => (
                        <div key={i} className="flex gap-2 p-2 rounded-lg bg-muted/20 border border-border/40 text-[11px] text-muted-foreground">
                          <Zap size={10} className="text-amber-500 shrink-0 mt-0.5" />
                          {point}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 text-[10px] uppercase tracking-widest text-muted-foreground font-bold">
                    <Linkedin size={12} className="text-sky-500" />
                    Connection Message
                  </div>
                  <div className="rounded-2xl border border-sky-500/20 bg-sky-500/5 p-5 text-sm text-foreground/90 leading-relaxed font-sans min-h-[100px]">
                    {data.connectionMessage}
                  </div>
                </div>
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 text-[10px] uppercase tracking-widest text-muted-foreground font-bold">
                    <MessageSquare size={12} className="text-sky-500" />
                    Follow-up Sequence
                  </div>
                  <div className="rounded-2xl border border-border/50 bg-muted/20 p-5 text-sm text-foreground/90 leading-relaxed font-sans min-h-[100px]">
                    {data.followUpMessage}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 bg-muted/10 border-t border-white/5 flex justify-end">
          <button
            onClick={onClose}
            className="px-8 py-3 rounded-xl bg-foreground text-background text-sm font-bold hover:opacity-90 transition-all"
          >
            Close Strategy
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}

function EmailReviewModal({
  data,
  recipient,
  onCancel,
  onConfirm
}: {
  data: Extract<StrategyResult["execution"], { type: "Email" }>;
  recipient: string;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  const [timeLeft, setTimeLeft] = useState(3);
  const [progress, setProgress] = useState(100);

  useEffect(() => {
    if (timeLeft <= 0) {
      onConfirm();
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft(prev => prev - 1);
    }, 1000);

    const progressTimer = setInterval(() => {
      setProgress(prev => Math.max(0, prev - (100 / (3 * 20)))); // 20 ticks per second
    }, 50);

    return () => {
      clearInterval(timer);
      clearInterval(progressTimer);
    };
  }, [timeLeft, onConfirm]);

  return createPortal(
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-background/80 backdrop-blur-md animate-fade-in" onClick={onCancel} />

      {/* Modal */}
      <div className="relative glass-card w-full max-w-xl overflow-hidden animate-scale-in shadow-2xl border-white/10 flex flex-col max-h-[90vh]">
        {/* Progress Bar */}
        <div className="absolute top-0 left-0 h-1 bg-primary transition-all duration-50" style={{ width: `${progress}%` }} />

        {/* Header */}
        <div className="p-6 pb-4 border-b border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-primary/10 text-primary">
              <Clock size={18} className="animate-pulse" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-foreground">Reviewing Email Before Sending</h2>
              <p className="text-xs text-muted-foreground">Automatic delivery in {timeLeft}s...</p>
            </div>
          </div>
          <button onClick={onCancel} className="p-2 rounded-full hover:bg-white/5 text-muted-foreground transition-all">
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 scrollbar-thin">
          <div className="space-y-4">
            <div className="flex gap-4">
              <div className="flex-1 space-y-1.5">
                <div className="flex items-center gap-2 text-[10px] uppercase tracking-widest text-muted-foreground font-bold">
                  <User size={12} />
                  Recipient
                </div>
                <div className="px-3 py-2 rounded-xl bg-muted/30 border border-border/50 text-sm font-medium text-foreground">
                  {recipient}
                </div>
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center gap-2 text-[10px] uppercase tracking-widest text-muted-foreground font-bold">
                <MessageSquare size={12} />
                Subject Line
              </div>
              <div className="px-3 py-2 rounded-xl bg-muted/30 border border-border/50 text-sm font-bold text-foreground">
                {data.subject}
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center gap-2 text-[10px] uppercase tracking-widest text-muted-foreground font-bold">
                <Mail size={12} />
                Email Content
              </div>
              <div className="rounded-2xl border border-border/50 bg-muted/20 p-5 text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap font-sans min-h-[200px]">
                {data.body}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 bg-muted/10 border-t border-white/5 flex gap-3">
          <button
            onClick={onCancel}
            className="flex-1 py-3 px-4 rounded-xl border border-border/50 text-sm font-bold text-muted-foreground hover:bg-white/5 transition-all"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="flex-[2] btn-gradient py-3 px-4 rounded-xl text-sm font-bold text-white shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-2"
          >
            <Send size={16} />
            Send Now
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
