"use client";

import { cn } from "@/lib/utils";

interface HeatmapProps {
  labels: string[];
  matrix: Record<string, Record<string, number>>;
  className?: string;
}

function getColor(value: number): string {
  // Interpolate from red (-1) through white (0) to green (+1)
  const clamped = Math.max(-1, Math.min(1, value));
  if (clamped >= 0) {
    const g = Math.round(180 + 75 * (1 - clamped));
    return `rgb(${Math.round(60 + 195 * (1 - clamped))}, ${g}, ${Math.round(60 + 195 * (1 - clamped))})`;
  }
  const r = Math.round(180 + 75 * (1 + clamped));
  return `rgb(${r}, ${Math.round(60 + 195 * (1 + clamped))}, ${Math.round(60 + 195 * (1 + clamped))})`;
}

export function Heatmap({ labels, matrix, className }: HeatmapProps) {
  return (
    <div className={cn("overflow-x-auto", className)}>
      <div
        className="inline-grid gap-px"
        style={{
          gridTemplateColumns: `80px repeat(${labels.length}, minmax(60px, 1fr))`,
        }}
      >
        {/* Header row */}
        <div />
        {labels.map((label) => (
          <div
            key={`h-${label}`}
            className="truncate px-2 py-1.5 text-center text-[10px] font-semibold tracking-wider text-muted-foreground uppercase"
          >
            {label}
          </div>
        ))}

        {/* Data rows */}
        {labels.map((rowLabel) => (
          <>
            <div
              key={`r-${rowLabel}`}
              className="flex items-center truncate px-2 py-1.5 text-[10px] font-semibold tracking-wider text-muted-foreground uppercase"
            >
              {rowLabel}
            </div>
            {labels.map((colLabel) => {
              const value = matrix[rowLabel]?.[colLabel] ?? 0;
              return (
                <div
                  key={`${rowLabel}-${colLabel}`}
                  className="flex items-center justify-center rounded px-2 py-2 text-xs font-medium"
                  style={{
                    backgroundColor: getColor(value),
                    color: Math.abs(value) > 0.6 ? "#fff" : "#1a1a2e",
                  }}
                  title={`${rowLabel} / ${colLabel}: ${value.toFixed(3)}`}
                >
                  {value.toFixed(2)}
                </div>
              );
            })}
          </>
        ))}
      </div>
    </div>
  );
}
