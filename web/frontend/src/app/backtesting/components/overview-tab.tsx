"use client";

import { Eye, EyeOff, LineChart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChartCard } from "@/components/common/chart-card";
import { DataTable } from "@/components/common/data-table";
import { StatCard } from "@/components/common/stat-card";
import { LightweightChart } from "@/components/charts/lightweight-chart";
import { DrawdownChart } from "@/components/charts/drawdown-chart";
import {
    formatNumber,
    formatPercent,
} from "@/lib/format";
import {
    formatBenchmarkValue,
    getMetricTrend,
} from "@/lib/backtest-utils";
import type { BacktestBenchmarkStats, TimeSeries } from "@/types/api";

interface OverviewTabProps {
    benchmarkStats: BacktestBenchmarkStats | null | undefined;
    comparisonChartSeries: TimeSeries[];
    visiblePortfolioChartSeries: TimeSeries[];
    valueHistory: Record<string, unknown>[];
    portfolioChartLogScale: boolean;
    showPortfolioSeries: boolean;
    showBenchmarkSeries: boolean;
    exportBaseName: string;
    onTogglePortfolioSeries: () => void;
    onToggleBenchmarkSeries: () => void;
    onToggleLogScale: () => void;
}

export function OverviewTab({
    benchmarkStats,
    comparisonChartSeries,
    visiblePortfolioChartSeries,
    valueHistory,
    portfolioChartLogScale,
    showPortfolioSeries,
    showBenchmarkSeries,
    exportBaseName,
    onTogglePortfolioSeries,
    onToggleBenchmarkSeries,
    onToggleLogScale,
}: OverviewTabProps) {
    return (
        <>
            {benchmarkStats && (
                <>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                        <StatCard
                            label="Alpha"
                            value={formatBenchmarkValue(
                                benchmarkStats.alpha,
                                formatPercent,
                            )}
                            trend={getMetricTrend(benchmarkStats.alpha)}
                        />
                        <StatCard
                            label="Beta"
                            value={formatBenchmarkValue(
                                benchmarkStats.beta,
                                (value) => formatNumber(value ?? null, 3),
                            )}
                            trend="neutral"
                        />
                        <StatCard
                            label="R-Squared"
                            value={formatBenchmarkValue(
                                benchmarkStats.r_squared,
                                (value) => formatNumber(value ?? null, 3),
                            )}
                            trend="neutral"
                        />
                    </div>

                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                        <StatCard
                            label="Tracking Error"
                            value={formatBenchmarkValue(
                                benchmarkStats.tracking_error,
                                formatPercent,
                            )}
                            trend="neutral"
                        />
                        <StatCard
                            label="Information Ratio"
                            value={formatBenchmarkValue(
                                benchmarkStats.information_ratio,
                                (value) => formatNumber(value ?? null, 3),
                            )}
                            trend={getMetricTrend(
                                benchmarkStats.information_ratio,
                            )}
                        />
                        <StatCard
                            label="Up/Down Capture"
                            value={`${formatBenchmarkValue(benchmarkStats.up_capture, formatPercent)} / ${formatBenchmarkValue(benchmarkStats.down_capture, formatPercent)}`}
                            trend="neutral"
                        />
                    </div>
                </>
            )}

            {benchmarkStats && comparisonChartSeries.length > 0 && (
                <ChartCard
                    title={`Portfolio vs ${benchmarkStats.benchmark_name}`}
                    action={
                        <>
                            <Button
                                type="button"
                                variant="outline"
                                size="xs"
                                onClick={onTogglePortfolioSeries}
                            >
                                {showPortfolioSeries ? (
                                    <Eye className="h-3.5 w-3.5" />
                                ) : (
                                    <EyeOff className="h-3.5 w-3.5" />
                                )}
                                Portfolio
                            </Button>
                            <Button
                                type="button"
                                variant="outline"
                                size="xs"
                                onClick={onToggleBenchmarkSeries}
                            >
                                {showBenchmarkSeries ? (
                                    <Eye className="h-3.5 w-3.5" />
                                ) : (
                                    <EyeOff className="h-3.5 w-3.5" />
                                )}
                                Benchmark
                            </Button>
                            <Button
                                type="button"
                                variant="outline"
                                size="xs"
                                onClick={onToggleLogScale}
                            >
                                <LineChart className="h-3.5 w-3.5" />
                                {portfolioChartLogScale ? "Linear" : "Log"}
                            </Button>
                        </>
                    }
                >
                    <LightweightChart
                        series={visiblePortfolioChartSeries}
                        height={400}
                        type="line"
                        logScale={portfolioChartLogScale}
                        downloadImageName={`${exportBaseName}-portfolio`}
                    />
                </ChartCard>
            )}

            {!benchmarkStats && valueHistory.length > 0 && (
                <ChartCard
                    title="Portfolio Value"
                    action={
                        <Button
                            type="button"
                            variant="outline"
                            size="xs"
                            onClick={onToggleLogScale}
                        >
                            <LineChart className="h-3.5 w-3.5" />
                            {portfolioChartLogScale ? "Linear" : "Log"}
                        </Button>
                    }
                >
                    <LightweightChart
                        series={[
                            {
                                name: "Value",
                                dates: valueHistory.map((row) =>
                                    String(row.date),
                                ),
                                values: valueHistory.map(
                                    (row) => row.Value as number,
                                ),
                            },
                        ]}
                        height={400}
                        type="area"
                        logScale={portfolioChartLogScale}
                        downloadImageName={`${exportBaseName}-portfolio`}
                    />
                </ChartCard>
            )}

            {valueHistory.length > 0 && (
                <ChartCard title="Drawdown">
                    <DrawdownChart
                        data={valueHistory.map((row) => ({
                            date: String(row.date),
                            value: row.Value as number,
                        }))}
                        height={200}
                    />
                </ChartCard>
            )}

            {benchmarkStats && (
                <ChartCard title="Benchmark Comparison">
                    <DataTable
                        columns={[
                            { key: "metric", label: "Metric" },
                            { key: "value", label: "Value" },
                        ]}
                        data={[
                            {
                                metric: "Benchmark",
                                value: benchmarkStats.benchmark_name,
                            },
                            {
                                metric: "Observations",
                                value: String(benchmarkStats.n_observations),
                            },
                            {
                                metric: "Alpha",
                                value: formatBenchmarkValue(
                                    benchmarkStats.alpha,
                                    formatPercent,
                                ),
                            },
                            {
                                metric: "Beta",
                                value: formatBenchmarkValue(
                                    benchmarkStats.beta,
                                    (value) => formatNumber(value ?? null, 4),
                                ),
                            },
                            {
                                metric: "R-Squared",
                                value: formatBenchmarkValue(
                                    benchmarkStats.r_squared,
                                    (value) => formatNumber(value ?? null, 4),
                                ),
                            },
                            {
                                metric: "Tracking Error",
                                value: formatBenchmarkValue(
                                    benchmarkStats.tracking_error,
                                    formatPercent,
                                ),
                            },
                            {
                                metric: "Information Ratio",
                                value: formatBenchmarkValue(
                                    benchmarkStats.information_ratio,
                                    (value) => formatNumber(value ?? null, 4),
                                ),
                            },
                            {
                                metric: "Up Capture",
                                value: formatBenchmarkValue(
                                    benchmarkStats.up_capture,
                                    formatPercent,
                                ),
                            },
                            {
                                metric: "Down Capture",
                                value: formatBenchmarkValue(
                                    benchmarkStats.down_capture,
                                    formatPercent,
                                ),
                            },
                        ]}
                    />
                </ChartCard>
            )}
        </>
    );
}
