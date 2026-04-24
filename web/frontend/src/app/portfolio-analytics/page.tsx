"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
} from "@/components/common/loading-skeleton";
import { LineChartWrapper } from "@/components/charts/line-chart-wrapper";
import { AreaChartWrapper } from "@/components/charts/recharts-wrappers";
import { Heatmap } from "@/components/common/heatmap";
import { PieChart } from "lucide-react";
import { apiPost } from "@/lib/api";
import { formatPercent, formatNumber } from "@/lib/format";
import type {
  RollingMetricsRequest,
  RollingMetricsResponse,
  BenchmarkRequest,
  BenchmarkResponse,
  DrawdownRequest,
  DrawdownResponse,
  CorrelationRequest,
  CorrelationResponse,
} from "@/types/api";

// ---------------------------------------------------------------------------
// Tab 1 — Rolling Metrics
// ---------------------------------------------------------------------------

function RollingMetricsTab() {
  const [ticker, setTicker] = useState("SPY");
  const [benchmarkTicker, setBenchmarkTicker] = useState("");
  const [window, setWindow] = useState(63);
  const [riskFreeRate, setRiskFreeRate] = useState(0.04);
  const [startDate, setStartDate] = useState("2015-01-01");
  const [endDate, setEndDate] = useState("2024-12-31");

  const mutation = useMutation({
    mutationFn: (req: RollingMetricsRequest) =>
      apiPost<RollingMetricsResponse>("/api/portfolio-analytics/rolling", req),
    onSuccess: () => toast.success("Rolling metrics computed"),
    onError: (e) => toast.error(`Rolling metrics failed: ${e.message}`),
  });

  const handleRun = () => {
    const t = ticker.trim().toUpperCase();
    if (!t) {
      toast.error("Please enter a ticker.");
      return;
    }
    const req: RollingMetricsRequest = {
      ticker: t,
      window,
      risk_free_rate: riskFreeRate,
      start_date: startDate,
      end_date: endDate,
    };
    const bm = benchmarkTicker.trim().toUpperCase();
    if (bm) req.benchmark_ticker = bm;
    mutation.mutate(req);
  };

  const data = mutation.data;

  // Transform response arrays into chart data
  const chartData =
    data?.dates
      ?.map((date, i) => ({
        date,
        sharpe: data.sharpe[i],
        volatility: data.volatility[i],
        beta: data.beta ? data.beta[i] : null,
      }))
      .filter(
        (d) =>
          d.sharpe !== null || d.volatility !== null || d.beta !== null,
      ) ?? [];

  const series = [
    { key: "sharpe" },
    { key: "volatility" },
    ...(data?.beta ? [{ key: "beta" }] : []),
  ];

  return (
    <ToolLayout
      configPanel={
        <ConfigPanel title="Rolling Configuration">
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
            <Label className="text-xs text-muted-foreground">
              Benchmark Ticker (optional)
            </Label>
            <Input
              className="border-border/50 bg-background/50"
              value={benchmarkTicker}
              onChange={(e) => setBenchmarkTicker(e.target.value)}
              placeholder="e.g. SPY"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">
              Window (days)
            </Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              value={window}
              onChange={(e) => setWindow(Number(e.target.value))}
              min={5}
            />
            <p className="text-xs text-muted-foreground">
              Rolling window in trading days (63 = ~quarter)
            </p>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">
              Risk-Free Rate
            </Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              step={0.01}
              value={riskFreeRate}
              onChange={(e) => setRiskFreeRate(Number(e.target.value))}
              min={0}
              max={1}
            />
          </div>

          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">
                Start Date
              </Label>
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

          <Button
            className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
            onClick={handleRun}
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "Computing..." : "Run Rolling Metrics"}
          </Button>
        </ConfigPanel>
      }
    >
      {mutation.isPending && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </div>
          <ChartSkeleton />
        </>
      )}

      {data && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <StatCard
              label="Mean Rolling Sharpe"
              value={formatNumber(data.mean_sharpe, 3)}
              trend={
                data.mean_sharpe != null && data.mean_sharpe > 0
                  ? "up"
                  : "down"
              }
            />
            <StatCard
              label="Mean Rolling Vol"
              value={formatPercent(data.mean_vol)}
              trend="neutral"
            />
            {data.mean_beta != null && (
              <StatCard
                label="Mean Rolling Beta"
                value={formatNumber(data.mean_beta, 3)}
                trend={data.mean_beta > 1 ? "up" : "down"}
              />
            )}
          </div>

          {chartData.length > 0 && (
            <ChartCard title="Rolling Metrics Over Time">
              <LineChartWrapper
                data={chartData as Record<string, unknown>[]}
                xKey="date"
                series={series}
                height={400}
                referenceY={0}
                referenceLabel="Zero"
              />
            </ChartCard>
          )}
        </>
      )}

      {mutation.isError && (
        <InlineError
          message={mutation.error?.message ?? "Rolling metrics failed"}
          onRetry={handleRun}
        />
      )}

      {!mutation.isPending && !mutation.isError && !data && (
        <EmptyState
          icon={PieChart}
          message="Configure parameters and click Run Rolling Metrics to see results."
          presets={[
            {
              label: "SPY vs SPY (63-day)",
              onClick: () => {
                setTicker("SPY");
                setBenchmarkTicker("SPY");
                setWindow(63);
              },
            },
            {
              label: "QQQ (126-day)",
              onClick: () => {
                setTicker("QQQ");
                setBenchmarkTicker("");
                setWindow(126);
              },
            },
          ]}
        />
      )}
    </ToolLayout>
  );
}

