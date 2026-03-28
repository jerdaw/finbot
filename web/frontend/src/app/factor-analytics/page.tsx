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
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
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
import { LineChartWrapper } from "@/components/charts/line-chart-wrapper";
import { Layers } from "lucide-react";
import { apiPost } from "@/lib/api";
import { formatPercent, formatNumber } from "@/lib/format";
import type {
  FactorRegressionRequest,
  FactorRegressionResponse,
  FactorAttributionResponse,
  FactorRiskResponse,
  RollingRSquaredResponse,
} from "@/types/api";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function parseFactorNames(raw: string): string[] {
  return raw
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s !== "");
}

function tryParseJSON(raw: string): Record<string, number>[] | null {
  if (!raw.trim()) return null;
  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return null;
    return parsed as Record<string, number>[];
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Page component
// ---------------------------------------------------------------------------

export default function FactorAnalyticsPage() {
  // --- Config state ---
  const [ticker, setTicker] = useState("SPY");
  const [modelType, setModelType] = useState("auto");
  const [factorNamesRaw, setFactorNamesRaw] = useState("Mkt-RF, SMB, HML");
  const [factorDataRaw, setFactorDataRaw] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  // --- Shared result state ---
  const [regressionData, setRegressionData] =
    useState<FactorRegressionResponse | null>(null);
  const [attributionData, setAttributionData] =
    useState<FactorAttributionResponse | null>(null);
  const [riskData, setRiskData] = useState<FactorRiskResponse | null>(null);
  const [rollingData, setRollingData] =
    useState<RollingRSquaredResponse | null>(null);

  // --- Mutations ---
  const regressionMutation = useMutation({
    mutationFn: (req: FactorRegressionRequest) =>
      apiPost<FactorRegressionResponse>(
        "/api/factor-analytics/regression",
        req,
      ),
  });

  const attributionMutation = useMutation({
    mutationFn: (req: FactorRegressionRequest) =>
      apiPost<FactorAttributionResponse>(
        "/api/factor-analytics/attribution",
        req,
      ),
  });

  const riskMutation = useMutation({
    mutationFn: (req: FactorRegressionRequest) =>
      apiPost<FactorRiskResponse>("/api/factor-analytics/risk", req),
  });

  const rollingMutation = useMutation({
    mutationFn: (req: FactorRegressionRequest) =>
      apiPost<RollingRSquaredResponse>(
        "/api/factor-analytics/rolling-r-squared",
        req,
      ),
  });

  // --- Build request ---
  const buildRequest = (): FactorRegressionRequest | null => {
    const parsedFactorNames = parseFactorNames(factorNamesRaw);
    if (parsedFactorNames.length === 0) {
      toast.error("Please enter at least one factor name.");
      return null;
    }

    let parsedFactorData: Record<string, number>[] | undefined;
    if (factorDataRaw.trim()) {
      const parsed = tryParseJSON(factorDataRaw);
      if (!parsed) {
        toast.error(
          "Invalid factor data JSON. Expected an array of objects, e.g. " +
            '[{"Mkt-RF": 0.01, "SMB": -0.005}]',
        );
        return null;
      }
      parsedFactorData = parsed;
    }

    return {
      ticker: ticker.trim().toUpperCase(),
      factor_data: parsedFactorData ?? [],
      factor_names: parsedFactorNames,
      model_type: modelType === "auto" ? undefined : modelType,
      start_date: startDate || undefined,
      end_date: endDate || undefined,
    };
  };

  // --- Run All handler ---
  const handleRunAll = async () => {
    const req = buildRequest();
    if (!req) return;

    try {
      const reg = await regressionMutation.mutateAsync(req);
      setRegressionData(reg);

      const [attr, risk, rolling] = await Promise.all([
        attributionMutation.mutateAsync(req),
        riskMutation.mutateAsync(req),
        rollingMutation.mutateAsync(req).catch(() => null),
      ]);

      setAttributionData(attr);
      setRiskData(risk);
      setRollingData(rolling);

      toast.success("Factor analysis complete");
    } catch (e) {
      toast.error(`Analysis failed: ${(e as Error).message}`);
    }
  };

  const isPending =
    regressionMutation.isPending ||
    attributionMutation.isPending ||
    riskMutation.isPending;

  const hasError =
    regressionMutation.isError &&
    !regressionMutation.isPending;

  // --- Build chart data for regression tab ---
  const loadingsChartData = regressionData
    ? regressionData.factor_names.map((f) => ({
        factor: f,
        loading: regressionData.loadings[f] ?? 0,
      }))
    : [];

  const regressionTableData = regressionData
    ? regressionData.factor_names.map((f) => ({
        factor: f,
        loading: regressionData.loadings[f],
        t_stat: regressionData.t_stats[f],
        p_value: regressionData.p_values[f],
      }))
    : [];

  // --- Build chart data for attribution tab ---
  const attributionChartData = attributionData
    ? [
        ...attributionData.factor_names.map((f) => ({
          name: f,
          contribution: attributionData.factor_contributions[f] ?? 0,
        })),
        {
          name: "Alpha",
          contribution: attributionData.alpha_contribution ?? 0,
        },
      ]
    : [];

  const attributionTableData = attributionData
    ? [
        ...attributionData.factor_names.map((f) => ({
          factor: f,
          contribution: attributionData.factor_contributions[f],
        })),
        {
          factor: "Alpha (Residual)",
          contribution: attributionData.alpha_contribution,
        },
      ]
    : [];

  // --- Build chart data for risk tab ---
  const riskChartData = riskData
    ? [
        { type: "Systematic", value: riskData.systematic_variance ?? 0 },
        { type: "Idiosyncratic", value: riskData.idiosyncratic_variance ?? 0 },
      ]
    : [];

  const riskTableData = riskData
    ? riskData.factor_names.map((f) => ({
        factor: f,
        marginal_contribution: riskData.marginal_contributions[f],
      }))
    : [];

  // --- Build rolling R-squared chart data ---
  const rollingChartData = rollingData
    ? rollingData.dates.map((d, i) => ({
        date: d,
        r_squared: rollingData.values[i],
      }))
    : [];

  return (
    <div className="space-y-8">
      <PageHeader
        title="Factor Analytics"
        description="Fama-French style factor regression, return attribution, and risk decomposition"
      />

      <Tabs defaultValue="regression" className="space-y-6">
        <TabsList>
          <TabsTrigger value="regression">Factor Regression</TabsTrigger>
          <TabsTrigger value="attribution">Return Attribution</TabsTrigger>
          <TabsTrigger value="risk">Risk Decomposition</TabsTrigger>
        </TabsList>

        {/* ================================================================
            Tab 1: Factor Regression
            ================================================================ */}
        <TabsContent value="regression" className="mt-0 space-y-0">
          <ToolLayout
            configPanel={
              <ConfigPanel title="Configuration">
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

                <div className="space-y-2">
                  <Label className="text-xs text-muted-foreground">
                    Model Type
                  </Label>
                  <Select value={modelType} onValueChange={setModelType}>
                    <SelectTrigger className="border-border/50 bg-background/50">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                      <SelectItem value="auto">Auto Detect</SelectItem>
                      <SelectItem value="CAPM">CAPM</SelectItem>
                      <SelectItem value="FF3">FF3</SelectItem>
                      <SelectItem value="FF5">FF5</SelectItem>
                      <SelectItem value="CUSTOM">CUSTOM</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label className="text-xs text-muted-foreground">
                    Factor Names
                  </Label>
                  <Input
                    className="border-border/50 bg-background/50"
                    value={factorNamesRaw}
                    onChange={(e) => setFactorNamesRaw(e.target.value)}
                    placeholder="e.g. Mkt-RF, SMB, HML"
                  />
                  <p className="text-xs text-muted-foreground">
                    Comma-separated factor names
                  </p>
                </div>

                <div className="space-y-2">
                  <Label className="text-xs text-muted-foreground">
                    Factor Data (JSON)
                  </Label>
                  <textarea
                    className="flex min-h-[80px] w-full rounded-md border border-border/50 bg-background/50 px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    value={factorDataRaw}
                    onChange={(e) => setFactorDataRaw(e.target.value)}
                    placeholder='[{"Mkt-RF": 0.01, "SMB": -0.005, "HML": 0.003}, ...]'
                    rows={4}
                  />
                  <p className="text-xs text-muted-foreground">
                    Paste factor returns as JSON array of objects
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
                  onClick={handleRunAll}
                  disabled={isPending}
                >
                  {isPending ? "Running..." : "Run All"}
                </Button>
              </ConfigPanel>
            }
          >
            {/* Loading skeletons */}
            {isPending && (
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

            {/* Regression results */}
            {regressionData && !isPending && (
              <>
                <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                  <StatCard
                    label="Alpha"
                    value={formatPercent(regressionData.alpha)}
                    trend={
                      regressionData.alpha != null && regressionData.alpha > 0
                        ? "up"
                        : regressionData.alpha != null &&
                            regressionData.alpha < 0
                          ? "down"
                          : "neutral"
                    }
                  />
                  <StatCard
                    label="R-Squared"
                    value={formatNumber(regressionData.r_squared, 4)}
                  />
                  <StatCard
                    label="Adj R-Squared"
                    value={formatNumber(regressionData.adj_r_squared, 4)}
                  />
                  <StatCard
                    label="Model Type"
                    value={regressionData.model_type}
                  />
                </div>

                <ChartCard title="Factor Loadings">
                  <BarChartWrapper
                    data={loadingsChartData as Record<string, unknown>[]}
                    xKey="factor"
                    yKey="loading"
                    height={300}
                    label="Loading by Factor"
                  />
                </ChartCard>

                {rollingChartData.length > 0 && (
                  <ChartCard title="Rolling R-Squared">
                    <LineChartWrapper
                      data={rollingChartData as Record<string, unknown>[]}
                      xKey="date"
                      series={[{ key: "r_squared" }]}
                      height={250}
                      label="Rolling R-Squared over Time"
                      referenceY={1}
                      referenceLabel="Perfect Fit"
                    />
                  </ChartCard>
                )}

                <ChartCard title="Regression Results">
                  <DataTable
                    columns={[
                      { key: "factor", label: "Factor" },
                      {
                        key: "loading",
                        label: "Loading",
                        format: (v) => formatNumber(v as number | null, 4),
                      },
                      {
                        key: "t_stat",
                        label: "t-Statistic",
                        format: (v) => formatNumber(v as number | null, 4),
                      },
                      {
                        key: "p_value",
                        label: "p-Value",
                        format: (v) => formatNumber(v as number | null, 4),
                      },
                    ]}
                    data={regressionTableData as Record<string, unknown>[]}
                  />
                </ChartCard>
              </>
            )}

            {/* Error state */}
            {hasError && (
              <InlineError
                message={
                  regressionMutation.error?.message ??
                  "Factor regression failed"
                }
                onRetry={handleRunAll}
              />
            )}

            {/* Empty state */}
            {!isPending && !hasError && !regressionData && (
              <EmptyState
                icon={Layers}
                message="Configure parameters and click Run All to perform factor analysis."
                presets={[
                  {
                    label: "SPY FF3 Model",
                    onClick: () => {
                      setTicker("SPY");
                      setModelType("FF3");
                      setFactorNamesRaw("Mkt-RF, SMB, HML");
                    },
                  },
                  {
                    label: "QQQ CAPM",
                    onClick: () => {
                      setTicker("QQQ");
                      setModelType("CAPM");
                      setFactorNamesRaw("Mkt-RF");
                    },
                  },
                ]}
              />
            )}
          </ToolLayout>
        </TabsContent>

        {/* ================================================================
            Tab 2: Return Attribution
            ================================================================ */}
        <TabsContent value="attribution" className="mt-0 space-y-6">
          {isPending && (
            <>
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
                <CardSkeleton />
                <CardSkeleton />
                <CardSkeleton />
              </div>
              <ChartSkeleton />
            </>
          )}

          {!isPending && !attributionData && (
            <EmptyState
              icon={Layers}
              message="Run factor regression first to see return attribution results."
            />
          )}

          {attributionData && !isPending && (
            <>
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
                <StatCard
                  label="Total Return"
                  value={formatPercent(attributionData.total_return)}
                  trend={
                    attributionData.total_return != null &&
                    attributionData.total_return > 0
                      ? "up"
                      : attributionData.total_return != null &&
                          attributionData.total_return < 0
                        ? "down"
                        : "neutral"
                  }
                />
                <StatCard
                  label="Explained Return"
                  value={formatPercent(attributionData.explained_return)}
                />
                <StatCard
                  label="Residual Return"
                  value={formatPercent(attributionData.residual_return)}
                  trend={
                    attributionData.residual_return != null &&
                    attributionData.residual_return > 0
                      ? "up"
                      : attributionData.residual_return != null &&
                          attributionData.residual_return < 0
                        ? "down"
                        : "neutral"
                  }
                />
              </div>

              <ChartCard title="Factor Contributions">
                <BarChartWrapper
                  data={attributionChartData as Record<string, unknown>[]}
                  xKey="name"
                  yKey="contribution"
                  height={300}
                  label="Contribution to Total Return"
                />
              </ChartCard>

              <ChartCard title="Attribution Detail">
                <DataTable
                  columns={[
                    { key: "factor", label: "Factor" },
                    {
                      key: "contribution",
                      label: "Contribution",
                      format: (v) => formatPercent(v as number | null),
                    },
                  ]}
                  data={attributionTableData as Record<string, unknown>[]}
                />
              </ChartCard>
            </>
          )}
        </TabsContent>

        {/* ================================================================
            Tab 3: Risk Decomposition
            ================================================================ */}
        <TabsContent value="risk" className="mt-0 space-y-6">
          {isPending && (
            <>
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
                <CardSkeleton />
                <CardSkeleton />
                <CardSkeleton />
              </div>
              <ChartSkeleton />
            </>
          )}

          {!isPending && !riskData && (
            <EmptyState
              icon={Layers}
              message="Run factor regression first to see risk decomposition results."
            />
          )}

          {riskData && !isPending && (
            <>
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
                <StatCard
                  label="Systematic Variance"
                  value={formatNumber(riskData.systematic_variance, 6)}
                />
                <StatCard
                  label="Idiosyncratic Variance"
                  value={formatNumber(riskData.idiosyncratic_variance, 6)}
                />
                <StatCard
                  label="% Systematic"
                  value={formatPercent(riskData.pct_systematic)}
                />
              </div>

              <ChartCard title="Variance Decomposition">
                <BarChartWrapper
                  data={riskChartData as Record<string, unknown>[]}
                  xKey="type"
                  yKey="value"
                  height={300}
                  label="Systematic vs Idiosyncratic Variance"
                />
              </ChartCard>

              <ChartCard title="Marginal Factor Contributions">
                <DataTable
                  columns={[
                    { key: "factor", label: "Factor" },
                    {
                      key: "marginal_contribution",
                      label: "Marginal Contribution",
                      format: (v) => formatNumber(v as number | null, 6),
                    },
                  ]}
                  data={riskTableData as Record<string, unknown>[]}
                />
              </ChartCard>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
