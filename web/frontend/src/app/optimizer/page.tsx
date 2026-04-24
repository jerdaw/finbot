"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { Target, TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    BarChartWrapper,
    ScatterChartWrapper,
} from "@/components/charts/recharts-wrappers";
import { DataTable } from "@/components/common/data-table";
import { Heatmap } from "@/components/common/heatmap";
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
import { apiGet, apiPost } from "@/lib/api";
import { formatPercent, formatNumber, formatCurrency } from "@/lib/format";
import type {
    DCAOptimizerRequest,
    DCAOptimizerResponse,
    EfficientFrontierRequest,
    EfficientFrontierResponse,
    ParetoOptimizerRequest,
    ParetoOptimizerResponse,
    StrategyInfo,
} from "@/types/api";

const DEFAULT_RATIOS = "0.1, 0.2, 0.3, 0.5, 0.7, 1.0";
const DEFAULT_DCA_DURATIONS = "30, 60, 90, 120, 180, 252";
const DEFAULT_TRIAL_DURATIONS = "252, 504, 756";
const DEFAULT_PARETO_STRATEGIES = [
    "NoRebalance",
    "Rebalance",
    "SMACrossover",
    "RiskParity",
    "DualMomentum",
];

function parseNumberList(input: string): number[] {
    return input
        .split(",")
        .map((value) => Number(value.trim()))
        .filter((value) => Number.isFinite(value));
}

function parseTickerList(input: string): string[] {
    return input
        .split(",")
        .map((value) => value.trim().toUpperCase())
        .filter((value) => value.length > 0);
}