// ---------------------------------------------------------------------------
// Tab 2 — Benchmark Analysis
// ---------------------------------------------------------------------------

function BenchmarkTab() {
  const [portfolioTicker, setPortfolioTicker] = useState("QQQ");
  const [benchmarkTicker, setBenchmarkTicker] = useState("SPY");
  const [riskFreeRate, setRiskFreeRate] = useState(0.04);
  const [startDate, setStartDate] = useState("2015-01-01");
  const [endDate, setEndDate] = useState("2024-12-31");

  const mutation = useMutation({
    mutationFn: (req: BenchmarkRequest) =>
      apiPost<BenchmarkResponse>("/api/portfolio-analytics/benchmark", req),
    onSuccess: () => toast.success("Benchmark analysis complete"),
    onError: (e) => toast.error(`Benchmark analysis failed: ${e.message}`),
  });

  const handleRun = () => {
    const pt = portfolioTicker.trim().toUpperCase();
    const bt = benchmarkTicker.trim().toUpperCase();
    if (!pt || !bt) {
      toast.error("Please enter both portfolio and benchmark tickers.");
      return;
    }
    mutation.mutate({
      portfolio_ticker: pt,
      benchmark_ticker: bt,
      risk_free_rate: riskFreeRate,
      start_date: startDate,
      end_date: endDate,
    });
  };

  const data = mutation.data;

  return (
    <ToolLayout
      configPanel={
        <ConfigPanel title="Benchmark Configuration">
          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">
              Portfolio Ticker
            </Label>
            <Input
              className="border-border/50 bg-background/50"
              value={portfolioTicker}
              onChange={(e) => setPortfolioTicker(e.target.value)}
              placeholder="e.g. QQQ"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">
              Benchmark Ticker
            </Label>
            <Input
              className="border-border/50 bg-background/50"
              value={benchmarkTicker}
              onChange={(e) => setBenchmarkTicker(e.target.value)}
              placeholder="e.g. SPY"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">
              Risk-Free Rate
            </Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              step={0.01}
              value={riskFreeRate}
              onChange={(e) => setRiskFreeRate(Number(e.target.value))}
              min={0}
              max={1}
            />
          </div>

          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">
                Start Date
              </Label>
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

          <Button
            className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
            onClick={handleRun}
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "Analyzing..." : "Run Benchmark Analysis"}
          </Button>
        </ConfigPanel>
      }
    >
      {mutation.isPending && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </div>
        </>
      )}

      {data && (
        <>
          {/* Row 1 */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <StatCard
              label="Alpha"
              value={formatPercent(data.alpha)}
              trend={
                data.alpha != null && data.alpha > 0 ? "up" : "down"
              }
            />
            <StatCard
              label="Beta"
              value={formatNumber(data.beta, 3)}
              trend="neutral"
            />
            <StatCard
              label="R-Squared"
              value={formatNumber(data.r_squared, 3)}
              trend="neutral"
            />
          </div>

          {/* Row 2 */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <StatCard
              label="Tracking Error"
              value={formatPercent(data.tracking_error)}
              trend="neutral"
            />
            <StatCard
              label="Information Ratio"
              value={formatNumber(data.information_ratio, 3)}
              trend={
                data.information_ratio != null && data.information_ratio > 0
                  ? "up"
                  : "down"
              }
            />
            <StatCard
              label="Up/Down Capture"
              value={`${formatPercent(data.up_capture)} / ${formatPercent(data.down_capture)}`}
              trend="neutral"
            />
          </div>
        </>
      )}

      {mutation.isError && (
        <InlineError
          message={mutation.error?.message ?? "Benchmark analysis failed"}
          onRetry={handleRun}
        />
      )}

      {!mutation.isPending && !mutation.isError && !data && (
        <EmptyState
          icon={PieChart}
          message="Configure parameters and click Run Benchmark Analysis to see results."
          presets={[
            {
              label: "QQQ vs SPY",
              onClick: () => {
                setPortfolioTicker("QQQ");
                setBenchmarkTicker("SPY");
              },
            },
            {
              label: "UPRO vs SPY",
              onClick: () => {
                setPortfolioTicker("UPRO");
                setBenchmarkTicker("SPY");
              },
            },
          ]}
        />
      )}
    </ToolLayout>
  );
}

