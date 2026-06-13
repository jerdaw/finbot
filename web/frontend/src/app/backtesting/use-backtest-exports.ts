"use client";

import { toast } from "sonner";
import { getEndingValue, getNumericStat } from "@/lib/backtest-utils";
import {
    buildCsv,
    buildExportBaseName,
    downloadFile,
} from "@/lib/export-utils";
import type { ComparisonRun } from "@/stores/backtest-store";
import type {
    BacktestRequest,
    BacktestResponse,
    ReturnTableRow,
    RollingMetricsResponse,
    SaveExperimentResponse,
} from "@/types/api";

interface UseBacktestExportsArgs {
    result: BacktestResponse | undefined;
    lastRunRequest: BacktestRequest | null;
    lastComparisonRequest: BacktestRequest | null;
    savedExperiment: SaveExperimentResponse | null;
    benchmarkValueHistory: Record<string, unknown>[];
    realValueHistory: Record<string, unknown>[];
    rollingMetrics: RollingMetricsResponse | null | undefined;
    monthlyReturns: ReturnTableRow[];
    annualReturns: ReturnTableRow[];
    comparisonRuns: ComparisonRun[];
}

export function useBacktestExports({
    result,
    lastRunRequest,
    lastComparisonRequest,
    savedExperiment,
    benchmarkValueHistory,
    realValueHistory,
    rollingMetrics,
    monthlyReturns,
    annualReturns,
    comparisonRuns,
}: UseBacktestExportsArgs) {
    const handleExportJson = () => {
        if (!result) {
            toast.error("Run a backtest before exporting results.");
            return;
        }

        downloadFile(
            JSON.stringify(
                {
                    request: lastRunRequest,
                    result,
                    saved_experiment: savedExperiment,
                },
                null,
                2,
            ),
            `${buildExportBaseName(lastRunRequest)}-run.json`,
            "application/json;charset=utf-8",
        );
        toast.success("Backtest JSON exported");
    };

    const handleExportCsv = () => {
        if (!result?.value_history || result.value_history.length === 0) {
            toast.error("Run a backtest before exporting results.");
            return;
        }

        const benchmarkByDate = new Map(
            benchmarkValueHistory.map((row) => [
                String(row.date ?? row.index ?? ""),
                row.Value ?? null,
            ]),
        );
        const realByDate = new Map(
            realValueHistory.map((row) => [
                String(row.date ?? row.index ?? ""),
                row.Value ?? null,
            ]),
        );
        const rollingByDate = new Map(
            (rollingMetrics?.dates ?? []).map((date, index) => [
                date,
                {
                    sharpe: rollingMetrics?.sharpe[index] ?? null,
                    volatility: rollingMetrics?.volatility[index] ?? null,
                    beta: rollingMetrics?.beta?.[index] ?? null,
                },
            ]),
        );

        const rows = result.value_history.map((row) => {
            const date = String(row.date ?? row.index ?? "");
            const rolling = rollingByDate.get(date);
            return {
                date,
                portfolio_value: row.Value ?? null,
                real_portfolio_value: realByDate.get(date) ?? null,
                benchmark_value: benchmarkByDate.get(date) ?? null,
                rolling_sharpe: rolling?.sharpe ?? null,
                rolling_volatility: rolling?.volatility ?? null,
                rolling_beta: rolling?.beta ?? null,
            };
        });

        downloadFile(
            buildCsv(rows, [
                "date",
                "portfolio_value",
                "real_portfolio_value",
                "benchmark_value",
                "rolling_sharpe",
                "rolling_volatility",
                "rolling_beta",
            ]),
            `${buildExportBaseName(lastRunRequest)}-timeseries.csv`,
            "text/csv;charset=utf-8",
        );
        toast.success("Backtest CSV exported");
    };

    const handleExportReturnsCsv = () => {
        const rows = [...monthlyReturns, ...annualReturns];
        if (rows.length === 0) {
            toast.error("No return tables are available for this run.");
            return;
        }

        downloadFile(
            buildCsv(
                rows.map((row) => ({
                    period: row.period,
                    start_value: row.start_value,
                    end_value: row.end_value,
                    return_pct: row.return_pct,
                })),
                ["period", "start_value", "end_value", "return_pct"],
            ),
            `${buildExportBaseName(lastRunRequest)}-returns.csv`,
            "text/csv;charset=utf-8",
        );
        toast.success("Returns CSV exported");
    };

    const handleExportTradesCsv = () => {
        if (!result?.trades || result.trades.length === 0) {
            toast.error("No trades are available for this run.");
            return;
        }

        downloadFile(
            buildCsv(result.trades as unknown as Array<Record<string, unknown>>, [
                "date",
                "ticker",
                "action",
                "size",
                "price",
                "value",
            ]),
            `${buildExportBaseName(lastRunRequest)}-trades.csv`,
            "text/csv;charset=utf-8",
        );
        toast.success("Trades CSV exported");
    };

    const handleExportComparisonCsv = () => {
        const rows = comparisonRuns.map((run) => ({
            portfolio: run.portfolio.label,
            status: run.error ? "error" : "complete",
            ending_value: getEndingValue(run.result ?? undefined),
            cagr: getNumericStat(run.result?.stats, "CAGR"),
            roi: getNumericStat(run.result?.stats, "ROI"),
            sharpe: getNumericStat(run.result?.stats, "Sharpe"),
            max_drawdown: getNumericStat(run.result?.stats, "Max Drawdown"),
            error: run.error ?? "",
        }));

        if (rows.length === 0) {
            toast.error("Run a portfolio comparison before exporting.");
            return;
        }

        downloadFile(
            buildCsv(rows, [
                "portfolio",
                "status",
                "ending_value",
                "cagr",
                "roi",
                "sharpe",
                "max_drawdown",
                "error",
            ]),
            `${buildExportBaseName(lastComparisonRequest ?? lastRunRequest)}-comparison.csv`,
            "text/csv;charset=utf-8",
        );
        toast.success("Comparison CSV exported");
    };

    return {
        handleExportJson,
        handleExportCsv,
        handleExportReturnsCsv,
        handleExportTradesCsv,
        handleExportComparisonCsv,
    };
}
