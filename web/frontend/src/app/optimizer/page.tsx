"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { BarChartWrapper } from "@/components/charts/recharts-wrappers";
import { DataTable } from "@/components/common/data-table";
import { StatCard } from "@/components/common/stat-card";
import { PageHeader } from "@/components/common/page-header";
import { ConfigPanel } from "@/components/common/config-panel";
import { ChartCard } from "@/components/common/chart-card";
import { ToolLayout } from "@/components/common/tool-layout";
import { EmptyState } from "@/components/common/empty-state";
import { InlineError } from "@/components/common/inline-error";
import {
  ChartSkeleton,
  CardSkeleton,
  TableSkeleton,
} from "@/components/common/loading-skeleton";
import { TrendingUp } from "lucide-react";
import { apiPost } from "@/lib/api";
import { formatPercent, formatNumber, formatCurrency } from "@/lib/format";
import type { DCAOptimizerRequest, DCAOptimizerResponse } from "@/types/api";

const DEFAULT_RATIOS = "0.1, 0.2, 0.3, 0.5, 0.7, 1.0";
const DEFAULT_DCA_DURATIONS = "30, 60, 90, 120, 180, 252";
const DEFAULT_TRIAL_DURATIONS = "252, 504, 756";

/** Parse a comma-separated string of numbers. */
function parseNumberList(input: string): number[] {
  return input
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s !== "")
    .map(Number)
    .filter((n) => !isNaN(n));
}

