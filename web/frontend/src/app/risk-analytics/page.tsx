"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
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
import { BarChartWrapper } from "@/components/charts/recharts-wrappers";
import { Shield } from "lucide-react";
import { apiPost } from "@/lib/api";
import { formatPercent, formatNumber, formatCurrency } from "@/lib/format";
import type {
  VaRRequest,
  VaRResponse,
  StressTestRequest,
  StressTestResponse,
  KellyRequest,
  KellyResponse,
  MultiKellyRequest,
  MultiKellyResponse,
} from "@/types/api";

// ---------------------------------------------------------------------------
// Scenario metadata
// ---------------------------------------------------------------------------
const STRESS_SCENARIOS: { key: string; label: string }[] = [
  { key: "2008_financial_crisis", label: "2008 Financial Crisis" },
  { key: "covid_crash_2020", label: "COVID Crash 2020" },
  { key: "dot_com_bubble", label: "Dot-Com Bubble" },
  { key: "black_monday_1987", label: "Black Monday 1987" },
];

// ===========================================================================
// Tab 1: VaR / CVaR
// ===========================================================================
function VaRTab() {
  const [ticker, setTicker] = useState("SPY");
  const [confidence, setConfidence] = useState(0.95);
  const [horizonDays, setHorizonDays] = useState("1");
  const [portfolioValue, setPortfolioValue] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const mutation = useMutation({
    mutationFn: (req: VaRRequest) =>
      apiPost<VaRResponse>("/api/risk-analytics/var", req, 120000),
    onSuccess: () => toast.success("VaR analysis complete"),
    onError: (e) => toast.error(`VaR analysis failed: ${e.message}`),
  });

  const handleRun = () => {
    const req: VaRRequest = {
      ticker: ticker.toUpperCase(),
      confidence,
      horizon_days: Number(horizonDays),
    };
    if (portfolioValue) req.portfolio_value = Number(portfolioValue);
    if (startDate) req.start_date = startDate;
    if (endDate) req.end_date = endDate;
    mutation.mutate(req);
  };

  const data = mutation.data;
  const hasDollarVaR = portfolioValue && data;

  // Chart data for method comparison
  const chartData =
    data
      ? [
          {
            method: "Historical",
            var_pct: Math.abs(data.historical.var_ ?? 0),
          },
          {
            method: "Parametric",
            var_pct: Math.abs(data.parametric.var_ ?? 0),
          },
          {
            method: "Monte Carlo",
            var_pct: Math.abs(data.montecarlo.var_ ?? 0),
          },
        ]
      : [];

  return (
    <ToolLayout
      configPanel={
        <ConfigPanel title="VaR Configuration">
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
              Confidence Level: {(confidence * 100).toFixed(0)}%
            </Label>
            <Slider
              value={[confidence]}
              onValueChange={([v]) => setConfidence(v)}
              min={0.9}
              max={0.99}
              step={0.01}
            />
            <p className="text-xs text-muted-foreground">
              Higher values give more conservative risk estimates
            </p>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">
              Horizon (Days)
            </Label>
            <Select value={horizonDays} onValueChange={setHorizonDays}>
              <SelectTrigger className="border-border/50 bg-background/50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                <SelectItem value="1">1 Day</SelectItem>
                <SelectItem value="5">5 Days</SelectItem>
                <SelectItem value="10">10 Days</SelectItem>
                <SelectItem value="21">21 Days</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">
              Portfolio Value ($)
            </Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              value={portfolioValue}
              onChange={(e) => setPortfolioValue(e.target.value)}
              placeholder="Optional, e.g. 100000"
            />
            <p className="text-xs text-muted-foreground">
              Leave blank for percentage-only results
            </p>
          </div>

          <div className="grid grid-cols-2 gap-2">
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
            {mutation.isPending ? "Running..." : "Run Analysis"}
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
        </>
      )}

      {data && !mutation.isPending && (
        <>
          {/* Primary stat cards */}
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard
              label="Historical VaR"
              value={formatPercent(data.historical.var_)}
              trend="down"
            />
            <StatCard
              label="Parametric VaR"
              value={formatPercent(data.parametric.var_)}
              trend="down"
            />
            <StatCard
              label="Monte Carlo VaR"
              value={formatPercent(data.montecarlo.var_)}
              trend="down"
            />
            <StatCard
              label="CVaR (Expected Shortfall)"
              value={formatPercent(data.cvar.cvar)}
              trend="down"
            />
          </div>

          {/* Dollar VaR cards when portfolio value is specified */}
          {hasDollarVaR && (
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
              <StatCard
                label="Historical VaR ($)"
                value={formatCurrency(data.historical.var_dollars)}
                trend="down"
              />
              <StatCard
                label="Parametric VaR ($)"
                value={formatCurrency(data.parametric.var_dollars)}
                trend="down"
              />
              <StatCard
                label="Monte Carlo VaR ($)"
                value={formatCurrency(data.montecarlo.var_dollars)}
                trend="down"
              />
            </div>
          )}

          {/* Method comparison chart */}
          {chartData.length > 0 && (
            <ChartCard title="VaR Method Comparison">
              <BarChartWrapper
                data={chartData as Record<string, unknown>[]}
                xKey="method"
                yKey="var_pct"
                height={300}
                label={`${Number(horizonDays)}-Day VaR at ${(confidence * 100).toFixed(0)}% Confidence`}
              />
            </ChartCard>
          )}

          {/* Observation details */}
          <ChartCard title="Analysis Details">
            <DataTable
              columns={[
                { key: "metric", label: "Metric" },
                { key: "value", label: "Value" },
              ]}
              data={[
                {
                  metric: "Observations",
                  value: formatNumber(data.historical.n_observations, 0),
                },
                {
                  metric: "Confidence Level",
                  value: formatPercent(data.historical.confidence),
                },
                {
                  metric: "Horizon (Days)",
                  value: formatNumber(data.historical.horizon_days, 0),
                },
                {
                  metric: "CVaR Tail Observations",
                  value: formatNumber(data.cvar.n_tail_obs, 0),
                },
              ]}
            />
          </ChartCard>
        </>
      )}

      {mutation.isError && (
        <InlineError
          message={mutation.error?.message ?? "VaR analysis failed"}
          onRetry={handleRun}
        />
      )}

      {!mutation.isPending && !mutation.isError && !data && (
        <EmptyState
          icon={Shield}
          message="Configure parameters and click Run Analysis to see VaR results."
          presets={[
            {
              label: "SPY VaR",
              onClick: () => {
                setTicker("SPY");
                setConfidence(0.95);
                setHorizonDays("1");
              },
            },
            {
              label: "QQQ 10-Day VaR",
              onClick: () => {
                setTicker("QQQ");
                setConfidence(0.99);
                setHorizonDays("10");
              },
            },
          ]}
        />
      )}
    </ToolLayout>
  );
}

