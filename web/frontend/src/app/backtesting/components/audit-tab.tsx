"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ChartCard } from "@/components/common/chart-card";
import { DataTable } from "@/components/common/data-table";
import { StatCard } from "@/components/common/stat-card";
import {
    formatCurrencyPrecise,
    formatNumber,
    formatPercent,
} from "@/lib/format";
import type {
    AppliedBacktestCostAssumptions,
    BacktestCostSummary,
    BacktestMissingDataSummary,
    SaveExperimentResponse,
    WalkForwardHandoff,
} from "@/types/api";

interface CostBySymbolRow extends Record<string, string | number> {
    ticker: string;
    total_cost: number;
}

interface AuditTabProps {
    savedExperiment: SaveExperimentResponse | null;
    costSummary: BacktestCostSummary | null | undefined;
    appliedCostAssumptions: AppliedBacktestCostAssumptions | undefined;
    costBySymbolRows: CostBySymbolRow[];
    missingDataSummary: BacktestMissingDataSummary | undefined;
    walkForwardRequest: WalkForwardHandoff | null | undefined;
    walkForwardHref: string;
    stats: Record<string, unknown> | null | undefined;
}

function formatStatisticValue(metric: string, value: unknown): string {
    if (typeof value !== "number") {
        return String(value ?? "N/A");
    }
    if (
        value < 1 &&
        value > -1 &&
        metric !== "Sharpe" &&
        metric !== "Smart Sharpe"
    ) {
        return formatPercent(value);
    }
    return formatNumber(value, 4);
}

export function AuditTab({
    savedExperiment,
    costSummary,
    appliedCostAssumptions,
    costBySymbolRows,
    missingDataSummary,
    walkForwardRequest,
    walkForwardHref,
    stats,
}: AuditTabProps) {
    return (
        <>
            {savedExperiment && (
                <ChartCard title="Experiment Lineage">
                    <DataTable
                        columns={[
                            { key: "field", label: "Field" },
                            { key: "value", label: "Value" },
                        ]}
                        data={[
                            {
                                field: "Run ID",
                                value: savedExperiment.run_id,
                            },
                            {
                                field: "Strategy",
                                value: savedExperiment.strategy_name,
                            },
                            {
                                field: "Created At",
                                value: new Date(
                                    savedExperiment.created_at,
                                ).toLocaleString(),
                            },
                            {
                                field: "Config Hash",
                                value: savedExperiment.config_hash,
                            },
                            {
                                field: "Data Snapshot",
                                value: savedExperiment.data_snapshot_id,
                            },
                        ]}
                    />
                </ChartCard>
            )}

            {costSummary && appliedCostAssumptions && (
                <>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                        <StatCard
                            label="Estimated Costs"
                            value={formatCurrencyPrecise(
                                costSummary.total_costs,
                            )}
                            trend="down"
                        />
                        <StatCard
                            label="Commission"
                            value={formatCurrencyPrecise(
                                costSummary.total_commission,
                            )}
                            trend="down"
                        />
                        <StatCard
                            label="Spread"
                            value={formatCurrencyPrecise(
                                costSummary.total_spread,
                            )}
                            trend="down"
                        />
                        <StatCard
                            label="Slippage"
                            value={formatCurrencyPrecise(
                                costSummary.total_slippage,
                            )}
                            trend="down"
                        />
                    </div>

                    <ChartCard title="Execution Frictions">
                        <DataTable
                            columns={[
                                { key: "field", label: "Field" },
                                { key: "value", label: "Value" },
                            ]}
                            data={[
                                {
                                    field: "Commission Model",
                                    value: appliedCostAssumptions.commission_label,
                                },
                                {
                                    field: "Spread Model",
                                    value: appliedCostAssumptions.spread_label,
                                },
                                {
                                    field: "Slippage Model",
                                    value: appliedCostAssumptions.slippage_label,
                                },
                                {
                                    field: "Equity Curve Impact",
                                    value: appliedCostAssumptions.estimated_only
                                        ? "Estimated separately from the equity curve"
                                        : "Applied directly to the equity curve",
                                },
                            ]}
                        />
                    </ChartCard>

                    {costBySymbolRows.length > 0 && (
                        <ChartCard title="Estimated Costs by Symbol">
                            <DataTable
                                columns={[
                                    { key: "ticker", label: "Ticker" },
                                    {
                                        key: "total_cost",
                                        label: "Estimated Cost",
                                        format: (value) =>
                                            formatCurrencyPrecise(
                                                value as number | null,
                                            ),
                                    },
                                ]}
                                data={costBySymbolRows}
                            />
                        </ChartCard>
                    )}
                </>
            )}

            {missingDataSummary && (
                <ChartCard title="Missing Data Handling">
                    <div className="mb-3 space-y-1 text-sm text-muted-foreground">
                        <p>Policy: {missingDataSummary.policy}</p>
                        {missingDataSummary.note && (
                            <p>{missingDataSummary.note}</p>
                        )}
                    </div>
                    <DataTable
                        columns={[
                            { key: "ticker", label: "Ticker" },
                            {
                                key: "had_missing_data",
                                label: "Had Gaps",
                                format: (value) => (value ? "Yes" : "No"),
                            },
                            { key: "missing_rows", label: "Missing Rows" },
                            { key: "missing_cells", label: "Missing Cells" },
                            { key: "rows_dropped", label: "Rows Dropped" },
                            {
                                key: "remaining_missing_cells",
                                label: "Remaining Gaps",
                            },
                        ]}
                        data={missingDataSummary.tickers}
                        initialRows={8}
                    />
                </ChartCard>
            )}

            {walkForwardRequest && (
                <ChartCard title="Walk-Forward Follow-Up">
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                        <div className="space-y-1">
                            <p className="text-sm text-muted-foreground">
                                {walkForwardRequest.reason}
                            </p>
                            <p className="text-xs text-muted-foreground/70">
                                Suggested windows: train{" "}
                                {walkForwardRequest.train_window} days, test{" "}
                                {walkForwardRequest.test_window} days, step{" "}
                                {walkForwardRequest.step_size} days.
                            </p>
                        </div>
                        <Button asChild>
                            <Link href={walkForwardHref}>
                                Open Walk-Forward Analysis
                            </Link>
                        </Button>
                    </div>
                </ChartCard>
            )}

            <ChartCard title="Metric Methodology">
                <DataTable
                    columns={[
                        { key: "metric", label: "Metric" },
                        { key: "basis", label: "Calculation Basis" },
                    ]}
                    data={[
                        {
                            metric: "Max Drawdown",
                            basis: "Peak-to-trough decline computed directly from the portfolio value path. This matches the drawdown chart.",
                        },
                        {
                            metric: "CAGR",
                            basis: "Annualized compound growth from starting value, ending value, and elapsed trading history.",
                        },
                        {
                            metric: "Sharpe",
                            basis: "QuantStats daily-return ratio derived from the same portfolio value history.",
                        },
                        {
                            metric: "ROI",
                            basis: "Ending value divided by starting value minus one.",
                        },
                    ]}
                />
            </ChartCard>

            {stats && (
                <ChartCard title="Full Statistics">
                    <DataTable
                        columns={[
                            { key: "metric", label: "Metric" },
                            { key: "value", label: "Value" },
                        ]}
                        data={Object.entries(stats).map(([metric, value]) => ({
                            metric,
                            value: formatStatisticValue(metric, value),
                        }))}
                        initialRows={18}
                    />
                </ChartCard>
            )}
        </>
    );
}