export default function OptimizerPage() {
  const [ticker, setTicker] = useState("SPY");
  const [ratioRange, setRatioRange] = useState(DEFAULT_RATIOS);
  const [dcaDurations, setDcaDurations] = useState(DEFAULT_DCA_DURATIONS);
  const [trialDurations, setTrialDurations] = useState(DEFAULT_TRIAL_DURATIONS);
  const [startingCash, setStartingCash] = useState(10000);
  const [showRawResults, setShowRawResults] = useState(false);

  const mutation = useMutation({
    mutationFn: (req: DCAOptimizerRequest) =>
      apiPost<DCAOptimizerResponse>("/api/optimizer/run", req, 120000),
    onSuccess: () => toast.success("Optimization complete"),
    onError: (e) => toast.error(`Optimization failed: ${e.message}`),
  });

  const handleRun = () => {
    const ratios = parseNumberList(ratioRange);
    const durations = parseNumberList(dcaDurations);
    const trials = parseNumberList(trialDurations);

    if (ratios.length === 0) {
      toast.error("Please enter at least one ratio value.");
      return;
    }

    mutation.mutate({
      ticker: ticker.toUpperCase(),
      ratio_range: ratios,
      dca_durations: durations.length > 0 ? durations : undefined,
      trial_durations: trials.length > 0 ? trials : undefined,
      starting_cash: startingCash,
    });
  };

  const result = mutation.data;

  // Derive summary stats from by_ratio data
  const bestByRatio = result?.by_ratio?.reduce(
    (best, row) => {
      const cagr = row["cagr"] as number | undefined;
      if (cagr != null && (best == null || cagr > (best["cagr"] as number))) {
        return row;
      }
      return best;
    },
    null as Record<string, unknown> | null,
  );

  const bestByDuration = result?.by_duration?.reduce(
    (best, row) => {
      const cagr = row["cagr"] as number | undefined;
      if (cagr != null && (best == null || cagr > (best["cagr"] as number))) {
        return row;
      }
      return best;
    },
    null as Record<string, unknown> | null,
  );

  return (
    <div className="space-y-8">
      <PageHeader
        title="DCA Optimizer"
        description="Find optimal dollar-cost averaging parameters via grid search"
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
            <Label className="text-xs text-muted-foreground">DCA Ratios</Label>
            <Input
              className="border-border/50 bg-background/50"
              value={ratioRange}
              onChange={(e) => setRatioRange(e.target.value)}
              placeholder="0.1, 0.2, 0.3, ..."
            />
            <p className="text-xs text-muted-foreground">
              Comma-separated ratio values (fraction of cash to invest each period)
            </p>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">DCA Durations (days)</Label>
            <Input
              className="border-border/50 bg-background/50"
              value={dcaDurations}
              onChange={(e) => setDcaDurations(e.target.value)}
              placeholder="30, 60, 90, ..."
            />
            <p className="text-xs text-muted-foreground">
              Comma-separated number of trading days for DCA
            </p>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Trial Durations (days)</Label>
            <Input
              className="border-border/50 bg-background/50"
              value={trialDurations}
              onChange={(e) => setTrialDurations(e.target.value)}
              placeholder="252, 504, ..."
            />
            <p className="text-xs text-muted-foreground">
              Total trial lengths to evaluate
            </p>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Starting Cash ($)</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              value={startingCash}
              onChange={(e) => setStartingCash(Number(e.target.value))}
              min={1}
            />
          </div>

          <Button
            className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
            onClick={handleRun}
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "Optimizing..." : "Run Optimizer"}
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
              <TableSkeleton />
            </>
          )}

          {result && (
            <>
              {/* Summary stat cards */}
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <StatCard
                  label="Best Ratio"
                  value={
                    bestByRatio
                      ? String(bestByRatio["ratio"] ?? "N/A")
                      : "N/A"
                  }
                />
                <StatCard
                  label="Best Ratio CAGR"
                  value={
                    bestByRatio
                      ? formatPercent(bestByRatio["cagr"] as number)
                      : "N/A"
                  }
                  trend={
                    bestByRatio && (bestByRatio["cagr"] as number) > 0
                      ? "up"
                      : "neutral"
                  }
                />
                <StatCard
                  label="Best Duration"
                  value={
                    bestByDuration
                      ? `${bestByDuration["duration"] ?? "N/A"} days`
                      : "N/A"
                  }
                />
                <StatCard
                  label="Total Scenarios"
                  value={formatNumber(result.raw_results?.length ?? 0, 0)}
                />
              </div>

              {/* By Ratio bar chart */}
              {result.by_ratio && result.by_ratio.length > 0 && (
                <ChartCard title="Performance by DCA Ratio">
                  <BarChartWrapper
                    data={result.by_ratio}
                    xKey="ratio"
                    yKey="cagr"
                    height={300}
                    label="CAGR by Ratio"
                  />
                </ChartCard>
              )}

              {/* By Duration bar chart */}
              {result.by_duration && result.by_duration.length > 0 && (
                <ChartCard title="Performance by DCA Duration">
                  <BarChartWrapper
                    data={result.by_duration}
                    xKey="duration"
                    yKey="cagr"
                    height={300}
                    label="CAGR by Duration (days)"
                  />
                </ChartCard>
              )}

              {/* Raw results table (expandable) */}
              {result.raw_results && result.raw_results.length > 0 && (
                <ChartCard
                  title={`Raw Results (${result.raw_results.length})`}
                  action={
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowRawResults(!showRawResults)}
                    >
                      {showRawResults ? "Collapse" : "Expand"}
                    </Button>
                  }
                >
                  {showRawResults && (
                    <DataTable
                      columns={buildRawResultColumns(result.raw_results)}
                      data={result.raw_results}
                    />
                  )}
                </ChartCard>
              )}
            </>
          )}

          {mutation.isError && (
            <InlineError
              message={mutation.error?.message ?? "Optimization failed"}
              onRetry={handleRun}
            />
          )}

          {!mutation.isPending && !mutation.isError && !result && (
            <EmptyState
              icon={TrendingUp}
              message="Configure parameters and click Run Optimizer to see results."
              presets={[
                { label: "SPY Default Grid", onClick: () => { setTicker("SPY"); setRatioRange(DEFAULT_RATIOS); setDcaDurations(DEFAULT_DCA_DURATIONS); } },
              ]}
            />
          )}
      </ToolLayout>
    </div>
  );
}

/** Dynamically build columns from raw result keys. */
function buildRawResultColumns(
  data: Record<string, unknown>[],
): { key: string; label: string; format?: (v: unknown) => string }[] {
  if (data.length === 0) return [];
  const keys = Object.keys(data[0]);

  return keys.map((key) => ({
    key,
    label: key
      .replace(/_/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase()),
    format: (v: unknown) => {
      if (v == null) return "N/A";
      if (typeof v === "number") {
        // Heuristic: values between -1 and 1 are likely percentages
        if (
          Math.abs(v) < 1 &&
          (key.includes("cagr") ||
            key.includes("sharpe") ||
            key.includes("drawdown") ||
            key.includes("return") ||
            key.includes("std"))
        ) {
          return formatPercent(v);
        }
        return formatNumber(v, 4);
      }
      return String(v);
    },
  }));
}
