"use client";

import { ChartCard } from "@/components/common/chart-card";
import { DataTable } from "@/components/common/data-table";
import { StatCard } from "@/components/common/stat-card";
import { LightweightChart } from "@/components/charts/lightweight-chart";
import {
    formatCurrencyPrecise,
    formatPercent,
} from "@/lib/format";
import { getMetricTrend } from "@/lib/backtest-utils";
import type {
    CashflowEventRecord,
    TimeSeries,
    WithdrawalDurabilitySummary,
} from "@/types/api";

interface CashflowsTabProps {
    withdrawalDurability: WithdrawalDurabilitySummary | null | undefined;
    inflationAdjustedSeries: TimeSeries[];
    cashflowEvents: CashflowEventRecord[];
}

export function CashflowsTab({
    withdrawalDurability,
    inflationAdjustedSeries,
    cashflowEvents,
}: CashflowsTabProps) {
    if (!withdrawalDurability) {
        return null;
    }

    return (
        <>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <StatCard
                    label="Withdrawal Plan"
                    value={
                        withdrawalDurability.survived_to_end
                            ? "Survived"
                            : "Depleted"
                    }
                    trend={
                        withdrawalDurability.survived_to_end ? "up" : "down"
                    }
                />
                <StatCard
                    label="Real Ending Value"
                    value={formatCurrencyPrecise(
                        withdrawalDurability.ending_real_value,
                    )}
                    trend={getMetricTrend(
                        withdrawalDurability.real_total_return,
                    )}
                />
                <StatCard
                    label="Total Withdrawals"
                    value={formatCurrencyPrecise(
                        withdrawalDurability.total_withdrawals,
                    )}
                    trend="neutral"
                />
                <StatCard
                    label="Net Cashflow"
                    value={formatCurrencyPrecise(
                        withdrawalDurability.net_cashflow,
                    )}
                    trend={getMetricTrend(withdrawalDurability.net_cashflow)}
                />
            </div>

            {inflationAdjustedSeries.length > 0 && (
                <ChartCard
                    title={`Nominal vs Real Value (${formatPercent(withdrawalDurability.inflation_rate)} inflation)`}
                >
                    <LightweightChart
                        series={inflationAdjustedSeries}
                        height={360}
                        type="line"
                    />
                </ChartCard>
            )}

            {cashflowEvents.length > 0 && (
                <ChartCard title="Cashflow Log">
                    <DataTable
                        columns={[
                            {
                                key: "scheduled_date",
                                label: "Scheduled",
                                format: (value) =>
                                    new Date(String(value)).toLocaleDateString(),
                            },
                            {
                                key: "applied_date",
                                label: "Applied",
                                format: (value) =>
                                    new Date(String(value)).toLocaleDateString(),
                            },
                            { key: "label", label: "Label" },
                            { key: "source", label: "Type" },
                            { key: "direction", label: "Direction" },
                            {
                                key: "amount",
                                label: "Amount",
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
                            {
                                key: "portfolio_value_after",
                                label: "Portfolio After",
                                format: (value) =>
                                    formatCurrencyPrecise(
                                        value as number | null,
                                    ),
                            },
                        ]}
                        data={cashflowEvents}
                        initialRows={12}
                    />
                </ChartCard>
            )}
        </>
    );
}
