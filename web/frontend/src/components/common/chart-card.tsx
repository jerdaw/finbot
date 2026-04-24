"use client";

import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface ChartCardProps {
  title: string;
  children: ReactNode;
  className?: string;
  action?: ReactNode;
}

export function ChartCard({ title, children, className, action }: ChartCardProps) {
  return (
    <div
      className={cn(
        "relative min-w-0 overflow-hidden rounded-lg border border-border/60 bg-card shadow-sm",
        className,
      )}
    >
      <div className="flex flex-col gap-2 border-b border-border/60 bg-muted/10 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
        <h3 className="text-sm font-semibold text-foreground">
          {title}
        </h3>
        {action && <div className="flex flex-wrap items-center gap-2">{action}</div>}
      </div>
      <div className="min-w-0 p-4 sm:p-5">{children}</div>
    </div>
  );
}
