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
    <div className="min-w-0 space-y-6">
      {/* Config panel (Bounded Width) */}
      <div
        className={cn(
          "mx-auto w-full max-w-[1400px]",
          configCollapsed && "hidden"
        )}
      >
        {configPanel}
      </div>

      {/* Results area (Full Width) */}
      <div className="min-w-0 flex-1 space-y-8 w-full">
        <div className="hidden min-h-8 items-center justify-end border-b border-border/40 pb-2 xl:flex">
          <Button
            variant="ghost"
            size="sm"
            className="h-7 gap-1.5 px-2 text-xs font-medium text-muted-foreground hover:text-foreground"
            onClick={() => setConfigCollapsed(!configCollapsed)}
            aria-label={configCollapsed ? "Show configuration" : "Hide configuration"}
            title={configCollapsed ? "Show configuration" : "Hide configuration"}
          >
            {configCollapsed ? (
              <PanelTopOpen className="h-4 w-4" />
            ) : (
              <PanelTopClose className="h-4 w-4" />
            )}
            <span>{configCollapsed ? "Show Configuration" : "Hide Configuration"}</span>
          </Button>
        </div>
        {children}
      </div>
    </div>
  );
}
