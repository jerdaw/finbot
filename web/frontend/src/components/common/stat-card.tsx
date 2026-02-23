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
        "group relative overflow-hidden rounded-xl border border-border/50 bg-card/80 p-5 backdrop-blur-sm transition-all duration-300 hover:border-border",
        "gradient-border",
        className,
      )}
    >
      {/* Subtle top gradient accent */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-blue-500/20 to-transparent" />

      <div className="flex items-center justify-between">
        <p className="text-xs font-medium tracking-wider text-muted-foreground uppercase">
          {label}
        </p>
        {icon && (
          <div className="text-muted-foreground/50 transition-colors group-hover:text-muted-foreground">
            {icon}
          </div>
        )}
      </div>
      <div className="mt-3 flex items-end gap-2">
        <p className="stat-value text-2xl font-bold tracking-tight">{value}</p>
        {trend && trend !== "neutral" && (
          <span
            className={cn(
              "mb-0.5 flex items-center gap-0.5 rounded-full px-1.5 py-0.5 text-xs font-medium",
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
