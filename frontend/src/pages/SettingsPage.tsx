import { useState } from "react";
import { Settings, Mail, Server, CheckCircle2, Eye, EyeOff } from "lucide-react";

export function SettingsPage() {
  const [senderEmail] = useState("pcoswomenscare@gmail.com");
  const [smtpHost, setSmtpHost] = useState("smtp.gmail.com");
  const [smtpPort, setSmtpPort] = useState("587");
  const [smtpUser, setSmtpUser] = useState("");
  const [smtpPass, setSmtpPass] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    // Placeholder: would POST to backend settings endpoint
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-2xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">Configure sender credentials and outreach model preferences.</p>
      </div>

      {/* Sender Email */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-center gap-2">
          <Mail size={16} className="text-primary" />
          <h2 className="text-sm font-semibold text-foreground">Sender Identity</h2>
        </div>
        <div className="space-y-2">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Sender Email Address</label>
          <input
            type="email"
            value={senderEmail}
            disabled
            placeholder="you@yourdomain.com"
            className="w-full rounded-lg border border-border bg-background/60 px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary/60 transition-all opacity-50 cursor-not-allowed"
          />
          <p className="text-[11px] text-muted-foreground">This will appear as the "From" address in outreach emails.</p>
        </div>
      </div>

      {/* SMTP Configuration */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-center gap-2">
          <Server size={16} className="text-primary" />
          <h2 className="text-sm font-semibold text-foreground">SMTP Configuration</h2>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2 col-span-2 sm:col-span-1">
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">SMTP Host</label>
            <input
              type="text"
              value={smtpHost}
              onChange={(e) => setSmtpHost(e.target.value)}
              placeholder="smtp.gmail.com"
              className="w-full rounded-lg border border-border bg-background/60 px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary/60 transition-all"
            />
          </div>
          <div className="space-y-2 col-span-2 sm:col-span-1">
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">SMTP Port</label>
            <input
              type="text"
              value={smtpPort}
              onChange={(e) => setSmtpPort(e.target.value)}
              placeholder="587"
              className="w-full rounded-lg border border-border bg-background/60 px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary/60 transition-all"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">SMTP Username</label>
          <input
            type="text"
            value={smtpUser}
            onChange={(e) => setSmtpUser(e.target.value)}
            placeholder="your-email@gmail.com"
            className="w-full rounded-lg border border-border bg-background/60 px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary/60 transition-all"
          />
        </div>

        <div className="space-y-2">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">SMTP Password / App Token</label>
          <div className="relative">
            <input
              type={showPass ? "text" : "password"}
              value={smtpPass}
              onChange={(e) => setSmtpPass(e.target.value)}
              placeholder="••••••••••••"
              className="w-full rounded-lg border border-border bg-background/60 px-4 py-2.5 pr-10 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary/60 transition-all"
            />
            <button
              type="button"
              onClick={() => setShowPass(!showPass)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
            >
              {showPass ? <EyeOff size={15} /> : <Eye size={15} />}
            </button>
          </div>
          <p className="text-[11px] text-muted-foreground">For Gmail, use an App Password. Never use your main password.</p>
        </div>
      </div>

      {/* Save button */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleSave}
          className="btn-gradient flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm"
        >
          <Settings size={14} />
          Save Settings
        </button>
        {saved && (
          <div className="flex items-center gap-1.5 text-sm text-status-online animate-fade-in">
            <CheckCircle2 size={15} />
            Settings saved!
          </div>
        )}
      </div>
    </div>
  );
}
