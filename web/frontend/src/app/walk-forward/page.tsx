"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
import { BarChart3 } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";
import { formatPercent, formatNumber } from "@/lib/format";
import type {
  WalkForwardRequest,
  WalkForwardResponse,
  StrategyInfo,
} from "@/types/api";

export default function WalkForwardPage() {
  const [tickers, setTickers] = useState("SPY");
  const [strategy, setStrategy] = useState("NoRebalance");
  const [startDate, setStartDate] = useState("2010-01-01");
  const [endDate, setEndDate] = useState("2024-12-31");
  const [trainWindow, setTrainWindow] = useState(504);
  const [testWindow, setTestWindow] = useState(126);
  const [stepSize, setStepSize] = useState(63);
  const [anchored, setAnchored] = useState(false);
  const [params, setParams] = useState<Record<string, number>>({});

  const { data: strategies } = useQuery({
    queryKey: ["strategies"],
    queryFn: () => apiGet<StrategyInfo[]>("/api/backtesting/strategies"),
  });

  const currentStrategy = strategies?.find((s) => s.name === strategy);

  const mutation = useMutation({
    mutationFn: (req: WalkForwardRequest) =>
      apiPost<WalkForwardResponse>("/api/walk-forward/run", req, 180000),
    onSuccess: () => toast.success("Walk-forward analysis complete"),
    onError: (e) => toast.error(`Walk-forward failed: ${e.message}`),
  });

  const handleRun = () => {
    const tickerList = tickers
      .split(",")
      .map((t) => t.trim().toUpperCase())
      .filter((t) => t !== "");

    if (tickerList.length === 0) {
      toast.error("Please enter at least one ticker.");
      return;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const strategyParams: Record<string, any> = { ...params };
    if (strategy === "NoRebalance") {
      strategyParams.equity_proportions = tickerList.map(
        () => 1 / tickerList.length,
      );
    }
    if (strategy === "Rebalance") {
      strategyParams.rebal_proportions = tickerList.map(
        () => 1 / tickerList.length,
      );
    }

    mutation.mutate({
      tickers: tickerList,
      strategy,
      strategy_params: strategyParams,
      start_date: startDate,
      end_date: endDate,
      train_window: trainWindow,
      test_window: testWindow,
      step_size: stepSize,
      anchored,
    });
  };

  const handleStrategyChange = (name: string) => {
    setStrategy(name);
    const s = strategies?.find((st) => st.name === name);
    if (s) {
      const defaults: Record<string, number> = {};
      s.params.forEach((p) => {
        defaults[p.name] = p.default as number;
      });
      setParams(defaults);
    } else {
      setParams({});
    }
  };

  const result = mutation.data;
  const summary = result?.summary_metrics;

  // Build timeline chart data from windows
  const timelineData = result?.windows?.map((w) => ({
    window: `W${w.window_id}`,
    test_start: w.test_start,
    test_end: w.test_end,
    cagr: w.metrics["CAGR"] ?? w.metrics["cagr"] ?? null,
    sharpe: w.metrics["Sharpe"] ?? w.metrics["sharpe"] ?? null,
    max_drawdown:
      w.metrics["Max Drawdown"] ?? w.metrics["max_drawdown"] ?? null,
  }));

  return (
    <div className="space-y-8">
      <PageHeader
        title="Walk-Forward Analysis"
        description="Test strategy robustness with rolling train/test windows"
      />

      <ToolLayout
        configPanel={
        <ConfigPanel title="Configuration">
          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Tickers</Label>
            <Input
              className="border-border/50 bg-background/50"
              value={tickers}
              onChange={(e) => setTickers(e.target.value)}
              placeholder="e.g. SPY, TLT"
            />
            <p className="text-xs text-muted-foreground">
              Comma-separated list
            </p>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Strategy</Label>
            <Select value={strategy} onValueChange={handleStrategyChange}>
              <SelectTrigger className="border-border/50 bg-background/50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                {strategies?.map((s) => (
                  <SelectItem key={s.name} value={s.name}>
                    {s.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {currentStrategy && (
              <p className="text-xs text-muted-foreground">
                {currentStrategy.description}
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Start Date</Label>
              <Input
                className="border-border/50 bg-background/50"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">End Date</Label>
              <Input
                className="border-border/50 bg-background/50"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Train Window (days)</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              value={trainWindow}
              onChange={(e) => setTrainWindow(Number(e.target.value))}
              min={1}
            />
            <p className="text-xs text-muted-foreground">
              Trading days for in-sample training (504 = ~2 years)
            </p>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Test Window (days)</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              value={testWindow}
              onChange={(e) => setTestWindow(Number(e.target.value))}
              min={1}
            />
            <p className="text-xs text-muted-foreground">
              Trading days for out-of-sample testing (126 = ~6 months)
            </p>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Step Size (days)</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              value={stepSize}
              onChange={(e) => setStepSize(Number(e.target.value))}
              min={1}
            />
            <p className="text-xs text-muted-foreground">
              Trading days between each window start (63 = ~quarter)
            </p>
          </div>

          <div className="flex items-center justify-between">
            <Label className="text-xs text-muted-foreground">Anchored</Label>
            <Switch
              checked={anchored}
              onCheckedChange={setAnchored}
            />
          </div>
          <p className="text-xs text-muted-foreground">
            Anchored: training window starts from the same date and grows.
            Rolling: fixed-size sliding window.
          </p>

          {/* Dynamic strategy params */}
          {currentStrategy?.params.map((p) => (
            <div key={p.name} className="space-y-1">
              <Label className="text-xs text-muted-foreground">{p.description || p.name}</Label>
              <Input
                className="border-border/50 bg-background/50"
                type="number"
                step={p.type === "float" ? 0.01 : 1}
                value={params[p.name] ?? p.default}
                onChange={(e) =>
                  setParams((prev) => ({
                    ...prev,
                    [p.name]: Number(e.target.value),
                  }))
                }
              />
            </div>
          ))}

          <Button
            className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
            onClick={handleRun}
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "Running..." : "Run Walk-Forward"}
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
              <TableSkeleton />
            </>
          )}

          {summary && result && (
            <>
              {/* Summary stat cards */}
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <StatCard
                  label="Avg CAGR"
                  value={formatPercent(
                    (summary["avg_cagr"] ??
                      summary["Avg CAGR"] ??
                      summary["CAGR"]) as number | null,
                  )}
                  trend={
                    ((summary["avg_cagr"] ??
                      summary["Avg CAGR"] ??
                      summary["CAGR"]) as number | null) != null &&
                    ((summary["avg_cagr"] ??
                      summary["Avg CAGR"] ??
                      summary["CAGR"]) as number) > 0
                      ? "up"
                      : "down"
                  }
                />
                <StatCard
                  label="Avg Sharpe"
                  value={formatNumber(
                    (summary["avg_sharpe"] ??
                      summary["Avg Sharpe"] ??
                      summary["Sharpe"]) as number | null,
                    3,
                  )}
                  trend={
                    ((summary["avg_sharpe"] ??
                      summary["Avg Sharpe"] ??
                      summary["Sharpe"]) as number | null) != null &&
                    ((summary["avg_sharpe"] ??
                      summary["Avg Sharpe"] ??
                      summary["Sharpe"]) as number) > 0
                      ? "up"
                      : "down"
                  }
                />
                <StatCard
                  label="Worst Drawdown"
                  value={formatPercent(
                    (summary["worst_drawdown"] ??
                      summary["Worst Drawdown"] ??
                      summary["Max Drawdown"]) as number | null,
                  )}
                  trend="down"
                />
                <StatCard
                  label="Windows"
                  value={formatNumber(result.windows?.length ?? 0, 0)}
                />
              </div>

              {/* Tabs: Summary Table | Timeline */}
              <ChartCard title="Results">
                <Tabs defaultValue="summary">
                  <TabsList>
                    <TabsTrigger value="summary">Summary Table</TabsTrigger>
                    <TabsTrigger value="timeline">Timeline</TabsTrigger>
                  </TabsList>

                  <TabsContent value="summary" className="mt-4">
                    {result.summary_table &&
                    result.summary_table.length > 0 ? (
                      <DataTable
                        columns={buildSummaryColumns(result.summary_table)}
                        data={result.summary_table}
                      />
                    ) : (
                      <DataTable
                        columns={[
                          { key: "metric", label: "Metric" },
                          { key: "value", label: "Value" },
                        ]}
                        data={Object.entries(summary).map(([k, v]) => ({
                          metric: k
                            .replace(/_/g, " ")
                            .replace(/\b\w/g, (c) => c.toUpperCase()),
                          value:
                            v == null
                              ? "N/A"
                              : typeof v === "number"
                                ? Math.abs(v) < 1
                                  ? formatPercent(v)
                                  : formatNumber(v, 4)
                                : String(v),
                        }))}
                      />
                    )}
                  </TabsContent>

                  <TabsContent value="timeline" className="mt-4 space-y-4">
                    {/* CAGR per window bar chart */}
                    {timelineData && timelineData.length > 0 && (
                      <BarChartWrapper
                        data={timelineData as Record<string, unknown>[]}
                        xKey="window"
                        yKey="cagr"
                        height={300}
                        label="CAGR per Window"
                      />
                    )}

                    {/* Window details table */}
                    {result.windows && result.windows.length > 0 && (
                      <DataTable
                        columns={[
                          {
                            key: "window_id",
                            label: "Window",
                            format: (v) => `W${v}`,
                          },
                          { key: "train_start", label: "Train Start" },
                          { key: "train_end", label: "Train End" },
                          { key: "test_start", label: "Test Start" },
                          { key: "test_end", label: "Test End" },
                          {
                            key: "cagr",
                            label: "CAGR",
                            format: (v) =>
                              formatPercent(v as number | null),
                          },
                          {
                            key: "sharpe",
                            label: "Sharpe",
                            format: (v) =>
                              formatNumber(v as number | null, 3),
                          },
                          {
                            key: "max_drawdown",
                            label: "Max DD",
                            format: (v) =>
                              formatPercent(v as number | null),
                          },
                        ]}
                        data={
                          result.windows.map((w) => ({
                            window_id: w.window_id,
                            train_start: w.train_start,
                            train_end: w.train_end,
                            test_start: w.test_start,
                            test_end: w.test_end,
                            cagr:
                              w.metrics["CAGR"] ??
                              w.metrics["cagr"] ??
                              null,
                            sharpe:
                              w.metrics["Sharpe"] ??
                              w.metrics["sharpe"] ??
                              null,
                            max_drawdown:
                              w.metrics["Max Drawdown"] ??
                              w.metrics["max_drawdown"] ??
                              null,
                          })) as Record<string, unknown>[]
                        }
                      />
                    )}
                  </TabsContent>
                </Tabs>
              </ChartCard>
            </>
          )}

          {mutation.isError && (
            <InlineError
              message={mutation.error?.message ?? "Walk-forward analysis failed"}
              onRetry={handleRun}
            />
          )}

          {!mutation.isPending && !mutation.isError && !result && (
            <EmptyState
              icon={BarChart3}
              message="Configure parameters and click Run Walk-Forward to see results."
              presets={[
                { label: "SPY Rolling Windows", onClick: () => { setTickers("SPY"); setStrategy("NoRebalance"); setTrainWindow(504); setTestWindow(126); } },
              ]}
            />
          )}
      </ToolLayout>
    </div>
  );
}

/** Dynamically build columns from summary_table data keys. */
function buildSummaryColumns(
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
        if (Math.abs(v) < 1 && v !== 0) {
          return formatPercent(v);
        }
        return formatNumber(v, 4);
      }
      return String(v);
    },
  }));
}
