"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { FanChart } from "@/components/charts/fan-chart";
import { BarChartWrapper } from "@/components/charts/recharts-wrappers";
import { DataTable } from "@/components/common/data-table";
import { StatCard } from "@/components/common/stat-card";
import { PageHeader } from "@/components/common/page-header";
import { ToolLayout } from "@/components/common/tool-layout";
import { EmptyState } from "@/components/common/empty-state";
import { InlineError } from "@/components/common/inline-error";
import { ChartSkeleton, CardSkeleton } from "@/components/common/loading-skeleton";
import { ConfigPanel } from "@/components/common/config-panel";
import { ChartCard } from "@/components/common/chart-card";
import { Shuffle } from "lucide-react";
import { apiPost } from "@/lib/api";
import { formatCurrency, formatPercent, formatNumber } from "@/lib/format";
import type { MonteCarloRequest, MonteCarloResponse } from "@/types/api";

export default function MonteCarloPage() {
  const [ticker, setTicker] = useState("SPY");
  const [simPeriods, setSimPeriods] = useState(252);
  const [nSims, setNSims] = useState(1000);

  const mutation = useMutation({
    mutationFn: (req: MonteCarloRequest) =>
      apiPost<MonteCarloResponse>("/api/monte-carlo/run", req, 120000),
    onSuccess: () => toast.success("Simulation complete"),
    onError: (e) => toast.error(`Simulation failed: ${e.message}`),
  });

  const handleRun = () => {
    mutation.mutate({
      ticker: ticker.toUpperCase(),
      sim_periods: simPeriods,
      n_sims: Math.min(nSims, 10000),
    });
  };

  const result = mutation.data;
  const stats = result?.statistics;

  // Build histogram data from final values of sample paths and bands
  const histogramData = buildHistogram(result);

  return (
    <div className="space-y-8">
      <PageHeader
        title="Monte Carlo Simulation"
        description="Run Monte Carlo simulations to model possible future price paths"
      />

      <ToolLayout
        configPanel={
        <ConfigPanel title="Configuration">
          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Ticker</Label>
            <Input
              className="border-border/50 bg-background/50"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              placeholder="e.g. SPY"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Simulation Periods</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              value={simPeriods}
              onChange={(e) => setSimPeriods(Number(e.target.value))}
              min={1}
            />
            <p className="text-xs text-muted-foreground">
              Trading days to simulate (252 = ~1 year)
            </p>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Number of Simulations</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              value={nSims}
              onChange={(e) => setNSims(Math.min(Number(e.target.value), 10000))}
              min={100}
              max={10000}
            />
            <p className="text-xs text-muted-foreground">
              Max 10,000 simulations
            </p>
          </div>

          <Button
            className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
            onClick={handleRun}
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "Running..." : "Run Simulation"}
          </Button>
        </ConfigPanel>
        }
      >
          {mutation.isPending && (
            <>
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <CardSkeleton />
                <CardSkeleton />
                <CardSkeleton />
                <CardSkeleton />
              </div>
              <ChartSkeleton />
              <ChartSkeleton />
            </>
          )}

          {stats && (
            <>
              {/* Stat cards */}
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <StatCard
                  label="Median Final Value"
                  value={formatCurrency(stats["median_final"] ?? null)}
                  trend={
                    stats["median_final"] != null && stats["median_final"] > 0
                      ? "up"
                      : "neutral"
                  }
                />
                <StatCard
                  label="Mean Final Value"
                  value={formatCurrency(stats["mean_final"] ?? null)}
                  trend={
                    stats["mean_final"] != null && stats["mean_final"] > 0
                      ? "up"
                      : "neutral"
                  }
                />
                <StatCard
                  label="VaR (p5)"
                  value={formatCurrency(stats["var_p5"] ?? null)}
                  trend="down"
                />
                <StatCard
                  label="Prob of Loss"
                  value={
                    stats["prob_loss"] != null
                      ? formatPercent(stats["prob_loss"])
                      : "N/A"
                  }
                  trend={
                    stats["prob_loss"] != null && stats["prob_loss"] > 0.5
                      ? "down"
                      : "up"
                  }
                />
              </div>

              {/* Fan chart */}
              {result && result.periods.length > 0 && (
                <ChartCard title="Price Path Fan Chart">
                  <FanChart
                    periods={result.periods}
                    bands={result.bands}
                    samplePaths={result.sample_paths}
                    height={400}
                  />
                </ChartCard>
              )}

              {/* Final value histogram */}
              {histogramData.length > 0 && (
                <ChartCard title="Final Value Distribution">
                  <BarChartWrapper
                    data={histogramData}
                    xKey="bin"
                    yKey="count"
                    height={300}
                  />
                </ChartCard>
              )}

              {/* Statistics table */}
              <ChartCard title="Simulation Statistics">
                <DataTable
                  columns={[
                    { key: "metric", label: "Metric" },
                    { key: "value", label: "Value" },
                  ]}
                  data={Object.entries(stats).map(([k, v]) => ({
                    metric: formatStatLabel(k),
                    value:
                      v == null
                        ? "N/A"
                        : k.includes("prob") || k.includes("pct")
                          ? formatPercent(v)
                          : formatNumber(v, 2),
                  }))}
                />
              </ChartCard>
            </>
          )}

          {mutation.isError && (
            <InlineError
              message={mutation.error?.message ?? "Simulation failed"}
              onRetry={handleRun}
            />
          )}

          {!mutation.isPending && !mutation.isError && !result && (
            <EmptyState
              icon={Shuffle}
              message="Configure parameters and click Run Simulation to see results."
              presets={[
                { label: "SPY 1-Year (1000 sims)", onClick: () => { setTicker("SPY"); setSimPeriods(252); setNSims(1000); } },
                { label: "QQQ 2-Year (5000 sims)", onClick: () => { setTicker("QQQ"); setSimPeriods(504); setNSims(5000); } },
              ]}
            />
          )}
      </ToolLayout>
    </div>
  );
}

/** Build histogram bins from sample_paths final values. */
function buildHistogram(
  result: MonteCarloResponse | undefined,
): Record<string, unknown>[] {
  if (!result?.sample_paths || result.sample_paths.length === 0) return [];

  const finalValues = result.sample_paths
    .map((path) => {
      const last = path[path.length - 1];
      return last;
    })
    .filter((v): v is number => v != null);

  if (finalValues.length === 0) return [];

  const min = Math.min(...finalValues);
  const max = Math.max(...finalValues);
  const nBins = 20;
  const binWidth = (max - min) / nBins || 1;

  const bins: Record<string, unknown>[] = [];
  for (let i = 0; i < nBins; i++) {
    const lo = min + i * binWidth;
    const hi = lo + binWidth;
    const count = finalValues.filter(
      (v) => v >= lo && (i === nBins - 1 ? v <= hi : v < hi),
    ).length;
    bins.push({
      bin: `$${lo.toFixed(0)}`,
      count,
    });
  }

  return bins;
}

/** Convert snake_case stat key to readable label. */
function formatStatLabel(key: string): string {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
