"use client";

import { BarChart3, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { LightweightChart } from "@/components/charts/lightweight-chart";
import { DataTable } from "@/components/common/data-table";
import { ChartCard } from "@/components/common/chart-card";
import { EmptyState } from "@/components/common/empty-state";
import { InlineError } from "@/components/common/inline-error";
import {
    formatCurrencyPrecise,
    formatNumber,
    formatPercent,
} from "@/lib/format";
import { getEndingValue } from "@/lib/backtest-utils";
import type { ComparisonRun } from "@/stores/backtest-store";
import type { TimeSeries } from "@/types/api";

export interface ComparisonMetricsRow
    extends Record<string, string | number | null> {
    portfolio: string;
    status: string;
    ending_value: number | null;
    cagr: number | null;
    roi: number | null;
    sharpe: number | null;
    max_drawdown: number | null;
    error: string;
}

interface ComparisonResultsTabProps {
    comparisonRuns: ComparisonRun[];
    comparisonRows: ComparisonMetricsRow[];
    comparisonResultSeries: TimeSeries[];
    comparisonDrawdownSeries: TimeSeries[];
    exportBaseName: string;
    onExportCsv: () => void;
}

function formatComparisonStat(key: string, value: unknown): string {
    if (typeof value !== "number") {
        return String(value ?? "N/A");
    }
    if (key === "Sharpe" || key === "Smart Sharpe") {
        return formatNumber(value, 4);
    }
    if (value < 1 && value > -1) {
        return formatPercent(value);
    }
    return formatNumber(value, 4);
}

export function ComparisonResultsTab({
    comparisonRuns,
    comparisonRows,
    comparisonResultSeries,
    comparisonDrawdownSeries,
    exportBaseName,
    onExportCsv,
}: ComparisonResultsTabProps) {
    if (comparisonRuns.length === 0) {
        return (
            <EmptyState
                icon={BarChart3}
                message="Add two or more portfolios in the portfolio builder, then run a comparison."
            />
        );
    }

    return (
        <>
            <ChartCard
                title="Portfolio Comparison"
                action={
                    <Button
                        type="button"
                        variant="outline"
                        size="xs"
                        onClick={onExportCsv}
                    >
                        <Download className="h-3.5 w-3.5" />
                        CSV
                    </Button>
                }
            >
                {comparisonResultSeries.length > 0 ? (
                    <LightweightChart
                        series={comparisonResultSeries}
                        height={400}
                        type="line"
                        downloadImageName={`${exportBaseName}-comparison`}
                    />
                ) : (
                    <p className="text-sm text-muted-foreground">
                        No successful comparison series are available.
                    </p>
                )}
            </ChartCard>

            <ChartCard title="Comparison Drawdown">
                {comparisonDrawdownSeries.length > 0 ? (
                    <LightweightChart
                        series={comparisonDrawdownSeries}
                        height={300}
                        type="line"
                        downloadImageName={`${exportBaseName}-comparison-drawdown`}
                    />
                ) : (
                    <p className="text-sm text-muted-foreground">
                        No successful comparison drawdown series are available.
                    </p>
                )}
            </ChartCard>

            <ChartCard title="Comparison Metrics">
                <DataTable
                    columns={[
                        { key: "portfolio", label: "Portfolio" },
                        { key: "status", label: "Status" },
                        {
                            key: "ending_value",
                            label: "Ending Value",
                            format: (value) =>
                                formatCurrencyPrecise(value as number | null),
                        },
                        {
                            key: "cagr",
                            label: "CAGR",
                            format: (value) =>
                                formatPercent(value as number | null),
                        },
                        {
                            key: "roi",
                            label: "ROI",
                            format: (value) =>
                                formatPercent(value as number | null),
                        },
                        {
                            key: "sharpe",
                            label: "Sharpe",
                            format: (value) =>
                                formatNumber(value as number | null, 3),
                        },
                        {
                            key: "max_drawdown",
                            label: "Max Drawdown",
                            format: (value) =>
                                formatPercent(value as number | null),
                        },
                        { key: "error", label: "Error" },
                    ]}
                    data={comparisonRows}
                />
            </ChartCard>

            <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
                {comparisonRuns.map((run) => (
                    <ChartCard
                        key={run.portfolio.id}
                        title={`${run.portfolio.label} Details`}
                    >
                        {run.error ? (
                            <InlineError message={run.error} />
                        ) : (
                            <DataTable
                                columns={[
                                    { key: "field", label: "Field" },
                                    { key: "value", label: "Value" },
                                ]}
                                data={[
                                    {
                                        field: "Tickers",
                                        value:
                                            run.request?.tickers.join(", ") ??
                                            "",
                                    },
                                    {
                                        field: "Strategy",
                                        value: run.request?.strategy ?? "",
                                    },
                                    {
                                        field: "Ending Value",
                                        value: formatCurrencyPrecise(
                                            getEndingValue(
                                                run.result ?? undefined,
                                            ),
                                        ),
                                    },
                                    ...Object.entries(
                                        run.result?.stats ?? {},
                                    ).map(([key, value]) => ({
                                        field: key,
                                        value: formatComparisonStat(key, value),
                                    })),
                                ]}
                                initialRows={8}
                            />
                        )}
                    </ChartCard>
                ))}
            </div>
        </>
    );
}
