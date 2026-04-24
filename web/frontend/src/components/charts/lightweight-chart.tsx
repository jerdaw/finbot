"use client";

import { useEffect, useRef } from "react";
import {
  createChart,
  type IChartApi,
  ColorType,
  PriceScaleMode,
  type Time,
  LineSeries,
  AreaSeries,
} from "lightweight-charts";
import { Download } from "lucide-react";
import { useThemeStore } from "@/stores/theme-store";
import { Button } from "@/components/ui/button";

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
  logScale?: boolean;
  downloadImageName?: string;
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
  logScale = false,
  downloadImageName,
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
        mode: logScale ? PriceScaleMode.Logarithmic : PriceScaleMode.Normal,
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
      chartRef.current = null;
    };
  }, [series, height, type, theme, logScale]);

  const handleDownloadImage = () => {
    const chart = chartRef.current;
    if (!chart || !downloadImageName) return;

    const canvas = chart.takeScreenshot();
    const anchor = document.createElement("a");
    anchor.href = canvas.toDataURL("image/png");
    anchor.download = downloadImageName.endsWith(".png")
      ? downloadImageName
      : `${downloadImageName}.png`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
  };

  return (
    <div className={className}>
      <div className="mb-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex min-w-0 flex-wrap items-center gap-3">
          {series.map((item, index) => (
            <span
              key={`${item.name}-${index}`}
              className="inline-flex min-w-0 items-center gap-1.5 text-xs text-muted-foreground"
            >
              <span
                className="h-2 w-2 shrink-0 rounded-full"
                style={{
                  backgroundColor:
                    item.color ||
                    DEFAULT_COLORS[index % DEFAULT_COLORS.length],
                }}
              />
              <span className="truncate">{item.name}</span>
            </span>
          ))}
        </div>
        {downloadImageName && (
          <Button
            type="button"
            variant="outline"
            size="xs"
            className="shrink-0 self-start sm:self-auto"
            onClick={handleDownloadImage}
          >
            <Download className="h-3.5 w-3.5" />
            PNG
          </Button>
        )}
      </div>
      <div ref={containerRef} className="rounded-lg" />
    </div>
  );
}