// ===========================================================================
// Tab 2: Stress Testing
// ===========================================================================
function StressTestTab() {
  const [ticker, setTicker] = useState("SPY");
  const [initialValue, setInitialValue] = useState(100000);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [enabledScenarios, setEnabledScenarios] = useState<
    Record<string, boolean>
  >({
    "2008_financial_crisis": true,
    covid_crash_2020: true,
    dot_com_bubble: true,
    black_monday_1987: true,
  });

  const toggleScenario = (key: string) => {
    setEnabledScenarios((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const mutation = useMutation({
    mutationFn: (req: StressTestRequest) =>
      apiPost<StressTestResponse>(
        "/api/risk-analytics/stress",
        req,
        120000,
      ),
    onSuccess: () => toast.success("Stress test complete"),
    onError: (e) => toast.error(`Stress test failed: ${e.message}`),
  });

  const handleRun = () => {
    const selectedScenarios = Object.entries(enabledScenarios)
      .filter(([, enabled]) => enabled)
      .map(([key]) => key);

    if (selectedScenarios.length === 0) {
      toast.error("Please select at least one scenario.");
      return;
    }

    const req: StressTestRequest = {
      ticker: ticker.toUpperCase(),
      scenarios: selectedScenarios,
      initial_value: initialValue,
    };
    if (startDate) req.start_date = startDate;
    if (endDate) req.end_date = endDate;
    mutation.mutate(req);
  };

  const data = mutation.data;
  const results = data?.results;

  // Find worst scenario
  const worstResult = results?.reduce(
    (worst, r) =>
      (r.max_drawdown_pct ?? 0) < (worst?.max_drawdown_pct ?? 0) ? r : worst,
    results[0],
  );

  // Chart data for scenario comparison
  const drawdownChartData =
    results?.map((r) => ({
      scenario: r.scenario_name,
      max_drawdown_pct: Math.abs(r.max_drawdown_pct ?? 0),
    })) ?? [];

  return (
    <ToolLayout
      configPanel={
        <ConfigPanel title="Stress Test Configuration">
          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Ticker</Label>
            <Input
              className="border-border/50 bg-background/50"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              placeholder="e.g. SPY"
            />
          </div>

          <div className="space-y-3">
            <Label className="text-xs text-muted-foreground">Scenarios</Label>
            {STRESS_SCENARIOS.map((s) => (
              <div
                key={s.key}
                className="flex items-center justify-between"
              >
                <Label className="text-xs text-muted-foreground">
                  {s.label}
                </Label>
                <Switch
                  checked={enabledScenarios[s.key] ?? false}
                  onCheckedChange={() => toggleScenario(s.key)}
                />
              </div>
            ))}
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">
              Initial Value ($)
            </Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              value={initialValue}
              onChange={(e) => setInitialValue(Number(e.target.value))}
              min={1}
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
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
            {mutation.isPending ? "Running..." : "Run Stress Test"}
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
        </>
      )}

      {results && results.length > 0 && !mutation.isPending && (
        <>
          {/* Worst scenario stat cards */}
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard
              label="Worst Scenario"
              value={worstResult?.scenario_name ?? "N/A"}
            />
            <StatCard
              label="Worst Drawdown"
              value={formatPercent(worstResult?.max_drawdown_pct ?? null)}
              trend="down"
            />
            <StatCard
              label="Trough Value"
              value={formatCurrency(worstResult?.trough_value ?? null)}
              trend="down"
            />
            <StatCard
              label="Recovery Days"
              value={formatNumber(worstResult?.recovery_days ?? null, 0)}
            />
          </div>

          {/* Scenario comparison chart */}
          {drawdownChartData.length > 0 && (
            <ChartCard title="Scenario Comparison">
              <BarChartWrapper
                data={drawdownChartData as Record<string, unknown>[]}
                xKey="scenario"
                yKey="max_drawdown_pct"
                height={300}
                label="Max Drawdown (%) by Scenario"
              />
            </ChartCard>
          )}

          {/* Details table */}
          <ChartCard title="Scenario Details">
            <DataTable
              columns={[
                { key: "scenario_name", label: "Scenario" },
                {
                  key: "trough_value",
                  label: "Trough Value",
                  format: (v) => formatCurrency(v as number | null),
                },
                {
                  key: "max_drawdown_pct",
                  label: "Max Drawdown",
                  format: (v) => formatPercent(v as number | null),
                },
                {
                  key: "shock_duration_days",
                  label: "Shock Duration (Days)",
                  format: (v) => formatNumber(v as number | null, 0),
                },
                {
                  key: "recovery_days",
                  label: "Recovery (Days)",
                  format: (v) => formatNumber(v as number | null, 0),
                },
              ]}
              data={results as unknown as Record<string, unknown>[]}
            />
          </ChartCard>
        </>
      )}

      {mutation.isError && (
        <InlineError
          message={mutation.error?.message ?? "Stress test failed"}
          onRetry={handleRun}
        />
      )}

      {!mutation.isPending && !mutation.isError && !results && (
        <EmptyState
          icon={Shield}
          message="Configure parameters and click Run Stress Test to see scenario results."
          presets={[
            {
              label: "SPY All Scenarios",
              onClick: () => {
                setTicker("SPY");
                setEnabledScenarios({
                  "2008_financial_crisis": true,
                  covid_crash_2020: true,
                  dot_com_bubble: true,
                  black_monday_1987: true,
                });
              },
            },
            {
              label: "QQQ Crisis Scenarios",
              onClick: () => {
                setTicker("QQQ");
                setEnabledScenarios({
                  "2008_financial_crisis": true,
                  covid_crash_2020: true,
                  dot_com_bubble: false,
                  black_monday_1987: false,
                });
              },
            },
          ]}
        />
      )}
    </ToolLayout>
  );
}

// ===========================================================================
// Tab 3: Kelly Criterion
// ===========================================================================
function KellyTab() {
  const [multiAsset, setMultiAsset] = useState(false);

  // Single-asset state
  const [ticker, setTicker] = useState("SPY");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  // Multi-asset state
  const [tickers, setTickers] = useState("SPY, TLT, GLD");
  const [multiStartDate, setMultiStartDate] = useState("");
  const [multiEndDate, setMultiEndDate] = useState("");

  // Single-asset mutation
  const kellyMutation = useMutation({
    mutationFn: (req: KellyRequest) =>
      apiPost<KellyResponse>("/api/risk-analytics/kelly", req, 120000),
    onSuccess: () => toast.success("Kelly analysis complete"),
    onError: (e) => toast.error(`Kelly analysis failed: ${e.message}`),
  });

  // Multi-asset mutation
  const multiKellyMutation = useMutation({
    mutationFn: (req: MultiKellyRequest) =>
      apiPost<MultiKellyResponse>(
        "/api/risk-analytics/kelly-multi",
        req,
        120000,
      ),
    onSuccess: () => toast.success("Multi-asset Kelly analysis complete"),
    onError: (e) =>
      toast.error(`Multi-asset Kelly failed: ${e.message}`),
  });

  const handleRunSingle = () => {
    const req: KellyRequest = {
      ticker: ticker.toUpperCase(),
    };
    if (startDate) req.start_date = startDate;
    if (endDate) req.end_date = endDate;
    kellyMutation.mutate(req);
  };

  const handleRunMulti = () => {
    const tickerList = tickers
      .split(",")
      .map((t) => t.trim().toUpperCase())
      .filter((t) => t !== "");

    if (tickerList.length < 2) {
      toast.error("Please enter at least two tickers.");
      return;
    }

    const req: MultiKellyRequest = {
      tickers: tickerList,
    };
    if (multiStartDate) req.start_date = multiStartDate;
    if (multiEndDate) req.end_date = multiEndDate;
    multiKellyMutation.mutate(req);
  };

  const singleData = kellyMutation.data;
  const multiData = multiKellyMutation.data;

  // Single-asset chart data
  const kellyChartData = singleData
    ? [
        { fraction: "Full Kelly", value: singleData.full_kelly ?? 0 },
        { fraction: "Half Kelly", value: singleData.half_kelly ?? 0 },
        { fraction: "Quarter Kelly", value: singleData.quarter_kelly ?? 0 },
      ]
    : [];

  // Multi-asset chart data
  const multiChartData = multiData
    ? Object.entries(multiData.half_kelly_weights).map(([asset, weight]) => ({
        asset,
        half_kelly: weight,
      }))
    : [];

  // Multi-asset table data
  const multiTableData = multiData
    ? Object.entries(multiData.weights).map(([asset, weight]) => ({
        asset,
        full_kelly: multiData.full_kelly_weights[asset] ?? 0,
        half_kelly: multiData.half_kelly_weights[asset] ?? 0,
        weight,
      }))
    : [];

  return (
    <ToolLayout
      configPanel={
        <ConfigPanel title="Kelly Criterion Configuration">
          <div className="flex items-center justify-between">
            <Label className="text-xs text-muted-foreground">
              {multiAsset ? "Multi-Asset Mode" : "Single Asset Mode"}
            </Label>
            <Switch
              checked={multiAsset}
              onCheckedChange={setMultiAsset}
            />
          </div>
          <p className="text-xs text-muted-foreground">
            {multiAsset
              ? "Compute optimal Kelly weights for a portfolio of assets."
              : "Compute optimal Kelly fraction for a single asset."}
          </p>

          {!multiAsset ? (
            <>
              <div className="space-y-2">
                <Label className="text-xs text-muted-foreground">
                  Ticker
                </Label>
                <Input
                  className="border-border/50 bg-background/50"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value)}
                  placeholder="e.g. SPY"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
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
                  <Label className="text-xs text-muted-foreground">
                    End Date
                  </Label>
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
                onClick={handleRunSingle}
                disabled={kellyMutation.isPending}
              >
                {kellyMutation.isPending ? "Running..." : "Run Analysis"}
              </Button>
            </>
          ) : (
            <>
              <div className="space-y-2">
                <Label className="text-xs text-muted-foreground">
                  Tickers
                </Label>
                <Input
                  className="border-border/50 bg-background/50"
                  value={tickers}
                  onChange={(e) => setTickers(e.target.value)}
                  placeholder="e.g. SPY, TLT, GLD"
                />
                <p className="text-xs text-muted-foreground">
                  Comma-separated list (at least 2)
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">
                    Start Date
                  </Label>
                  <Input
                    className="border-border/50 bg-background/50"
                    type="date"
                    value={multiStartDate}
                    onChange={(e) => setMultiStartDate(e.target.value)}
                  />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">
                    End Date
                  </Label>
                  <Input
                    className="border-border/50 bg-background/50"
                    type="date"
                    value={multiEndDate}
                    onChange={(e) => setMultiEndDate(e.target.value)}
                  />
                </div>
              </div>

              <Button
                className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
                onClick={handleRunMulti}
                disabled={multiKellyMutation.isPending}
              >
                {multiKellyMutation.isPending ? "Running..." : "Run Analysis"}
              </Button>
            </>
          )}
        </ConfigPanel>
      }
    >
      {/* Single-asset loading */}
      {!multiAsset && kellyMutation.isPending && (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </div>
          <ChartSkeleton />
        </>
      )}

      {/* Single-asset results */}
      {!multiAsset && singleData && !kellyMutation.isPending && (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard
              label="Full Kelly"
              value={formatPercent(singleData.full_kelly)}
              trend={
                singleData.full_kelly != null && singleData.full_kelly > 0
                  ? "up"
                  : "down"
              }
            />
            <StatCard
              label="Half Kelly"
              value={formatPercent(singleData.half_kelly)}
              trend={
                singleData.half_kelly != null && singleData.half_kelly > 0
                  ? "up"
                  : "down"
              }
            />
            <StatCard
              label="Quarter Kelly"
              value={formatPercent(singleData.quarter_kelly)}
              trend={
                singleData.quarter_kelly != null &&
                singleData.quarter_kelly > 0
                  ? "up"
                  : "down"
              }
            />
            <StatCard
              label="Win Rate"
              value={formatPercent(singleData.win_rate)}
              trend={
                singleData.win_rate != null && singleData.win_rate > 0.5
                  ? "up"
                  : "down"
              }
            />
          </div>

          {/* Kelly fractions chart */}
          {kellyChartData.length > 0 && (
            <ChartCard title="Kelly Fractions">
              <BarChartWrapper
                data={kellyChartData as Record<string, unknown>[]}
                xKey="fraction"
                yKey="value"
                height={300}
                label="Optimal Allocation Fractions"
              />
            </ChartCard>
          )}

          {/* Extra details */}
          <ChartCard title="Analysis Details">
            <DataTable
              columns={[
                { key: "metric", label: "Metric" },
                { key: "value", label: "Value" },
              ]}
              data={[
                {
                  metric: "Win/Loss Ratio",
                  value: formatNumber(singleData.win_loss_ratio, 3),
                },
                {
                  metric: "Expected Value",
                  value: formatPercent(singleData.expected_value),
                },
                {
                  metric: "Positive EV",
                  value: singleData.is_positive_ev ? "Yes" : "No",
                },
                {
                  metric: "Observations",
                  value: formatNumber(singleData.n_observations, 0),
                },
              ]}
            />
          </ChartCard>
        </>
      )}

      {/* Single-asset error */}
      {!multiAsset && kellyMutation.isError && (
        <InlineError
          message={kellyMutation.error?.message ?? "Kelly analysis failed"}
          onRetry={handleRunSingle}
        />
      )}

      {/* Single-asset empty */}
      {!multiAsset &&
        !kellyMutation.isPending &&
        !kellyMutation.isError &&
        !singleData && (
          <EmptyState
            icon={Shield}
            message="Configure parameters and click Run Analysis to see Kelly criterion results."
            presets={[
              {
                label: "SPY Kelly",
                onClick: () => {
                  setTicker("SPY");
                },
              },
              {
                label: "QQQ Kelly",
                onClick: () => {
                  setTicker("QQQ");
                },
              },
            ]}
          />
        )}

      {/* Multi-asset loading */}
      {multiAsset && multiKellyMutation.isPending && (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <CardSkeleton />
            <CardSkeleton />
          </div>
          <ChartSkeleton />
        </>
      )}

      {/* Multi-asset results */}
      {multiAsset && multiData && !multiKellyMutation.isPending && (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard
              label="Assets"
              value={formatNumber(multiData.n_assets, 0)}
            />
            <StatCard
              label="Observations"
              value={formatNumber(multiData.n_observations, 0)}
            />
          </div>

          {/* Weight allocation table */}
          <ChartCard title="Kelly Weights by Asset">
            <DataTable
              columns={[
                { key: "asset", label: "Asset" },
                {
                  key: "full_kelly",
                  label: "Full Kelly",
                  format: (v) => formatPercent(v as number | null),
                },
                {
                  key: "half_kelly",
                  label: "Half Kelly",
                  format: (v) => formatPercent(v as number | null),
                },
                {
                  key: "weight",
                  label: "Normalized Weight",
                  format: (v) => formatPercent(v as number | null),
                },
              ]}
              data={multiTableData as Record<string, unknown>[]}
            />
          </ChartCard>

          {/* Half-Kelly weights chart */}
          {multiChartData.length > 0 && (
            <ChartCard title="Half Kelly Weights">
              <BarChartWrapper
                data={multiChartData as Record<string, unknown>[]}
                xKey="asset"
                yKey="half_kelly"
                height={300}
                label="Half Kelly Weight per Asset"
              />
            </ChartCard>
          )}
        </>
      )}

      {/* Multi-asset error */}
      {multiAsset && multiKellyMutation.isError && (
        <InlineError
          message={
            multiKellyMutation.error?.message ??
            "Multi-asset Kelly analysis failed"
          }
          onRetry={handleRunMulti}
        />
      )}

      {/* Multi-asset empty */}
      {multiAsset &&
        !multiKellyMutation.isPending &&
        !multiKellyMutation.isError &&
        !multiData && (
          <EmptyState
            icon={Shield}
            message="Enter tickers and click Run Analysis to see multi-asset Kelly weights."
            presets={[
              {
                label: "SPY + TLT + GLD",
                onClick: () => {
                  setTickers("SPY, TLT, GLD");
                },
              },
              {
                label: "SPY + QQQ + IWM + EFA",
                onClick: () => {
                  setTickers("SPY, QQQ, IWM, EFA");
                },
              },
            ]}
          />
        )}
    </ToolLayout>
  );
}

// ===========================================================================
// Main Page
// ===========================================================================
export default function RiskAnalyticsPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Risk Analytics"
        description="Value-at-Risk, stress testing, and Kelly criterion analysis for portfolio risk management"
      />

      <Tabs defaultValue="var">
        <TabsList className="bg-muted/30">
          <TabsTrigger value="var">VaR / CVaR</TabsTrigger>
          <TabsTrigger value="stress">Stress Testing</TabsTrigger>
          <TabsTrigger value="kelly">Kelly Criterion</TabsTrigger>
        </TabsList>

        <TabsContent value="var" className="mt-6">
          <VaRTab />
        </TabsContent>

        <TabsContent value="stress" className="mt-6">
          <StressTestTab />
        </TabsContent>

        <TabsContent value="kelly" className="mt-6">
          <KellyTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
