"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Shuffle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FanChart } from "@/components/charts/fan-chart";
import { BarChartWrapper } from "@/components/charts/recharts-wrappers";
import { DataTable } from "@/components/common/data-table";
import { Heatmap } from "@/components/common/heatmap";
import { StatCard } from "@/components/common/stat-card";
import { PageHeader } from "@/components/common/page-header";
import { ToolLayout } from "@/components/common/tool-layout";
import { EmptyState } from "@/components/common/empty-state";
import { InlineError } from "@/components/common/inline-error";
import {
    ChartSkeleton,
    CardSkeleton,
} from "@/components/common/loading-skeleton";
import { ConfigPanel } from "@/components/common/config-panel";
import { ChartCard } from "@/components/common/chart-card";
import { apiPost } from "@/lib/api";
import { formatCurrency, formatPercent, formatNumber } from "@/lib/format";
import type {
    MonteCarloRequest,
    MonteCarloResponse,
    MultiAssetMonteCarloRequest,
    MultiAssetMonteCarloResponse,
} from "@/types/api";

function parseTickerList(input: string): string[] {
    return input
        .split(",")
        .map((value) => value.trim().toUpperCase())
        .filter((value) => value.length > 0);
}

function parseNumberList(input: string): number[] {
    return input
        .split(",")
        .map((value) => Number(value.trim()))
        .filter((value) => Number.isFinite(value));
}

