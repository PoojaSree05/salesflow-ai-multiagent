import { useState, useEffect } from "react";
import { AppSidebar } from "@/components/layout/AppSidebar";
import { DashboardPage } from "@/pages/DashboardPage";
import { CampaignsPage } from "@/pages/CampaignsPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { LeadsPage } from "@/pages/LeadsPage";
import { runStrategy } from "@/lib/api";
import { Sun, Moon, Menu, X } from "lucide-react";
import { useTheme } from "@/hooks/use-theme";
import type { StrategyResult, PipelineStatus } from "@/types/strategy";

type Page = "dashboard" | "campaigns" | "settings" | "leads";

const Index = () => {
  const [currentPage, setCurrentPage] = useState<Page>("dashboard");
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus>("idle");
  const [result, setResult] = useState<StrategyResult | null>(null);
  const [pendingResult, setPendingResult] = useState<StrategyResult | null>(null);
  const [animationFinished, setAnimationFinished] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();

  const handleRunStrategy = async (input: string, campaignMode: "single" | "multi") => {
    setPipelineStatus("loading");
    setResult(null);
    setPendingResult(null);
    setAnimationFinished(false);
    setErrorMessage(null);

    try {
      const data = await runStrategy(input, campaignMode);
      setPendingResult(data);

      // If animation already finished, proceed to success
      // Use setAnimationFinished callback to get latest state if possible, 
      // but in async await, we can check the state variable directly.
      // However, React state is async. Let's use a ref or just rely on handleAnimationComplete for the most part.
    } catch (err) {
      console.error("Strategy pipeline error:", err);
      const msg = err instanceof Error ? err.message : "The agent pipeline encountered an unexpected error.";
      setErrorMessage(msg.includes("Failed to fetch") ? "Cannot reach backend. Is it running on port 8000?" : msg);
      setPipelineStatus("error");
    }
  };

  // Using a useEffect to watch both pendingResult and animationFinished is safer
  useEffect(() => {
    if (pendingResult && animationFinished && pipelineStatus === "loading") {
      setResult(pendingResult);
      setPipelineStatus("success");

      // Automatically navigate to campaigns page after success
      const timer = setTimeout(() => {
        setCurrentPage("campaigns");
      }, 2500); // Give user 2.5s to see the success state on dashboard
      return () => clearTimeout(timer);
    }
  }, [pendingResult, animationFinished, pipelineStatus]);

  const handleAnimationComplete = () => {
    setAnimationFinished(true);
  };

  const renderPage = () => {
    switch (currentPage) {
      case "dashboard":
        return (
          <DashboardPage
            onRun={handleRunStrategy}
            pipelineStatus={pipelineStatus}
            result={result}
            errorMessage={errorMessage}
            onAnimationComplete={handleAnimationComplete}
          />
        );
      case "campaigns":
        return <CampaignsPage />;
      case "leads":
        return <LeadsPage />;
      case "settings":
        return <SettingsPage />;
    }
  };

  return (
    <div className="min-h-screen flex bg-background">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar – desktop always visible, mobile as drawer */}
      <div
        className={`fixed lg:static inset-y-0 left-0 z-50 transition-transform duration-300 lg:translate-x-0 ${sidebarOpen ? "translate-x-0" : "-translate-x-full"
          }`}
      >
        <AppSidebar
          currentPage={currentPage}
          onNavigate={(page) => {
            setCurrentPage(page);
            setSidebarOpen(false);
          }}
        />
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="sticky top-0 z-30 h-14 border-b border-border/60 bg-background/80 backdrop-blur-md">
          <div className="w-full px-4 sm:px-6 lg:px-8 h-full flex items-center justify-between">
            {/* Mobile menu toggle */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden flex items-center justify-center w-9 h-9 rounded-lg border border-border text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-all"
            >
              {sidebarOpen ? <X size={17} /> : <Menu size={17} />}
            </button>

            {/* Page title – desktop */}
            <div className="hidden lg:block">
              <p className="text-xs text-muted-foreground capitalize font-bold tracking-[0.15em] opacity-80">
                {currentPage}
              </p>
            </div>

            {/* Right side */}
            <div className="flex items-center gap-2">
              <button
                onClick={toggleTheme}
                aria-label="Toggle theme"
                className="flex items-center justify-center w-9 h-9 rounded-lg border border-border bg-card text-muted-foreground hover:text-foreground hover:bg-muted transition-all duration-200 hover:scale-105"
              >
                {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
              </button>
            </div>
          </div>
        </header>

        {/* Hero gradient overlay */}
        <div
          className="fixed inset-0 pointer-events-none -z-10"
          style={{
            background:
              "radial-gradient(ellipse 80% 40% at 50% -10%, hsl(224 71% 50% / 0.06), transparent)",
          }}
        />

        {/* Page content */}
        <main className="flex-1 px-4 sm:px-6 lg:px-8 py-6 w-full">
          {renderPage()}
        </main>

        {/* Footer */}
        <footer className="px-6 py-4 border-t border-border/40 text-center">
          <p className="text-[11px] text-muted-foreground">
            Powered by LangGraph · Multi-Agent Architecture · AI-Driven Sales Automation
          </p>
        </footer>
      </div>
    </div>
  );
};

export default Index;
