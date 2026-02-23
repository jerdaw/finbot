"use client";

import { useEffect, useRef } from "react";
import {
  createChart,
  type IChartApi,
  ColorType,
  type Time,
  LineSeries,
  AreaSeries,
} from "lightweight-charts";
import { useThemeStore } from "@/stores/theme-store";

interface SeriesData {
  name: string;
  dates: string[];
  values: (number | null)[];
  color?: string;
}

interface LightweightChartProps {
  series: SeriesData[];
  height?: number;
  type?: "line" | "area";
  className?: string;
}

const DEFAULT_COLORS = [
  "#3b82f6",
  "#22c55e",
  "#f59e0b",
  "#a855f7",
  "#06b6d4",
  "#ef4444",
];

export function LightweightChart({
  series,
  height = 400,
  type = "line",
  className,
}: LightweightChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const theme = useThemeStore((s) => s.theme);

  useEffect(() => {
    if (!containerRef.current) return;

    const isDark = theme === "dark";
    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height,
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: isDark ? "#71717a" : "#71717a",
        fontFamily: "var(--font-geist-sans), system-ui, sans-serif",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: isDark ? "rgba(255,255,255,0.04)" : "rgba(0,0,0,0.04)" },
        horzLines: { color: isDark ? "rgba(255,255,255,0.04)" : "rgba(0,0,0,0.04)" },
      },
      crosshair: {
        mode: 0,
        vertLine: {
          color: isDark ? "rgba(59,130,246,0.3)" : "rgba(59,130,246,0.2)",
          labelBackgroundColor: isDark ? "#1e293b" : "#f1f5f9",
        },
        horzLine: {
          color: isDark ? "rgba(59,130,246,0.3)" : "rgba(59,130,246,0.2)",
          labelBackgroundColor: isDark ? "#1e293b" : "#f1f5f9",
        },
      },
      rightPriceScale: {
        borderColor: isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.06)",
      },
      timeScale: {
        borderColor: isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.06)",
        timeVisible: false,
      },
    });

    chartRef.current = chart;

    series.forEach((s, i) => {
      const color = s.color || DEFAULT_COLORS[i % DEFAULT_COLORS.length];
      const data = s.dates
        .map((d, j) => ({
          time: d.split("T")[0] as Time,
          value: s.values[j],
        }))
        .filter((p): p is { time: Time; value: number } => p.value != null);

      if (type === "area") {
        const areaSeries = chart.addSeries(AreaSeries, {
          lineColor: color,
          topColor: `${color}25`,
          bottomColor: `${color}02`,
          lineWidth: 2,
        });
        areaSeries.setData(data);
      } else {
        const lineSeries = chart.addSeries(LineSeries, {
          color,
          lineWidth: 2,
        });
        lineSeries.setData(data);
      }
    });

    chart.timeScale().fitContent();

    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [series, height, type, theme]);

  return (
    <div className={className}>
      <div ref={containerRef} className="rounded-lg" />
    </div>
  );
}
