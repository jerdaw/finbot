"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RTooltip,
  ResponsiveContainer,
} from "recharts";

const TOOLTIP_STYLE = {
  backgroundColor: "rgba(15, 23, 42, 0.95)",
  border: "1px solid rgba(255, 255, 255, 0.08)",
  borderRadius: "8px",
  color: "#e2e8f0",
  fontSize: "12px",
  boxShadow: "0 8px 32px rgba(0, 0, 0, 0.3)",
};

interface DrawdownChartProps {
  data: { date: string; value: number }[];
  height?: number;
}

export function DrawdownChart({ data, height = 200 }: DrawdownChartProps) {
  let peak = -Infinity;
  const ddData = data.map((d) => {
    if (d.value > peak) peak = d.value;
    const dd = peak > 0 ? (d.value - peak) / peak : 0;
    return { date: d.date, drawdown: dd };
  });

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={ddData}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis
          dataKey="date"
          tick={{ fill: "#71717a", fontSize: 11 }}
          axisLine={{ stroke: "rgba(255,255,255,0.06)" }}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: "#71717a", fontSize: 11 }}
          axisLine={{ stroke: "rgba(255,255,255,0.06)" }}
          tickLine={false}
          tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
        />
        <RTooltip
          contentStyle={TOOLTIP_STYLE}
          formatter={(v?: number) => [`${((v ?? 0) * 100).toFixed(2)}%`, "Drawdown"]}
        />
        <Area
          type="monotone"
          dataKey="drawdown"
          stroke="#ef4444"
          fill="rgba(239,68,68,0.1)"
          strokeWidth={1.5}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
