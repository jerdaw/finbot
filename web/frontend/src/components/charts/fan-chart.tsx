"use client";

import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RTooltip,
  ResponsiveContainer,
  Line,
  ComposedChart,
  Area,
} from "recharts";
import type { PercentileBand } from "@/types/api";

const TOOLTIP_STYLE = {
  backgroundColor: "rgba(15, 23, 42, 0.95)",
  border: "1px solid rgba(255, 255, 255, 0.08)",
  borderRadius: "8px",
  color: "#e2e8f0",
  fontSize: "12px",
  boxShadow: "0 8px 32px rgba(0, 0, 0, 0.3)",
};

interface FanChartProps {
  periods: number[];
  bands: PercentileBand[];
  samplePaths?: (number | null)[][];
  height?: number;
}

export function FanChart({ periods, bands, samplePaths, height = 400 }: FanChartProps) {
  const data = periods.map((p, i) => {
    const row: Record<string, number | null> = { period: p };
    bands.forEach((b) => {
      row[b.label] = b.values[i];
    });
    samplePaths?.slice(0, 5).forEach((path, j) => {
      row[`sample_${j}`] = path[i];
    });
    return row;
  });

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis
          dataKey="period"
          tick={{ fill: "#71717a", fontSize: 11 }}
          axisLine={{ stroke: "rgba(255,255,255,0.06)" }}
          tickLine={false}
          label={{ value: "Period", position: "bottom", fill: "#71717a", fontSize: 11 }}
        />
        <YAxis
          tick={{ fill: "#71717a", fontSize: 11 }}
          axisLine={{ stroke: "rgba(255,255,255,0.06)" }}
          tickLine={false}
        />
        <RTooltip contentStyle={TOOLTIP_STYLE} />

        {/* Outer band: p5-p95 */}
        <Area type="monotone" dataKey="p95" stroke="none" fill="rgba(59,130,246,0.06)" />
        <Area type="monotone" dataKey="p5" stroke="none" fill="transparent" />

        {/* Inner band: p25-p75 */}
        <Area type="monotone" dataKey="p75" stroke="none" fill="rgba(59,130,246,0.12)" />
        <Area type="monotone" dataKey="p25" stroke="none" fill="transparent" />

        {/* Median line */}
        <Area
          type="monotone"
          dataKey="p50"
          stroke="#3b82f6"
          fill="none"
          strokeWidth={2}
        />

        {/* Sample paths */}
        {samplePaths?.slice(0, 5).map((_, j) => (
          <Line
            key={j}
            type="monotone"
            dataKey={`sample_${j}`}
            stroke="rgba(148,163,184,0.2)"
            dot={false}
            strokeWidth={1}
          />
        ))}
      </ComposedChart>
    </ResponsiveContainer>
  );
}
