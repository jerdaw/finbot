"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { LightweightChart } from "@/components/charts/lightweight-chart";
import { DataTable } from "@/components/common/data-table";
import { StatCard } from "@/components/common/stat-card";
import { PageHeader } from "@/components/common/page-header";
import { ChartCard } from "@/components/common/chart-card";
import { ChartSkeleton, CardSkeleton } from "@/components/common/loading-skeleton";
import { apiGet } from "@/lib/api";
import { formatPercent, formatNumber } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { FundInfo, SimulationResponse } from "@/types/api";

const CHART_COLORS = [
  "#3b82f6", "#22c55e", "#f59e0b", "#a855f7", "#06b6d4", "#ef4444",
  "#ec4899", "#14b8a6", "#f97316", "#8b5cf6",
];

const FUND_GROUPS: { label: string; tickers: string[] }[] = [
  { label: "S&P 500", tickers: ["SPY", "SSO", "UPRO"] },
  { label: "Nasdaq", tickers: ["QQQ", "QLD", "TQQQ"] },
  { label: "Treasury Long", tickers: ["TLT", "UBT", "TMF"] },
  { label: "Treasury Mid", tickers: ["IEF", "UST", "TYD"] },
  { label: "Treasury Short", tickers: ["SHY"] },
  { label: "Multi-Asset", tickers: ["NTSX"] },
];

const PRESETS: { label: string; tickers: string[] }[] = [
  { label: "Leveraged S&P", tickers: ["SPY", "SSO", "UPRO"] },
  { label: "Bond Duration", tickers: ["SHY", "IEF", "TLT"] },
  { label: "60/40", tickers: ["SPY", "TLT"] },
];

export default function SimulationsPage() {
  const [selected, setSelected] = useState<string[]>(["SPY"]);
  const [normalize, setNormalize] = useState(true);

  const { data: funds } = useQuery({
    queryKey: ["funds"],
    queryFn: () => apiGet<FundInfo[]>("/api/simulations/funds"),
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ["simulations", selected, normalize],
    queryFn: () => {
      const params = new URLSearchParams();
      selected.forEach((t) => params.append("tickers", t));
      if (normalize) params.set("normalize", "true");
      return apiGet<SimulationResponse>(`/api/simulations/run?${params.toString()}`, 60000);
    },
    enabled: selected.length > 0,
  });

  if (error) toast.error(`Simulation failed: ${(error as Error).message}`);

  const toggleFund = (ticker: string) => {
    setSelected((prev) =>
      prev.includes(ticker)
        ? prev.filter((t) => t !== ticker)
        : [...prev, ticker],
    );
  };

  return (
    <div className="space-y-8">
      <PageHeader
        title="Fund Simulations"
        description="Compare simulated leveraged fund performance across different products"
      />

      {/* Preset buttons */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-medium text-muted-foreground/60">Presets:</span>
        {PRESETS.map((preset) => (
          <button
            key={preset.label}
            onClick={() => setSelected(preset.tickers)}
            className="rounded-md border border-border/50 bg-card/50 px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-accent/50 hover:text-foreground"
          >
            {preset.label}
          </button>
        ))}
      </div>

      {/* Fund selector chips grouped by category */}
      <div className="space-y-3">
        {FUND_GROUPS.map((group) => {
          const availableTickers = group.tickers.filter((t) =>
            funds?.some((f) => f.ticker === t),
          );
          if (availableTickers.length === 0) return null;
          return (
            <div key={group.label}>
              <p className="mb-1.5 text-[10px] font-semibold tracking-widest text-muted-foreground/60 uppercase">
                {group.label}
              </p>
              <div className="flex flex-wrap gap-2">
                {availableTickers.map((ticker) => (
                  <button
                    key={ticker}
                    onClick={() => toggleFund(ticker)}
                    className={cn(
                      "rounded-lg border px-3 py-1.5 text-xs font-medium transition-all duration-200",
                      selected.includes(ticker)
                        ? "border-blue-500/50 bg-blue-500/10 text-blue-400 shadow-sm shadow-blue-500/10"
                        : "border-border/50 bg-card/30 text-muted-foreground hover:border-border hover:text-foreground",
                    )}
                  >
                    {ticker}
                  </button>
                ))}
              </div>
            </div>
          );
        })}
        {/* Ungrouped funds */}
        {(() => {
          const groupedTickers = FUND_GROUPS.flatMap((g) => g.tickers);
          const ungrouped = funds?.filter((f) => !groupedTickers.includes(f.ticker)) ?? [];
          if (ungrouped.length === 0) return null;
          return (
            <div>
              <p className="mb-1.5 text-[10px] font-semibold tracking-widest text-muted-foreground/60 uppercase">
                Other
              </p>
              <div className="flex flex-wrap gap-2">
                {ungrouped.map((f) => (
                  <button
                    key={f.ticker}
                    onClick={() => toggleFund(f.ticker)}
                    className={cn(
                      "rounded-lg border px-3 py-1.5 text-xs font-medium transition-all duration-200",
                      selected.includes(f.ticker)
                        ? "border-blue-500/50 bg-blue-500/10 text-blue-400 shadow-sm shadow-blue-500/10"
                        : "border-border/50 bg-card/30 text-muted-foreground hover:border-border hover:text-foreground",
                    )}
                  >
                    {f.ticker}
                  </button>
                ))}
              </div>
            </div>
          );
        })()}
      </div>

      {/* Normalize toggle */}
      <div className="flex items-center gap-3">
        <Switch
          id="normalize"
          checked={normalize}
          onCheckedChange={setNormalize}
        />
        <Label htmlFor="normalize" className="text-sm text-muted-foreground">
          Normalize to 100
        </Label>
      </div>

      {/* Chart */}
      {isLoading ? (
        <ChartSkeleton />
      ) : data ? (
        <ChartCard title={`${normalize ? "Normalized" : "Absolute"} Performance`}>
          <LightweightChart
            series={data.series.map((s, i) => ({
              ...s,
              color: CHART_COLORS[i % CHART_COLORS.length],
            }))}
            height={450}
            type="line"
          />
        </ChartCard>
      ) : null}

      {/* Metrics */}
      {isLoading ? (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <CardSkeleton /><CardSkeleton /><CardSkeleton /><CardSkeleton />
        </div>
      ) : data?.metrics && data.metrics.length > 0 ? (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            {data.metrics.slice(0, 4).map((m) => (
              <StatCard
                key={m.ticker}
                label={`${m.ticker} CAGR`}
                value={formatPercent(m.cagr)}
                trend={m.cagr != null && m.cagr > 0 ? "up" : "down"}
              />
            ))}
          </div>

          <ChartCard title="Summary Metrics">
            <DataTable
              columns={[
                { key: "ticker", label: "Ticker" },
                { key: "name", label: "Name" },
                { key: "leverage", label: "Leverage", format: (v) => `${v}x` },
                { key: "total_return", label: "Total Return", format: (v) => formatPercent(v as number) },
                { key: "cagr", label: "CAGR", format: (v) => formatPercent(v as number) },
                { key: "volatility", label: "Volatility", format: (v) => formatPercent(v as number) },
                { key: "max_drawdown", label: "Max DD", format: (v) => formatPercent(v as number) },
              ]}
              data={data.metrics}
            />
          </ChartCard>
        </>
      ) : null}
    </div>
  );
}