function DcaWorkspace() {
    const [ticker, setTicker] = useState("SPY");
    const [ratioRange, setRatioRange] = useState(DEFAULT_RATIOS);
    const [dcaDurations, setDcaDurations] = useState(DEFAULT_DCA_DURATIONS);
    const [trialDurations, setTrialDurations] = useState(
        DEFAULT_TRIAL_DURATIONS,
    );
    const [startingCash, setStartingCash] = useState(10000);
    const [showRawResults, setShowRawResults] = useState(false);

    const mutation = useMutation({
        mutationFn: (request: DCAOptimizerRequest) =>
            apiPost<DCAOptimizerResponse>(
                "/api/optimizer/run",
                request,
                120000,
            ),
        onSuccess: () => toast.success("Optimization complete"),
        onError: (error) =>
            toast.error(`Optimization failed: ${error.message}`),
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
    const bestByRatio = result?.by_ratio?.reduce(
        (best, row) => {
            const cagr = row["cagr"] as number | undefined;
            if (
                cagr != null &&
                (best == null ||
                    cagr >
                        ((best["cagr"] as number | undefined) ??
                            Number.NEGATIVE_INFINITY))
            ) {
                return row;
            }
            return best;
        },
        null as Record<string, unknown> | null,
    );
    const bestByDuration = result?.by_duration?.reduce(
        (best, row) => {
            const cagr = row["cagr"] as number | undefined;
            if (
                cagr != null &&
                (best == null ||
                    cagr >
                        ((best["cagr"] as number | undefined) ??
                            Number.NEGATIVE_INFINITY))
            ) {
                return row;
            }
            return best;
        },
        null as Record<string, unknown> | null,
    );

    return (
        <ToolLayout
            configPanel={
                <ConfigPanel title="DCA Grid Search">
                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">
                            Ticker
                        </Label>
                        <Input
                            className="border-border/50 bg-background/50"
                            value={ticker}
                            onChange={(event) => setTicker(event.target.value)}
                        />
                    </div>

                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">
                            DCA Ratios
                        </Label>
                        <Input
                            className="border-border/50 bg-background/50"
                            value={ratioRange}
                            onChange={(event) =>
                                setRatioRange(event.target.value)
                            }
                        />
                    </div>

                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">
                            DCA Durations (days)
                        </Label>
                        <Input
                            className="border-border/50 bg-background/50"
                            value={dcaDurations}
                            onChange={(event) =>
                                setDcaDurations(event.target.value)
                            }
                        />
                    </div>

                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">
                            Trial Durations (days)
                        </Label>
                        <Input
                            className="border-border/50 bg-background/50"
                            value={trialDurations}
                            onChange={(event) =>
                                setTrialDurations(event.target.value)
                            }
                        />
                    </div>

                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">
                            Starting Cash ($)
                        </Label>
                        <Input
                            className="border-border/50 bg-background/50"
                            type="number"
                            value={startingCash}
                            onChange={(event) =>
                                setStartingCash(Number(event.target.value))
                            }
                            min={1}
                        />
                    </div>

                    <Button
                        className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
                        onClick={handleRun}
                        disabled={mutation.isPending}
                    >
                        {mutation.isPending
                            ? "Optimizing..."
                            : "Run DCA Optimizer"}
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
                    <TableSkeleton />
                </>
            )}

            {result && (
                <>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
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
                                    ? formatPercent(
                                          bestByRatio["cagr"] as number,
                                      )
                                    : "N/A"
                            }
                            trend={
                                bestByRatio &&
                                (bestByRatio["cagr"] as number) > 0
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
                            value={formatNumber(
                                result.raw_results?.length ?? 0,
                                0,
                            )}
                        />
                    </div>

                    {result.by_ratio.length > 0 && (
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

                    {result.by_duration.length > 0 && (
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

                    {result.raw_results.length > 0 && (
                        <ChartCard
                            title={`Raw Results (${result.raw_results.length})`}
                            action={
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() =>
                                        setShowRawResults(!showRawResults)
                                    }
                                >
                                    {showRawResults ? "Collapse" : "Expand"}
                                </Button>
                            }
                        >
                            {showRawResults && (
                                <DataTable
                                    columns={buildRawResultColumns(
                                        result.raw_results,
                                    )}
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
                    message="Configure parameters and click Run DCA Optimizer to compare grid-search outcomes."
                    presets={[
                        {
                            label: "SPY Default Grid",
                            onClick: () => {
                                setTicker("SPY");
                                setRatioRange(DEFAULT_RATIOS);
                                setDcaDurations(DEFAULT_DCA_DURATIONS);
                            },
                        },
                    ]}
                />
            )}
        </ToolLayout>
    );
}

function ParetoWorkspace() {
    const [tickers, setTickers] = useState("SPY, TLT");
    const [startDate, setStartDate] = useState("2015-01-01");
    const [endDate, setEndDate] = useState("2024-12-31");
    const [initialCash, setInitialCash] = useState(10000);
    const [selectedStrategies, setSelectedStrategies] = useState<string[]>(
        DEFAULT_PARETO_STRATEGIES,
    );

    const { data: strategies } = useQuery({
        queryKey: ["strategies"],
        queryFn: () => apiGet<StrategyInfo[]>("/api/backtesting/strategies"),
    });

    const mutation = useMutation({
        mutationFn: (request: ParetoOptimizerRequest) =>
            apiPost<ParetoOptimizerResponse>(
                "/api/optimizer/pareto/run",
                request,
                180000,
            ),
        onSuccess: () => toast.success("Pareto sweep complete"),
        onError: (error) =>
            toast.error(`Pareto sweep failed: ${error.message}`),
    });

    const toggleStrategy = (strategyName: string) => {
        setSelectedStrategies((current) =>
            current.includes(strategyName)
                ? current.filter((value) => value !== strategyName)
                : [...current, strategyName],
        );
    };

    const handleRun = () => {
        const tickerList = parseTickerList(tickers);
        if (tickerList.length === 0) {
            toast.error("Enter at least one ticker for the Pareto sweep.");
            return;
        }
        if (selectedStrategies.length === 0) {
            toast.error("Select at least one strategy for the Pareto sweep.");
            return;
        }

        mutation.mutate({
            tickers: tickerList,
            strategies: selectedStrategies,
            start_date: startDate,
            end_date: endDate,
            initial_cash: initialCash,
            objective_a: "cagr",
            objective_b: "max_drawdown",
            maximize_a: true,
            maximize_b: false,
        });
    };

    const result = mutation.data;
    const bestCagr = result?.all_points.reduce(
        (best, point) =>
            Math.max(best, point.metrics.cagr ?? Number.NEGATIVE_INFINITY),
        Number.NEGATIVE_INFINITY,
    );
    const lowestDrawdown = result?.all_points.reduce(
        (best, point) =>
            Math.min(
                best,
                point.metrics.max_drawdown ?? Number.POSITIVE_INFINITY,
            ),
        Number.POSITIVE_INFINITY,
    );
    const scatterData =
        result?.all_points.map((point) => ({
            x: point.objective_b,
            y: point.objective_a,
            label: point.strategy_name,
        })) ?? [];

    return (
        <ToolLayout
            configPanel={
                <ConfigPanel title="Strategy Pareto Sweep">
                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">
                            Tickers
                        </Label>
                        <Input
                            className="border-border/50 bg-background/50"
                            value={tickers}
                            onChange={(event) => setTickers(event.target.value)}
                        />
                        <p className="text-xs text-muted-foreground">
                            Allocation strategies use the full list. Timing
                            strategies use the primary asset or required pair.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                        <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">
                                Start Date
                            </Label>
                            <Input
                                className="border-border/50 bg-background/50"
                                type="date"
                                value={startDate}
                                onChange={(event) =>
                                    setStartDate(event.target.value)
                                }
                            />
                        </div>
                        <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">
                                End Date
                            </Label>
                            <Input
                                className="border-border/50 bg-background/50"
                                type="date"
                                value={endDate}
                                onChange={(event) =>
                                    setEndDate(event.target.value)
                                }
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">
                            Initial Cash ($)
                        </Label>
                        <Input
                            className="border-border/50 bg-background/50"
                            type="number"
                            value={initialCash}
                            onChange={(event) =>
                                setInitialCash(Number(event.target.value))
                            }
                        />
                    </div>

                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">
                            Strategies
                        </Label>
                        <div className="flex flex-wrap gap-2">
                            {(strategies ?? []).map((strategy) => (
                                <Button
                                    key={strategy.name}
                                    type="button"
                                    variant="outline"
                                    size="xs"
                                    onClick={() =>
                                        toggleStrategy(strategy.name)
                                    }
                                    className={
                                        selectedStrategies.includes(
                                            strategy.name,
                                        )
                                            ? "border-blue-500/50 bg-blue-500/10 text-blue-300"
                                            : undefined
                                    }
                                >
                                    {strategy.name}
                                </Button>
                            ))}
                        </div>
                    </div>

                    <Button
                        className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
                        onClick={handleRun}
                        disabled={mutation.isPending}
                    >
                        {mutation.isPending
                            ? "Evaluating..."
                            : "Run Pareto Sweep"}
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
                    <TableSkeleton />
                </>
            )}

            {result && (
                <>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                        <StatCard
                            label="Strategies Evaluated"
                            value={formatNumber(result.n_evaluated, 0)}
                            trend="neutral"
                        />
                        <StatCard
                            label="Pareto Front Size"
                            value={formatNumber(result.pareto_front.length, 0)}
                            trend="up"
                        />
                        <StatCard
                            label="Best CAGR"
                            value={formatPercent(bestCagr)}
                            trend="up"
                        />
                        <StatCard
                            label="Lowest Drawdown"
                            value={formatPercent(lowestDrawdown)}
                            trend="up"
                        />
                    </div>

                    {scatterData.length > 0 && (
                        <ChartCard title="CAGR vs Max Drawdown">
                            <ScatterChartWrapper
                                data={scatterData}
                                xLabel="Max Drawdown"
                                yLabel="CAGR"
                                height={360}
                            />
                        </ChartCard>
                    )}

                    <ChartCard title="Pareto-Optimal Strategies">
                        <DataTable
                            columns={[
                                { key: "strategy_name", label: "Strategy" },
                                {
                                    key: "tickers_used",
                                    label: "Tickers",
                                    format: (value) =>
                                        Array.isArray(value)
                                            ? value.join(", ")
                                            : "",
                                },
                                {
                                    key: "objective_a",
                                    label: "CAGR",
                                    format: (value) =>
                                        formatPercent(value as number | null),
                                },
                                {
                                    key: "objective_b",
                                    label: "Max Drawdown",
                                    format: (value) =>
                                        formatPercent(value as number | null),
                                },
                                { key: "metrics.sharpe", label: "Sharpe" },
                            ]}
                            data={result.pareto_front.map((point) => ({
                                ...point,
                                "metrics.sharpe":
                                    point.metrics.sharpe != null
                                        ? formatNumber(point.metrics.sharpe, 3)
                                        : "N/A",
                            }))}
                        />
                    </ChartCard>

                    {result.warnings.length > 0 && (
                        <ChartCard title="Sweep Warnings">
                            <DataTable
                                columns={[{ key: "warning", label: "Warning" }]}
                                data={result.warnings.map((warning) => ({
                                    warning,
                                }))}
                            />
                        </ChartCard>
                    )}
                </>
            )}

            {mutation.isError && (
                <InlineError
                    message={mutation.error?.message ?? "Pareto sweep failed"}
                    onRetry={handleRun}
                />
            )}

            {!mutation.isPending && !mutation.isError && !result && (
                <EmptyState
                    icon={Target}
                    message="Evaluate a small strategy sweep and surface the non-dominated return versus drawdown frontier."
                    presets={[
                        {
                            label: "SPY / TLT Core Sweep",
                            onClick: () => {
                                setTickers("SPY, TLT");
                                setSelectedStrategies(
                                    DEFAULT_PARETO_STRATEGIES,
                                );
                            },
                        },
                    ]}
                />
            )}
        </ToolLayout>
    );
}

function EfficientFrontierWorkspace() {
    const [tickers, setTickers] = useState("SPY, TLT, GLD");
    const [startDate, setStartDate] = useState("2015-01-01");
    const [endDate, setEndDate] = useState("2024-12-31");
    const [riskFreeRate, setRiskFreeRate] = useState(0.04);
    const [nPortfolios, setNPortfolios] = useState(2500);

    const mutation = useMutation({
        mutationFn: (request: EfficientFrontierRequest) =>
            apiPost<EfficientFrontierResponse>(
                "/api/optimizer/efficient-frontier/run",
                request,
                120000,
            ),
        onSuccess: () => toast.success("Efficient frontier complete"),
        onError: (error) =>
            toast.error(`Efficient frontier failed: ${error.message}`),
    });

    const handleRun = () => {
        const tickerList = parseTickerList(tickers);
        if (tickerList.length < 2) {
            toast.error(
                "Enter at least two tickers for efficient frontier analysis.",
            );
            return;
        }

        mutation.mutate({
            tickers: tickerList,
            start_date: startDate,
            end_date: endDate,
            risk_free_rate: riskFreeRate,
            n_portfolios: nPortfolios,
        });
    };

    const result = mutation.data;
    const scatterData =
        result?.portfolios.map((portfolio) => ({
            x: portfolio.volatility,
            y: portfolio.expected_return,
            label: `Sharpe ${portfolio.sharpe_ratio.toFixed(2)}`,
        })) ?? [];
    const frontierData =
        result?.frontier.map((portfolio) => ({
            x: portfolio.volatility,
            y: portfolio.expected_return,
            label: `Sharpe ${portfolio.sharpe_ratio.toFixed(2)}`,
        })) ?? [];
    const correlationLabels = result
        ? Object.keys(result.correlation_matrix)
        : [];

    return (
        <ToolLayout
            configPanel={
                <ConfigPanel title="Efficient Frontier">
                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">
                            Tickers
                        </Label>
                        <Input
                            className="border-border/50 bg-background/50"
                            value={tickers}
                            onChange={(event) => setTickers(event.target.value)}
                        />
                    </div>

                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                        <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">
                                Start Date
                            </Label>
                            <Input
                                className="border-border/50 bg-background/50"
                                type="date"
                                value={startDate}
                                onChange={(event) =>
                                    setStartDate(event.target.value)
                                }
                            />
                        </div>
                        <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">
                                End Date
                            </Label>
                            <Input
                                className="border-border/50 bg-background/50"
                                type="date"
                                value={endDate}
                                onChange={(event) =>
                                    setEndDate(event.target.value)
                                }
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                        <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">
                                Risk-Free Rate
                            </Label>
                            <Input
                                className="border-border/50 bg-background/50"
                                type="number"
                                step={0.01}
                                min={0}
                                max={1}
                                value={riskFreeRate}
                                onChange={(event) =>
                                    setRiskFreeRate(Number(event.target.value))
                                }
                            />
                        </div>
                        <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">
                                Portfolios Sampled
                            </Label>
                            <Input
                                className="border-border/50 bg-background/50"
                                type="number"
                                min={100}
                                max={10000}
                                value={nPortfolios}
                                onChange={(event) =>
                                    setNPortfolios(Number(event.target.value))
                                }
                            />
                        </div>
                    </div>

                    <Button
                        className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
                        onClick={handleRun}
                        disabled={mutation.isPending}
                    >
                        {mutation.isPending
                            ? "Optimizing..."
                            : "Run Efficient Frontier"}
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

            {result && (
                <>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                        <StatCard
                            label="Sampled Portfolios"
                            value={formatNumber(result.portfolios.length, 0)}
                            trend="neutral"
                        />
                        <StatCard
                            label="Max Sharpe Return"
                            value={formatPercent(
                                result.max_sharpe.expected_return,
                            )}
                            trend="up"
                        />
                        <StatCard
                            label="Max Sharpe Volatility"
                            value={formatPercent(result.max_sharpe.volatility)}
                            trend="neutral"
                        />
                        <StatCard
                            label="Min Volatility"
                            value={formatPercent(
                                result.min_volatility.volatility,
                            )}
                            trend="up"
                        />
                    </div>

                    {scatterData.length > 0 && (
                        <ChartCard title="Sampled Portfolio Surface">
                            <ScatterChartWrapper
                                data={scatterData}
                                xLabel="Volatility"
                                yLabel="Expected Return"
                                height={360}
                            />
                        </ChartCard>
                    )}

                    {frontierData.length > 0 && (
                        <ChartCard title="Efficient Frontier">
                            <ScatterChartWrapper
                                data={frontierData}
                                xLabel="Volatility"
                                yLabel="Expected Return"
                                height={320}
                            />
                        </ChartCard>
                    )}

                    {correlationLabels.length > 0 && (
                        <ChartCard title="Historical Correlation Matrix">
                            <Heatmap
                                labels={correlationLabels}
                                matrix={result.correlation_matrix}
                            />
                        </ChartCard>
                    )}

                    <ChartCard title="Asset Statistics">
                        <DataTable
                            columns={[
                                { key: "ticker", label: "Ticker" },
                                {
                                    key: "annual_return",
                                    label: "Annual Return",
                                    format: (value) =>
                                        formatPercent(value as number | null),
                                },
                                {
                                    key: "annual_volatility",
                                    label: "Annual Volatility",
                                    format: (value) =>
                                        formatPercent(value as number | null),
                                },
                            ]}
                            data={result.asset_stats}
                        />
                    </ChartCard>

                    <ChartCard title="Highlighted Portfolios">
                        <DataTable
                            columns={[
                                { key: "label", label: "Portfolio" },
                                {
                                    key: "expected_return",
                                    label: "Expected Return",
                                    format: (value) =>
                                        formatPercent(value as number | null),
                                },
                                {
                                    key: "volatility",
                                    label: "Volatility",
                                    format: (value) =>
                                        formatPercent(value as number | null),
                                },
                                {
                                    key: "sharpe_ratio",
                                    label: "Sharpe",
                                    format: (value) =>
                                        formatNumber(value as number | null, 3),
                                },
                                {
                                    key: "weights",
                                    label: "Weights",
                                    format: (value) =>
                                        formatWeights(
                                            value as Record<string, number>,
                                        ),
                                },
                            ]}
                            data={[
                                { label: "Max Sharpe", ...result.max_sharpe },
                                {
                                    label: "Min Volatility",
                                    ...result.min_volatility,
                                },
                            ]}
                        />
                    </ChartCard>
                </>
            )}

            {mutation.isError && (
                <InlineError
                    message={
                        mutation.error?.message ?? "Efficient frontier failed"
                    }
                    onRetry={handleRun}
                />
            )}

            {!mutation.isPending && !mutation.isError && !result && (
                <EmptyState
                    icon={Target}
                    message="Sample long-only portfolios to estimate the efficient frontier and highlight max-Sharpe versus min-volatility allocations."
                    presets={[
                        {
                            label: "SPY / TLT / GLD",
                            onClick: () => {
                                setTickers("SPY, TLT, GLD");
                                setRiskFreeRate(0.04);
                                setNPortfolios(2500);
                            },
                        },
                    ]}
                />
            )}
        </ToolLayout>
    );
}

export default function OptimizerPage() {
    return (
        <div className="space-y-8">
            <PageHeader
                title="Portfolio Optimizer"
                description="Run DCA grids, strategy Pareto sweeps, and efficient frontier research from one workspace"
            />

            <Tabs defaultValue="dca" className="space-y-6">
                <TabsList>
                    <TabsTrigger value="dca">DCA</TabsTrigger>
                    <TabsTrigger value="pareto">Pareto</TabsTrigger>
                    <TabsTrigger value="frontier">
                        Efficient Frontier
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="dca">
                    <DcaWorkspace />
                </TabsContent>

                <TabsContent value="pareto">
                    <ParetoWorkspace />
                </TabsContent>

                <TabsContent value="frontier">
                    <EfficientFrontierWorkspace />
                </TabsContent>
            </Tabs>
        </div>
    );
}

function buildRawResultColumns(
    data: Record<string, unknown>[],
): { key: string; label: string; format?: (value: unknown) => string }[] {
    if (data.length === 0) return [];

    return Object.keys(data[0]).map((key) => ({
        key,
        label: key
            .replace(/_/g, " ")
            .replace(/\b\w/g, (character) => character.toUpperCase()),
        format: (value: unknown) => {
            if (value == null) return "N/A";
            if (typeof value === "number") {
                return Math.abs(value) <= 1
                    ? formatPercent(value)
                    : formatNumber(value, 4);
            }
            return String(value);
        },
    }));
}

function formatWeights(weights: Record<string, number>): string {
    return Object.entries(weights)
        .map(([ticker, weight]) => `${ticker} ${formatPercent(weight)}`)
        .join(", ");
}
