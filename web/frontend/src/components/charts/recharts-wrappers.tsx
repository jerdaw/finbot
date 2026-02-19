"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RTooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  ScatterChart,
  Scatter,
  Cell,
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

interface BarChartWrapperProps {
  data: Record<string, unknown>[];
  xKey: string;
  yKey: string;
  color?: string;
  height?: number;
  label?: string;
}

export function BarChartWrapper({
  data,
  xKey,
  yKey,
  color = CHART_COLORS.blue,
  height = 300,
  label,
}: BarChartWrapperProps) {
  return (
    <div>
      {label && (
        <p className="mb-3 text-xs font-medium tracking-wider text-muted-foreground uppercase">
          {label}
        </p>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
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
          <RTooltip contentStyle={TOOLTIP_STYLE} cursor={{ fill: "rgba(59, 130, 246, 0.06)" }} />
          <Bar dataKey={yKey} fill={color} radius={[6, 6, 0, 0]} fillOpacity={0.85} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

interface AreaChartWrapperProps {
  data: Record<string, unknown>[];
  xKey: string;
  series: { key: string; color?: string }[];
  height?: number;
  label?: string;
}

export function AreaChartWrapper({
  data,
  xKey,
  series,
  height = 300,
  label,
}: AreaChartWrapperProps) {
  return (
    <div>
      {label && (
        <p className="mb-3 text-xs font-medium tracking-wider text-muted-foreground uppercase">
          {label}
        </p>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
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
          {series.map((s, i) => {
            const seriesColor = s.color || CHART_COLORS.series[i % CHART_COLORS.series.length];
            return (
              <Area
                key={s.key}
                type="monotone"
                dataKey={s.key}
                stroke={seriesColor}
                fill={`${seriesColor}15`}
                strokeWidth={2}
              />
            );
          })}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

interface ScatterChartWrapperProps {
  data: { x: number; y: number; label?: string }[];
  xLabel?: string;
  yLabel?: string;
  height?: number;
  label?: string;
}

export function ScatterChartWrapper({
  data,
  xLabel = "X",
  yLabel = "Y",
  height = 300,
  label,
}: ScatterChartWrapperProps) {
  return (
    <div>
      {label && (
        <p className="mb-3 text-xs font-medium tracking-wider text-muted-foreground uppercase">
          {label}
        </p>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
          <XAxis
            dataKey="x"
            name={xLabel}
            tick={{ fill: "#71717a", fontSize: 11 }}
            axisLine={{ stroke: "rgba(255,255,255,0.06)" }}
            tickLine={false}
          />
          <YAxis
            dataKey="y"
            name={yLabel}
            tick={{ fill: "#71717a", fontSize: 11 }}
            axisLine={{ stroke: "rgba(255,255,255,0.06)" }}
            tickLine={false}
          />
          <RTooltip contentStyle={TOOLTIP_STYLE} />
          <Scatter data={data}>
            {data.map((_, i) => (
              <Cell key={i} fill={CHART_COLORS.blue} fillOpacity={0.7} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
