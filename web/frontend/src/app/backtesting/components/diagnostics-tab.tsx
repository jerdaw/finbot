"use client";

import { ChartCard } from "@/components/common/chart-card";
import { DataTable } from "@/components/common/data-table";
import { StatCard } from "@/components/common/stat-card";
import { LineChartWrapper } from "@/components/charts/line-chart-wrapper";
import {
    formatCurrencyPrecise,
    formatNumber,
    formatPercent,
} from "@/lib/format";
import {
    formatBenchmarkValue,
    getMetricTrend,
} from "@/lib/backtest-utils";
import type {
    BacktestRegimePeriod,
    BacktestRegimeSummary,
    RebalanceEventRecord,
    RollingMetricsResponse,
} from "@/types/api";

interface AllocationDriftRow {
    ticker: string;
    target_weight: number;
    latest_weight: number | null;
    max_drift: number;
}

interface DiagnosticsTabProps {
    rollingMetrics: RollingMetricsResponse | null | undefined;
    rollingChartData: Record<string, unknown>[];
    regimeSummary: BacktestRegimeSummary[];
    regimePeriods: BacktestRegimePeriod[];
    regimeReferenceTicker: string | null | undefined;
    allocationChartData: Record<string, unknown>[];
    allocationSeriesKeys: string[];
    allocationDriftSummary: AllocationDriftRow[];
    rebalanceEvents: RebalanceEventRecord[];
}