// ---------------------------------------------------------------------------
// Tab 3 — Drawdown Analysis
// ---------------------------------------------------------------------------

function DrawdownTab() {
  const [ticker, setTicker] = useState("SPY");
  const [topN, setTopN] = useState(5);
  const [startDate, setStartDate] = useState("2015-01-01");
  const [endDate, setEndDate] = useState("2024-12-31");

  const mutation = useMutation({
    mutationFn: (req: DrawdownRequest) =>
      apiPost<DrawdownResponse>("/api/portfolio-analytics/drawdown", req),
    onSuccess: () => toast.success("Drawdown analysis complete"),
    onError: (e) => toast.error(`Drawdown analysis failed: ${e.message}`),
  });

  const handleRun = () => {
    const t = ticker.trim().toUpperCase();
    if (!t) {
      toast.error("Please enter a ticker.");
      return;
    }
    mutation.mutate({
      ticker: t,
      top_n: topN,
      start_date: startDate,
      end_date: endDate,
    });
  };

  const data = mutation.data;

  // Build underwater curve chart data
  const underwaterData =
    data?.underwater_curve
      ?.map((val, idx) => ({
        idx,
        drawdown: val,
      }))
      .filter((d) => d.drawdown !== null) ?? [];

  return (
    <ToolLayout
      configPanel={
        <ConfigPanel title="Drawdown Configuration">
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
            <Label className="text-xs text-muted-foreground">
              Top N Periods
            </Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              value={topN}
              onChange={(e) =>
                setTopN(Math.max(1, Math.min(10, Number(e.target.value))))
              }
              min={1}
              max={10}
            />
            <p className="text-xs text-muted-foreground">
              Number of worst drawdown periods to show (1-10)
            </p>
          </div>

          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">
                Start Date
              </Label>
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

          <Button
            className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
            onClick={handleRun}
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "Analyzing..." : "Run Drawdown Analysis"}
          </Button>
        </ConfigPanel>
      }
    >
      {mutation.isPending && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </div>
          <ChartSkeleton />
          <ChartSkeleton />
        </>
      )}

      {data && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              label="Max Drawdown"
              value={formatPercent(data.max_depth)}
              trend="down"
            />
            <StatCard
              label="Avg Drawdown"
              value={formatPercent(data.avg_depth)}
              trend="down"
            />
            <StatCard
              label="Total Periods"
              value={formatNumber(data.n_periods, 0)}
              trend="neutral"
            />
            <StatCard
              label="Current Drawdown"
              value={formatPercent(data.current_drawdown)}
              trend={
                data.current_drawdown != null && data.current_drawdown < 0
                  ? "down"
                  : "up"
              }
            />
          </div>

          {/* Underwater Curve */}
          {underwaterData.length > 0 && (
            <ChartCard title="Underwater Curve">
              <AreaChartWrapper
                data={underwaterData as Record<string, unknown>[]}
                xKey="idx"
                series={[{ key: "drawdown", color: "#ef4444" }]}
                height={350}
              />
            </ChartCard>
          )}

          {/* Drawdown Periods Table */}
          {data.periods && data.periods.length > 0 && (
            <ChartCard title="Drawdown Periods">
              <DataTable
                columns={[
                  {
                    key: "rank",
                    label: "Rank",
                    format: (v) => String(v),
                  },
                  {
                    key: "depth",
                    label: "Depth",
                    format: (v) => formatPercent(v as number | null),
                  },
                  {
                    key: "duration_bars",
                    label: "Duration (bars)",
                    format: (v) => formatNumber(v as number | null, 0),
                  },
                  {
                    key: "recovery_bars",
                    label: "Recovery (bars)",
                    format: (v) =>
                      v != null
                        ? formatNumber(v as number, 0)
                        : "Ongoing",
                  },
                  {
                    key: "start_idx",
                    label: "Start Idx",
                    format: (v) => formatNumber(v as number | null, 0),
                  },
                  {
                    key: "trough_idx",
                    label: "Trough Idx",
                    format: (v) => formatNumber(v as number | null, 0),
                  },
                ]}
                data={data.periods.map((p, i) => ({
                  rank: i + 1,
                  depth: p.depth,
                  duration_bars: p.duration_bars,
                  recovery_bars: p.recovery_bars,
                  start_idx: p.start_idx,
                  trough_idx: p.trough_idx,
                }))}
              />
            </ChartCard>
          )}
        </>
      )}

      {mutation.isError && (
        <InlineError
          message={mutation.error?.message ?? "Drawdown analysis failed"}
          onRetry={handleRun}
        />
      )}

      {!mutation.isPending && !mutation.isError && !data && (
        <EmptyState
          icon={PieChart}
          message="Configure parameters and click Run Drawdown Analysis to see results."
          presets={[
            {
              label: "SPY (Top 5)",
              onClick: () => {
                setTicker("SPY");
                setTopN(5);
              },
            },
            {
              label: "QQQ (Top 10)",
              onClick: () => {
                setTicker("QQQ");
                setTopN(10);
              },
            },
          ]}
        />
      )}
    </ToolLayout>
  );
}

