"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RTooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { CHART_COLORS } from "@/lib/constants";

const TOOLTIP_STYLE = {
  backgroundColor: "rgba(15, 23, 42, 0.95)",
  border: "1px solid rgba(255, 255, 255, 0.08)",
  borderRadius: "8px",
  color: "#e2e8f0",
  fontSize: "12px",
  boxShadow: "0 8px 32px rgba(0, 0, 0, 0.3)",
  backdropFilter: "blur(12px)",
};

interface LineChartSeries {
  key: string;
  color?: string;
  strokeDasharray?: string;
}

interface LineChartWrapperProps {
  data: Record<string, unknown>[];
  xKey: string;
  series: LineChartSeries[];
  height?: number;
  label?: string;
  referenceY?: number;
  referenceLabel?: string;
}

export function LineChartWrapper({
  data,
  xKey,
  series,
  height = 300,
  label,
  referenceY,
  referenceLabel,
}: LineChartWrapperProps) {
  return (
    <div>
      {label && (
        <p className="mb-3 text-xs font-medium tracking-wider text-muted-foreground uppercase">
          {label}
        </p>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data}>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="rgba(255,255,255,0.04)"
          />
          <XAxis
            dataKey={xKey}
            tick={{ fill: "#71717a", fontSize: 11 }}
            axisLine={{ stroke: "rgba(255,255,255,0.06)" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "#71717a", fontSize: 11 }}
            axisLine={{ stroke: "rgba(255,255,255,0.06)" }}
            tickLine={false}
          />
          <RTooltip contentStyle={TOOLTIP_STYLE} />
          {referenceY != null && (
            <ReferenceLine
              y={referenceY}
              stroke="rgba(255,255,255,0.2)"
              strokeDasharray="4 4"
              label={
                referenceLabel
                  ? {
                      value: referenceLabel,
                      fill: "#71717a",
                      fontSize: 10,
                    }
                  : undefined
              }
            />
          )}
          {series.map((s, i) => (
            <Line
              key={s.key}
              type="monotone"
              dataKey={s.key}
              stroke={
                s.color ||
                CHART_COLORS.series[i % CHART_COLORS.series.length]
              }
              strokeWidth={2}
              dot={false}
              strokeDasharray={s.strokeDasharray}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