export function DiagnosticsTab({
    rollingMetrics,
    rollingChartData,
    regimeSummary,
    regimePeriods,
    regimeReferenceTicker,
    allocationChartData,
    allocationSeriesKeys,
    allocationDriftSummary,
    rebalanceEvents,
}: DiagnosticsTabProps) {
    return (
        <>
            {rollingMetrics && (
                <>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                        <StatCard
                            label="Mean Rolling Sharpe"
                            value={formatBenchmarkValue(
                                rollingMetrics.mean_sharpe,
                                (value) => formatNumber(value ?? null, 3),
                            )}
                            trend={getMetricTrend(
                                rollingMetrics.mean_sharpe,
                            )}
                        />
                        <StatCard
                            label="Mean Rolling Vol"
                            value={formatBenchmarkValue(
                                rollingMetrics.mean_vol,
                                formatPercent,
                            )}
                            trend="neutral"
                        />
                        {rollingMetrics.mean_beta != null && (
                            <StatCard
                                label="Mean Rolling Beta"
                                value={formatNumber(
                                    rollingMetrics.mean_beta,
                                    3,
                                )}
                                trend="neutral"
                            />
                        )}
                    </div>

                    {rollingChartData.length > 0 && (
                        <ChartCard
                            title={`Rolling Diagnostics (${rollingMetrics.window}-day)`}
                        >
                            <LineChartWrapper
                                data={rollingChartData}
                                xKey="date"
                                series={[
                                    { key: "sharpe", color: "#2563eb" },
                                    { key: "volatility", color: "#f97316" },
                                    ...(rollingMetrics.beta
                                        ? [
                                              {
                                                  key: "beta",
                                                  color: "#16a34a",
                                              },
                                          ]
                                        : []),
                                ]}
                                height={360}
                                referenceY={0}
                                referenceLabel="Zero"
                            />
                        </ChartCard>
                    )}
                </>
            )}

            {regimeSummary.length > 0 && (
                <ChartCard
                    title={
                        regimeReferenceTicker
                            ? `Regime Summary (${regimeReferenceTicker})`
                            : "Regime Summary"
                    }
                >
                    <DataTable
                        columns={[
                            { key: "regime", label: "Regime" },
                            { key: "count_periods", label: "Periods" },
                            { key: "total_days", label: "Days" },
                            {
                                key: "cagr",
                                label: "CAGR",
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
                                key: "sharpe",
                                label: "Sharpe",
                                format: (value) =>
                                    formatNumber(value as number | null, 3),
                            },
                            {
                                key: "total_return",
                                label: "Total Return",
                                format: (value) =>
                                    formatPercent(value as number | null),
                            },
                        ]}
                        data={regimeSummary}
                    />
                </ChartCard>
            )}

            {regimePeriods.length > 0 && (
                <ChartCard title="Regime Periods">
                    <DataTable
                        columns={[
                            { key: "regime", label: "Regime" },
                            {
                                key: "start",
                                label: "Start",
                                format: (value) =>
                                    new Date(String(value)).toLocaleDateString(),
                            },
                            {
                                key: "end",
                                label: "End",
                                format: (value) =>
                                    new Date(String(value)).toLocaleDateString(),
                            },
                            { key: "days", label: "Days" },
                            {
                                key: "market_return",
                                label: "Market Return",
                                format: (value) =>
                                    formatPercent(value as number | null),
                            },
                            {
                                key: "market_volatility",
                                label: "Market Vol",
                                format: (value) =>
                                    formatPercent(value as number | null),
                            },
                            {
                                key: "portfolio_return",
                                label: "Portfolio Return",
                                format: (value) =>
                                    formatPercent(value as number | null),
                            },
                            {
                                key: "portfolio_volatility",
                                label: "Portfolio Vol",
                                format: (value) =>
                                    formatPercent(value as number | null),
                            },
                        ]}
                        data={regimePeriods}
                        initialRows={10}
                    />
                </ChartCard>
            )}

            {allocationChartData.length > 0 && (
                <>
                    <ChartCard title="Allocation Drift">
                        <LineChartWrapper
                            data={allocationChartData}
                            xKey="date"
                            series={allocationSeriesKeys.map(
                                (key, index) => ({
                                    key,
                                    color:
                                        index === 0
                                            ? "#2563eb"
                                            : index === 1
                                              ? "#16a34a"
                                              : index === 2
                                                ? "#f97316"
                                                : undefined,
                                }),
                            )}
                            height={360}
                        />
                    </ChartCard>

                    {allocationDriftSummary.length > 0 && (
                        <ChartCard title="Allocation Drift Summary">
                            <DataTable
                                columns={[
                                    { key: "ticker", label: "Ticker" },
                                    {
                                        key: "target_weight",
                                        label: "Target",
                                        format: (value) =>
                                            formatPercent(
                                                value as number | null,
                                            ),
                                    },
                                    {
                                        key: "latest_weight",
                                        label: "Latest",
                                        format: (value) =>
                                            formatPercent(
                                                value as number | null,
                                            ),
                                    },
                                    {
                                        key: "max_drift",
                                        label: "Max Drift",
                                        format: (value) =>
                                            formatPercent(
                                                value as number | null,
                                            ),
                                    },
                                ]}
                                data={allocationDriftSummary}
                            />
                        </ChartCard>
                    )}
                </>
            )}

            {rebalanceEvents.length > 0 && (
                <ChartCard title="Rebalance Log">
                    <DataTable
                        columns={[
                            {
                                key: "date",
                                label: "Date",
                                format: (value) =>
                                    new Date(String(value)).toLocaleDateString(),
                            },
                            { key: "event_type", label: "Event" },
                            { key: "trade_count", label: "Trades" },
                            {
                                key: "symbols",
                                label: "Symbols",
                                format: (value) =>
                                    Array.isArray(value)
                                        ? value.join(", ")
                                        : String(value ?? ""),
                            },
                            {
                                key: "gross_trade_value",
                                label: "Gross Value",
                                format: (value) =>
                                    formatCurrencyPrecise(
                                        value as number | null,
                                    ),
                            },
                            {
                                key: "net_trade_value",
                                label: "Net Flow",
                                format: (value) =>
                                    formatCurrencyPrecise(
                                        value as number | null,
                                    ),
                            },
                            {
                                key: "portfolio_value",
                                label: "Portfolio",
                                format: (value) =>
                                    formatCurrencyPrecise(
                                        value as number | null,
                                    ),
                            },
                            {
                                key: "cash_after",
                                label: "Cash After",
                                format: (value) =>
                                    formatCurrencyPrecise(
                                        value as number | null,
                                    ),
                            },
                        ]}
                        data={rebalanceEvents}
                        initialRows={12}
                    />
                </ChartCard>
            )}
        </>
    );
}
