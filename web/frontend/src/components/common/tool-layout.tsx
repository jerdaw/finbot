"use client";

import { useState, type ReactNode } from "react";
import { PanelTopClose, PanelTopOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ToolLayoutProps {
  configPanel: ReactNode;
  children: ReactNode;
  /** @deprecated ToolLayout now uses a full-width top configuration workbench. */
  configWidth?: number;
}

export function ToolLayout({
  configPanel,
  children,
}: ToolLayoutProps) {
  const [configCollapsed, setConfigCollapsed] = useState(false);

  return (
    <div className="min-w-0 space-y-5">
      {/* Config panel */}
      <div className={cn("min-w-0", configCollapsed && "hidden")}>
        {configPanel}
      </div>

      {/* Results area */}
      <div className="min-w-0 space-y-5">
        <div className="hidden min-h-8 items-center justify-end border-b border-border/40 pb-2 lg:flex">
          <Button
            variant="ghost"
            size="sm"
            className="h-7 gap-1.5 px-2 text-xs text-muted-foreground hover:text-foreground"
            onClick={() => setConfigCollapsed(!configCollapsed)}
            aria-label={configCollapsed ? "Show inputs" : "Hide inputs"}
            title={configCollapsed ? "Show inputs" : "Hide inputs"}
          >
            {configCollapsed ? (
              <PanelTopOpen className="h-3.5 w-3.5" />
            ) : (
              <PanelTopClose className="h-3.5 w-3.5" />
            )}
            <span>{configCollapsed ? "Show inputs" : "Hide inputs"}</span>
          </Button>
        </div>
        {children}
      </div>
    </div>
  );
}
