"use client";

import { useState, type ReactNode } from "react";
import { PanelLeftClose, PanelLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ToolLayoutProps {
  configPanel: ReactNode;
  children: ReactNode;
  /** Width of config panel on desktop (default: 360px) */
  configWidth?: number;
}

export function ToolLayout({
  configPanel,
  children,
  configWidth = 360,
}: ToolLayoutProps) {
  const [configCollapsed, setConfigCollapsed] = useState(false);

  return (
    <div
      className={cn(
        "grid gap-6",
        configCollapsed
          ? "grid-cols-1"
          : "grid-cols-1 lg:grid-cols-[var(--config-width)_1fr]",
      )}
      style={{ "--config-width": `${configWidth}px` } as React.CSSProperties}
    >
      {/* Config panel */}
      <div className={cn(configCollapsed && "hidden")}>
        {configPanel}
      </div>

      {/* Results area */}
      <div className="min-w-0 space-y-6">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="hidden h-7 w-7 text-muted-foreground hover:text-foreground lg:flex"
            onClick={() => setConfigCollapsed(!configCollapsed)}
            title={configCollapsed ? "Show config panel" : "Hide config panel"}
          >
            {configCollapsed ? (
              <PanelLeft className="h-3.5 w-3.5" />
            ) : (
              <PanelLeftClose className="h-3.5 w-3.5" />
            )}
          </Button>
        </div>
        {children}
      </div>
    </div>
  );
}