// ---------------------------------------------------------------------------
// Tab 4 — Correlation
// ---------------------------------------------------------------------------

function CorrelationTab() {
  const [tickers, setTickers] = useState("SPY, QQQ, TLT, GLD");
  const [weights, setWeights] = useState("");
  const [startDate, setStartDate] = useState("2015-01-01");
  const [endDate, setEndDate] = useState("2024-12-31");

  const mutation = useMutation({
    mutationFn: (req: CorrelationRequest) =>
      apiPost<CorrelationResponse>("/api/portfolio-analytics/correlation", req),
    onSuccess: () => toast.success("Correlation analysis complete"),
    onError: (e) => toast.error(`Correlation analysis failed: ${e.message}`),
  });

  const handleRun = () => {
    const tickerList = tickers
      .split(",")
      .map((t) => t.trim().toUpperCase())
      .filter(Boolean);

    if (tickerList.length < 2) {
      toast.error("Please enter at least 2 tickers (comma-separated).");
      return;
    }

    const req: CorrelationRequest = {
      tickers: tickerList,
      start_date: startDate,
      end_date: endDate,
    };

    // Parse optional weights
    if (weights.trim()) {
      const weightValues = weights
        .split(",")
        .map((w) => parseFloat(w.trim()))
        .filter((w) => !isNaN(w));

      if (weightValues.length === tickerList.length) {
        const weightMap: Record<string, number> = {};
        tickerList.forEach((t, i) => {
          weightMap[t] = weightValues[i];
        });
        req.weights = weightMap;
      } else {
        toast.error(
          `Weights count (${weightValues.length}) does not match tickers count (${tickerList.length}).`,
        );
        return;
      }
    }

    mutation.mutate(req);
  };

  const data = mutation.data;

  // Build per-asset volatility table data
  const volTableData = data
    ? Object.entries(data.individual_vols).map(([asset, vol]) => ({
        asset,
        volatility: vol,
      }))
    : [];

  return (
    <ToolLayout
      configPanel={
        <ConfigPanel title="Correlation Configuration">
          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">
              Tickers (comma-separated)
            </Label>
            <Input
              className="border-border/50 bg-background/50"
              value={tickers}
              onChange={(e) => setTickers(e.target.value)}
              placeholder="e.g. SPY, QQQ, TLT, GLD"
            />
            <p className="text-xs text-muted-foreground">
              Minimum 2 tickers required
            </p>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">
              Weights (optional, comma-separated)
            </Label>
            <Input
              className="border-border/50 bg-background/50"
              value={weights}
              onChange={(e) => setWeights(e.target.value)}
              placeholder="e.g. 0.4, 0.3, 0.2, 0.1"
            />
            <p className="text-xs text-muted-foreground">
              Must match number of tickers. Equal weights if omitted.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">
                Start Date
              </Label>
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

          <Button
            className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
            onClick={handleRun}
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "Analyzing..." : "Run Correlation Analysis"}
          </Button>
        </ConfigPanel>
      }
    >
      {mutation.isPending && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </div>
          <ChartSkeleton />
          <ChartSkeleton />
        </>
      )}

      {data && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              label="HHI"
              value={formatNumber(data.herfindahl_index, 4)}
              trend="neutral"
            />
            <StatCard
              label="Effective N"
              value={formatNumber(data.effective_n, 2)}
              trend={
                data.effective_n != null && data.effective_n > 1
                  ? "up"
                  : "neutral"
              }
            />
            <StatCard
              label="Diversification Ratio"
              value={formatNumber(data.diversification_ratio, 3)}
              trend={
                data.diversification_ratio != null &&
                data.diversification_ratio > 1
                  ? "up"
                  : "neutral"
              }
            />
            <StatCard
              label="Avg Pairwise Corr"
              value={formatNumber(data.avg_pairwise_correlation, 3)}
              trend={
                data.avg_pairwise_correlation != null &&
                data.avg_pairwise_correlation < 0.5
                  ? "up"
                  : "down"
              }
            />
          </div>

          {/* Correlation Matrix Heatmap */}
          {data.correlation_matrix && (
            <ChartCard title="Correlation Matrix">
              <Heatmap
                labels={Object.keys(data.correlation_matrix)}
                matrix={data.correlation_matrix}
              />
            </ChartCard>
          )}

          {/* Individual Volatilities Table */}
          {volTableData.length > 0 && (
            <ChartCard title="Individual Volatilities">
              <DataTable
                columns={[
                  { key: "asset", label: "Asset" },
                  {
                    key: "volatility",
                    label: "Annualized Vol",
                    format: (v) => formatPercent(v as number | null),
                  },
                ]}
                data={volTableData}
              />
            </ChartCard>
          )}
        </>
      )}

      {mutation.isError && (
        <InlineError
          message={mutation.error?.message ?? "Correlation analysis failed"}
          onRetry={handleRun}
        />
      )}

      {!mutation.isPending && !mutation.isError && !data && (
        <EmptyState
          icon={PieChart}
          message="Configure parameters and click Run Correlation Analysis to see results."
          presets={[
            {
              label: "SPY, QQQ, TLT, GLD",
              onClick: () => {
                setTickers("SPY, QQQ, TLT, GLD");
                setWeights("");
              },
            },
            {
              label: "SPY, TLT (60/40)",
              onClick: () => {
                setTickers("SPY, TLT");
                setWeights("0.6, 0.4");
              },
            },
          ]}
        />
      )}
    </ToolLayout>
  );
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function PortfolioAnalyticsPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Portfolio Analytics"
        description="Rolling metrics, benchmark analysis, drawdown detection, and correlation analysis"
      />

      <Tabs defaultValue="rolling" className="space-y-6">
        <TabsList>
          <TabsTrigger value="rolling">Rolling Metrics</TabsTrigger>
          <TabsTrigger value="benchmark">Benchmark Analysis</TabsTrigger>
          <TabsTrigger value="drawdown">Drawdown Analysis</TabsTrigger>
          <TabsTrigger value="correlation">Correlation</TabsTrigger>
        </TabsList>

        <TabsContent value="rolling">
          <RollingMetricsTab />
        </TabsContent>

        <TabsContent value="benchmark">
          <BenchmarkTab />
        </TabsContent>

        <TabsContent value="drawdown">
          <DrawdownTab />
        </TabsContent>

        <TabsContent value="correlation">
          <CorrelationTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
