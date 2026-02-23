"use client";

import { type ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface Preset {
  label: string;
  onClick: () => void;
}

interface EmptyStateProps {
  icon?: LucideIcon;
  message: string;
  presets?: Preset[];
  className?: string;
  children?: ReactNode;
}

export function EmptyState({
  icon: Icon,
  message,
  presets,
  className,
  children,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-xl border border-dashed border-border/50 bg-card/20 py-16",
        className,
      )}
    >
      {Icon && (
        <Icon className="mb-4 h-10 w-10 text-muted-foreground/30" />
      )}
      <p className="text-sm text-muted-foreground">{message}</p>
      {presets && presets.length > 0 && (
        <div className="mt-4 flex flex-wrap items-center justify-center gap-2">
          <span className="text-xs text-muted-foreground/60">Try:</span>
          {presets.map((preset) => (
            <button
              key={preset.label}
              onClick={preset.onClick}
              className="rounded-md border border-border/50 bg-card/50 px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-accent/50 hover:text-foreground"
            >
              {preset.label}
            </button>
          ))}
        </div>
      )}
      {children}
    </div>
  );
}
