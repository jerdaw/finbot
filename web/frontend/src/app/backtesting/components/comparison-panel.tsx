"use client";

import { useBacktestStore } from "@/stores/backtest-store";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/common/data-table";
import { getEndingValue, getNumericStat } from "@/lib/backtest-utils";
import { formatCurrencyPrecise, formatPercent, formatNumber } from "@/lib/format";
import { Trash2 } from "lucide-react";

export function ComparisonPanel() {
    const { comparisonPortfolios, comparisonRuns, removeComparisonPortfolio } = useBacktestStore();

    if (comparisonPortfolios.length === 0 && comparisonRuns.length === 0) {
        return (
            <div className="text-center p-8 text-muted-foreground border rounded-md">
                No comparison runs available. Add portfolios to compare.
            </div>
        );
    }

    const comparisonData = comparisonRuns.map(run => ({
        portfolio: run.portfolio.label,
        status: run.error ? "Error" : "Complete",
        endingValue: formatCurrencyPrecise(getEndingValue(run.result ?? undefined) || 0),
        cagr: formatPercent((getNumericStat(run.result?.stats, "CAGR") || 0)),
        maxDrawdown: formatPercent((getNumericStat(run.result?.stats, "Max Drawdown") || 0)),
        sharpe: formatNumber((getNumericStat(run.result?.stats, "Sharpe") || 0)),
    }));

    return (
        <div className="space-y-6 mt-8 animate-in fade-in">
            <h2 className="text-2xl font-bold tracking-tight">Portfolio Comparison</h2>

            <div className="border rounded-md p-4">
                <h3 className="text-lg font-medium mb-4">Comparison Results</h3>
                <DataTable
                    data={comparisonData}
                    columns={[
                        { header: "Portfolio", accessorKey: "portfolio" },
                        { header: "Status", accessorKey: "status" },
                        { header: "Ending Value", accessorKey: "endingValue" },
                        { header: "CAGR", accessorKey: "cagr" },
                        { header: "Max Drawdown", accessorKey: "maxDrawdown" },
                        { header: "Sharpe", accessorKey: "sharpe" }
                    ]}
                />
            </div>

            <div className="border rounded-md p-4 bg-muted/50">
                <h3 className="text-lg font-medium mb-4">Portfolios in Queue</h3>
                <div className="space-y-2">
                    {comparisonPortfolios.map(p => (
                        <div key={p.id} className="flex justify-between items-center p-2 bg-background border rounded-md shadow-sm">
                            <div>
                                <div className="font-medium">{p.label}</div>
                                <div className="text-xs text-muted-foreground">{p.strategy}</div>
                            </div>
                            <Button variant="ghost" size="icon" onClick={() => removeComparisonPortfolio(p.id)}>
                                <Trash2 className="w-4 h-4 text-destructive" />
                            </Button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