function SingleAssetMonteCarloWorkspace() {
    const [ticker, setTicker] = useState("SPY");
    const [simPeriods, setSimPeriods] = useState(252);
    const [nSims, setNSims] = useState(1000);

    const mutation = useMutation({
        mutationFn: (request: MonteCarloRequest) =>
            apiPost<MonteCarloResponse>(
                "/api/monte-carlo/run",
                request,
                120000,
            ),
        onSuccess: () => toast.success("Simulation complete"),
        onError: (error) => toast.error(`Simulation failed: ${error.message}`),
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
    const histogramData = buildHistogram(result?.sample_paths);

    return (
        <ToolLayout
            configPanel={
                <ConfigPanel title="Single Asset">
                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">
                            Ticker
                        </Label>
                        <Input
                            className="border-border/50 bg-background/50"
                            value={ticker}
                            onChange={(event) => setTicker(event.target.value)}
                            placeholder="e.g. SPY"
                        />
                    </div>

                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">
                            Simulation Periods
                        </Label>
                        <Input
                            className="border-border/50 bg-background/50"
                            type="number"
                            value={simPeriods}
                            onChange={(event) =>
                                setSimPeriods(Number(event.target.value))
                            }
                            min={1}
                        />
                        <p className="text-xs text-muted-foreground">
                            Trading days to simulate (252 = ~1 year)
                        </p>
                    </div>

                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">
                            Number of Simulations
                        </Label>
                        <Input
                            className="border-border/50 bg-background/50"
                            type="number"
                            value={nSims}
                            onChange={(event) =>
                                setNSims(
                                    Math.min(Number(event.target.value), 10000),
                                )
                            }
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

            {stats && result && (
                <>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                        <StatCard
                            label="Median Final Value"
                            value={formatCurrency(stats["median"] ?? null)}
                            trend={
                                stats["median"] != null && stats["median"] > 0
                                    ? "up"
                                    : "neutral"
                            }
                        />
                        <StatCard
                            label="Mean Final Value"
                            value={formatCurrency(stats["mean"] ?? null)}
                            trend={
                                stats["mean"] != null && stats["mean"] > 0
                                    ? "up"
                                    : "neutral"
                            }
                        />
                        <StatCard
                            label="p5 Final Value"
                            value={formatCurrency(stats["p5"] ?? null)}
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
                                stats["prob_loss"] != null &&
                                stats["prob_loss"] > 0.5
                                    ? "down"
                                    : "up"
                            }
                        />
                    </div>

                    <ChartCard title="Price Path Fan Chart">
                        <FanChart
                            periods={result.periods}
                            bands={result.bands}
                            samplePaths={result.sample_paths}
                            height={400}
                        />
                    </ChartCard>

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

                    <ChartCard title="Simulation Statistics">
                        <DataTable
                            columns={[
                                { key: "metric", label: "Metric" },
                                { key: "value", label: "Value" },
                            ]}
                            data={Object.entries(stats).map(([key, value]) => ({
                                metric: formatStatLabel(key),
                                value:
                                    value == null
                                        ? "N/A"
                                        : key.includes("prob") ||
                                            key.includes("pct")
                                          ? formatPercent(value)
                                          : formatNumber(value, 2),
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
                    message="Configure parameters and click Run Simulation to see possible future price paths."
                    presets={[
                        {
                            label: "SPY 1-Year (1000 sims)",
                            onClick: () => {
                                setTicker("SPY");
                                setSimPeriods(252);
                                setNSims(1000);
                            },
                        },
                        {
                            label: "QQQ 2-Year (5000 sims)",
                            onClick: () => {
                                setTicker("QQQ");
                                setSimPeriods(504);
                                setNSims(5000);
                            },
                        },
                    ]}
                />
            )}
        </ToolLayout>
    );
}

function MultiAssetMonteCarloWorkspace() {
    const [tickers, setTickers] = useState("SPY, TLT, GLD");
    const [weights, setWeights] = useState("0.6, 0.3, 0.1");
    const [simPeriods, setSimPeriods] = useState(252);
    const [nSims, setNSims] = useState(1000);
    const [startValue, setStartValue] = useState(10000);

    const mutation = useMutation({
        mutationFn: (request: MultiAssetMonteCarloRequest) =>
            apiPost<MultiAssetMonteCarloResponse>(
                "/api/monte-carlo/multi-asset/run",
                request,
                120000,
            ),
        onSuccess: () => toast.success("Multi-asset simulation complete"),
        onError: (error) =>
            toast.error(`Multi-asset simulation failed: ${error.message}`),
    });

    const handleRun = () => {
        const tickerList = parseTickerList(tickers);
        const weightList = parseNumberList(weights);

        if (tickerList.length < 2) {
            toast.error(
                "Enter at least two tickers for a multi-asset simulation.",
            );
            return;
        }
        if (weightList.length > 0 && weightList.length !== tickerList.length) {
            toast.error(
                "Weights must either be blank or match the number of tickers.",
            );
            return;
        }

        mutation.mutate({
            tickers: tickerList,
            weights: weightList.length > 0 ? weightList : undefined,
            sim_periods: simPeriods,
            n_sims: Math.min(nSims, 10000),
            start_value: startValue,
        });
    };

    const result = mutation.data;
    const stats = result?.portfolio_statistics;
    const correlationLabels = result
        ? Object.keys(result.correlation_matrix)
        : [];

    return (
        <ToolLayout
            configPanel={
                <ConfigPanel title="Multi-Asset">
                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">
                            Tickers
                        </Label>
                        <Input
                            className="border-border/50 bg-background/50"
                            value={tickers}
                            onChange={(event) => setTickers(event.target.value)}
                            placeholder="SPY, TLT, GLD"
                        />
                        <p className="text-xs text-muted-foreground">
                            Comma-separated tickers for correlated portfolio
                            simulation.
                        </p>
                    </div>

                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">
                            Weights
                        </Label>
                        <Input
                            className="border-border/50 bg-background/50"
                            value={weights}
                            onChange={(event) => setWeights(event.target.value)}
                            placeholder="0.6, 0.3, 0.1"
                        />
                        <p className="text-xs text-muted-foreground">
                            Leave blank for equal-weight. Values are normalized
                            automatically.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                        <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">
                                Simulation Periods
                            </Label>
                            <Input
                                className="border-border/50 bg-background/50"
                                type="number"
                                value={simPeriods}
                                onChange={(event) =>
                                    setSimPeriods(Number(event.target.value))
                                }
                                min={1}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">
                                Number of Simulations
                            </Label>
                            <Input
                                className="border-border/50 bg-background/50"
                                type="number"
                                value={nSims}
                                onChange={(event) =>
                                    setNSims(
                                        Math.min(
                                            Number(event.target.value),
                                            10000,
                                        ),
                                    )
                                }
                                min={100}
                                max={10000}
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">
                            Starting Portfolio Value
                        </Label>
                        <Input
                            className="border-border/50 bg-background/50"
                            type="number"
                            value={startValue}
                            onChange={(event) =>
                                setStartValue(Number(event.target.value))
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
                            ? "Running..."
                            : "Run Multi-Asset Simulation"}
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

            {stats && result && (
                <>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                        <StatCard
                            label="Median Portfolio Value"
                            value={formatCurrency(stats["median"] ?? null)}
                            trend={
                                stats["median"] != null &&
                                stats["median"] > startValue
                                    ? "up"
                                    : "neutral"
                            }
                        />
                        <StatCard
                            label="Mean Portfolio Value"
                            value={formatCurrency(stats["mean"] ?? null)}
                            trend={
                                stats["mean"] != null &&
                                stats["mean"] > startValue
                                    ? "up"
                                    : "neutral"
                            }
                        />
                        <StatCard
                            label="p5 Portfolio Value"
                            value={formatCurrency(stats["p5"] ?? null)}
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
                                stats["prob_loss"] != null &&
                                stats["prob_loss"] > 0.5
                                    ? "down"
                                    : "up"
                            }
                        />
                    </div>

                    <ChartCard title="Portfolio Fan Chart">
                        <FanChart
                            periods={result.periods}
                            bands={result.portfolio_bands}
                            samplePaths={result.portfolio_sample_paths}
                            height={400}
                        />
                    </ChartCard>

                    {correlationLabels.length > 0 && (
                        <ChartCard title="Historical Correlation Matrix">
                            <Heatmap
                                labels={correlationLabels}
                                matrix={result.correlation_matrix}
                            />
                        </ChartCard>
                    )}

                    <ChartCard title="Asset Weights and Historical Stats">
                        <DataTable
                            columns={[
                                { key: "ticker", label: "Ticker" },
                                {
                                    key: "weight",
                                    label: "Weight",
                                    format: (value) =>
                                        formatPercent(value as number | null),
                                },
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
                            data={result.asset_statistics}
                        />
                    </ChartCard>
                </>
            )}

            {mutation.isError && (
                <InlineError
                    message={
                        mutation.error?.message ??
                        "Multi-asset simulation failed"
                    }
                    onRetry={handleRun}
                />
            )}

            {!mutation.isPending && !mutation.isError && !result && (
                <EmptyState
                    icon={Shuffle}
                    message="Model correlated multi-asset outcomes with custom weights and historical correlations."
                    presets={[
                        {
                            label: "Classic 60/40",
                            onClick: () => {
                                setTickers("SPY, TLT");
                                setWeights("0.6, 0.4");
                            },
                        },
                        {
                            label: "All Weather Tilt",
                            onClick: () => {
                                setTickers("SPY, TLT, GLD, DBC");
                                setWeights("0.3, 0.4, 0.15, 0.15");
                            },
                        },
                    ]}
                />
            )}
        </ToolLayout>
    );
}

export default function MonteCarloPage() {
    return (
        <div className="space-y-8">
            <PageHeader
                title="Monte Carlo Lab"
                description="Run single-asset and correlated multi-asset Monte Carlo research from one workspace"
            />

            <Tabs defaultValue="single" className="space-y-6">
                <TabsList>
                    <TabsTrigger value="single">Single Asset</TabsTrigger>
                    <TabsTrigger value="multi">Multi-Asset</TabsTrigger>
                </TabsList>

                <TabsContent value="single">
                    <SingleAssetMonteCarloWorkspace />
                </TabsContent>

                <TabsContent value="multi">
                    <MultiAssetMonteCarloWorkspace />
                </TabsContent>
            </Tabs>
        </div>
    );
}

function buildHistogram(
    samplePaths: (number | null)[][] | undefined,
): Record<string, unknown>[] {
    if (!samplePaths || samplePaths.length === 0) return [];

    const finalValues = samplePaths
        .map((path) => path[path.length - 1])
        .filter((value): value is number => value != null);
    if (finalValues.length === 0) return [];

    const min = Math.min(...finalValues);
    const max = Math.max(...finalValues);
    const nBins = 20;
    const binWidth = (max - min) / nBins || 1;

    return Array.from({ length: nBins }, (_, index) => {
        const low = min + index * binWidth;
        const high = low + binWidth;
        const count = finalValues.filter(
            (value) =>
                value >= low &&
                (index === nBins - 1 ? value <= high : value < high),
        ).length;
        return { bin: `$${low.toFixed(0)}`, count };
    });
}

function formatStatLabel(key: string): string {
    return key
        .replace(/_/g, " ")
        .replace(/\b\w/g, (character) => character.toUpperCase());
}
