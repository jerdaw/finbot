"use client";

import { DataTable } from "@/components/common/data-table";
import { ChartCard } from "@/components/common/chart-card";
import { formatCurrencyPrecise, formatNumber, formatPercent } from "@/lib/format";
import type { ReturnTableRow, TradeRecord } from "@/types/api";

interface ReturnsTabProps {
    monthlyReturns: ReturnTableRow[];
    annualReturns: ReturnTableRow[];
    trades: TradeRecord[];
}

const returnColumns = [
    { key: "period", label: "Period" },
    {
        key: "start_value",
        label: "Start Value",
        format: (value: unknown) => formatCurrencyPrecise(value as number | null),
    },
    {
        key: "end_value",
        label: "End Value",
        format: (value: unknown) => formatCurrencyPrecise(value as number | null),
    },
    {
        key: "return_pct",
        label: "Return",
        format: (value: unknown) => formatPercent(value as number | null),
    },
];

export function ReturnsTab({
    monthlyReturns,
    annualReturns,
    trades,
}: ReturnsTabProps) {
    return (
        <>
            {monthlyReturns.length > 0 && (
                <ChartCard title="Monthly Returns">
                    <DataTable
                        columns={returnColumns}
                        data={monthlyReturns}
                        initialRows={12}
                    />
                </ChartCard>
            )}

            {annualReturns.length > 0 && (
                <ChartCard title="Annual Returns">
                    <DataTable
                        columns={[
                            { ...returnColumns[0], label: "Year" },
                            ...returnColumns.slice(1),
                        ]}
                        data={annualReturns}
                        initialRows={12}
                    />
                </ChartCard>
            )}

            {trades.length > 0 && (
                <ChartCard title={`Trades (${trades.length})`}>
                    <DataTable
                        columns={[
                            { key: "date", label: "Date" },
                            { key: "ticker", label: "Ticker" },
                            { key: "action", label: "Action" },
                            {
                                key: "size",
                                label: "Size",
                                format: (value) =>
                                    formatNumber(value as number, 0),
                            },
                            {
                                key: "price",
                                label: "Price",
                                format: (value) =>
                                    formatCurrencyPrecise(value as number),
                            },
                            {
                                key: "value",
                                label: "Value",
                                format: (value) =>
                                    formatCurrencyPrecise(value as number),
                            },
                        ]}
                        data={trades}
                        initialRows={15}
                    />
                </ChartCard>
            )}
        </>
    );
}
