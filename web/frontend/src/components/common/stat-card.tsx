"use client";

import { TrendingDown, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string;
  trend?: "up" | "down" | "neutral";
  icon?: React.ReactNode;
  className?: string;
}

export function StatCard({ label, value, trend, icon, className }: StatCardProps) {
  return (
    <div
      className={cn(
        "group relative overflow-hidden rounded-lg border border-border/60 bg-card p-4 shadow-sm transition-colors hover:border-border",
        className,
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <p className="text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">
          {label}
        </p>
        {icon && (
          <div className="text-muted-foreground/50 transition-colors group-hover:text-muted-foreground">
            {icon}
          </div>
        )}
      </div>
      <div className="mt-2 flex flex-wrap items-end gap-2">
        <p className="stat-value break-words text-2xl font-semibold tracking-tight">{value}</p>
        {trend && trend !== "neutral" && (
          <span
            className={cn(
              "mb-1 flex items-center gap-0.5 rounded-md px-1.5 py-0.5 text-xs font-medium",
              trend === "up"
                ? "bg-emerald-500/10 text-emerald-400"
                : "bg-red-500/10 text-red-400",
            )}
          >
            {trend === "up" ? (
              <TrendingUp className="h-3 w-3" />
            ) : (
              <TrendingDown className="h-3 w-3" />
            )}
          </span>
        )}
      </div>
    </div>
  );
}
