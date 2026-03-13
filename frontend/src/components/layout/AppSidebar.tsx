import { LayoutDashboard, Send, BarChart2, Settings, Bot, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

type Page = "dashboard" | "campaigns" | "settings" | "leads";

interface AppSidebarProps {
  currentPage: Page;
  onNavigate: (page: Page) => void;
}

const navItems: { id: Page; label: string; icon: React.ElementType; description: string }[] = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard, description: "Agent pipeline & strategy" },
  { id: "campaigns", label: "Campaigns", icon: Send, description: "Email, LinkedIn & Call content" },
  { id: "leads", label: "Leads", icon: BarChart2, description: "Classified ICP leads & channels" },
  { id: "settings", label: "Settings", icon: Settings, description: "Sender & model config" },
];

export function AppSidebar({ currentPage, onNavigate }: AppSidebarProps) {
  return (
    <aside className="sidebar-shell flex flex-col w-72 min-h-screen border-r border-border/60 bg-card/50 backdrop-blur-md flex-shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-4 px-6 py-6 border-b border-border/60">
        <div className="flex items-center justify-center w-10 h-10 rounded-xl btn-gradient flex-shrink-0 shadow-lg shadow-primary/20">
          <Bot size={22} className="text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight text-foreground leading-none">
            SalesFlow <span className="text-gradient">AI</span>
          </h1>
          <p className="text-[11px] text-muted-foreground mt-1 leading-tight font-medium uppercase tracking-wider">Orchestrator</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-8 flex flex-col gap-1.5">
        <p className="text-[11px] uppercase tracking-[0.2em] text-muted-foreground px-3 mb-4 font-bold">
          Navigation
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={cn(
                "w-full flex items-center gap-4 px-4 py-3.5 rounded-xl text-left transition-all duration-300 group relative",
                isActive
                  ? "bg-primary/10 text-primary border border-primary/20 shadow-sm"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted/80 border border-transparent"
              )}
            >
              <Icon
                size={20}
                className={cn(
                  "flex-shrink-0 transition-colors",
                  isActive ? "text-primary scale-110" : "text-muted-foreground group-hover:text-foreground"
                )}
              />
              <div className="flex-1 min-w-0">
                <p className={cn("text-base font-semibold leading-none", isActive ? "text-primary" : "")}>{item.label}</p>
                <p className="text-[11px] text-muted-foreground mt-1.5 truncate font-medium opacity-80">{item.description}</p>
              </div>
              {isActive && (
                <>
                  <ChevronRight size={16} className="text-primary/60 flex-shrink-0" />
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-primary rounded-l-full" />
                </>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-6 py-6 border-t border-border/60">
        <div className="badge-online inline-flex items-center gap-2 text-[11px] font-bold">
          <span className="w-2 h-2 rounded-full bg-status-online animate-pulse shadow-[0_0_8px_hsl(var(--status-online))]" />
          SYSTEM ONLINE
        </div>
        <p className="text-[11px] text-muted-foreground mt-3 leading-relaxed font-medium">
          Powered by LangGraph Agentic Framework
        </p>
      </div>
    </aside>
  );
}
