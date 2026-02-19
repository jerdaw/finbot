"use client";

import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface ConfigPanelProps {
  title: string;
  children: ReactNode;
  className?: string;
}

export function ConfigPanel({ title, children, className }: ConfigPanelProps) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border border-border/50 bg-card/50 backdrop-blur-sm",
        "h-fit lg:sticky lg:top-20",
        className,
      )}
    >
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-blue-500/20 to-transparent" />
      <div className="border-b border-border/50 px-5 py-4">
        <h3 className="text-xs font-semibold tracking-wider text-muted-foreground uppercase">
          {title}
        </h3>
      </div>
      <div className="space-y-4 p-5">{children}</div>
    </div>
  );
}
