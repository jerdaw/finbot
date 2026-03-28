"use client";

import { cn } from "@/lib/utils";

interface MetricBadgeProps {
  value: number | null;
  format?: (v: number) => string;
  className?: string;
}

export function MetricBadge({ value, format, className }: MetricBadgeProps) {
  if (value == null) {
    return (
      <span className={cn("text-xs text-muted-foreground", className)}>
        N/A
      </span>
    );
  }

  const formatted = format ? format(value) : value.toFixed(2);
  const isPositive = value > 0;
  const isNegative = value < 0;

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        isPositive && "bg-emerald-500/10 text-emerald-400",
        isNegative && "bg-red-500/10 text-red-400",
        !isPositive && !isNegative && "bg-muted/50 text-muted-foreground",
        className,
      )}
    >
      {isPositive && "+"}
      {formatted}
    </span>
  );
}
