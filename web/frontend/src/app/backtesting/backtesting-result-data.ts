import type { ComparisonMetricsRow } from "@/app/backtesting/components/comparison-results-tab";
import {
    buildDrawdownValues,
    buildWalkForwardHref,
    cloneAssets,
    getEndingValue,
    getNumericStat,
    normalizeRequestForSignature,
} from "@/lib/backtest-utils";
import { buildExportBaseName } from "@/lib/export-utils";
import type {
    BacktestCostAssumptions,
    BacktestRequest,
    BacktestResponse,
    MissingDataPolicy,
    OneTimeCashflowEvent,
    RecurringCashflowRule,
} from "@/types/api";
import type {
    ComparisonRun,
    PortfolioAsset,
} from "@/stores/backtest-store";

interface BuildBacktestResultDataArgs {
    result: BacktestResponse | undefined;
    lastRunRequest: BacktestRequest | null;
    lastComparisonRequest: BacktestRequest | null;
    comparisonRuns: ComparisonRun[];
    showPortfolioSeries: boolean;
    showBenchmarkSeries: boolean;
    costAssumptions: BacktestCostAssumptions;
    params: Record<string, number>;
    ticker: string;
    altTicker: string;
    portfolioAssets: PortfolioAsset[];
    strategy: string;
    startDate: string;
    endDate: string;
    cash: number;
    benchmarkTicker: string;
    riskFreeRate: number;
    recurringContribution: number;
    contributionFrequency: RecurringCashflowRule["frequency"];
    recurringWithdrawal: number;
    withdrawalFrequency: RecurringCashflowRule["frequency"];
    oneTimeCashflows: OneTimeCashflowEvent[];
    inflationRate: number;
    missingDataPolicy: MissingDataPolicy;
    isAllocationStrategy: boolean;
    needsMultiAsset: boolean | undefined;
}

export function buildBacktestResultData({
    result,
    lastRunRequest,
    lastComparisonRequest,
    comparisonRuns,
    showPortfolioSeries,
    showBenchmarkSeries,
    costAssumptions,
    params,
    ticker,
    altTicker,
    portfolioAssets,
    strategy,
    startDate,
    endDate,
    cash,
    benchmarkTicker,
    riskFreeRate,
    recurringContribution,
    contributionFrequency,
    recurringWithdrawal,
    withdrawalFrequency,
    oneTimeCashflows,
    inflationRate,
    missingDataPolicy,
    isAllocationStrategy,
    needsMultiAsset,
}: BuildBacktestResultDataArgs) {
    const stats = result?.stats;
    const benchmarkStats = result?.benchmark_stats;
    const benchmarkValueHistory = result?.benchmark_value_history ?? [];
    const cashflowEvents = result?.cashflow_events ?? [];
    const realValueHistory = result?.real_value_history ?? [];
    const withdrawalDurability = result?.withdrawal_durability;
    const allocationHistory = result?.allocation_history ?? [];
    const rebalanceEvents = result?.rebalance_events ?? [];
    const rollingMetrics = result?.rolling_metrics;
    const appliedCostAssumptions = result?.applied_cost_assumptions;
    const costSummary = result?.cost_summary;
    const missingDataSummary = result?.missing_data_summary;
    const walkForwardRequest = result?.walk_forward_request;
    const regimeReferenceTicker = result?.regime_reference_ticker;
    const regimeSummary = result?.regime_summary ?? [];
    const regimePeriods = result?.regime_periods ?? [];
    const monthlyReturns = result?.monthly_returns ?? [];
    const annualReturns = result?.annual_returns ?? [];
    const walkForwardHref = buildWalkForwardHref(walkForwardRequest);
    const resultSummaryRequest = result ? lastRunRequest : lastComparisonRequest;
    const costBySymbolRows = Object.entries(
        costSummary?.costs_by_symbol ?? {},
    ).map(([tickerSymbol, total]) => ({
        ticker: tickerSymbol,
        total_cost: total,
    }));
    const inflationAdjustedSeries =
        realValueHistory.length > 0
            ? [
                  {
                      name: "Nominal",
                      dates:
                          result?.value_history?.map((r) => String(r.date)) ??
                          [],
                      values:
                          result?.value_history?.map(
                              (r) => r.Value as number,
                          ) ?? [],
                      color: "#2563eb",
                  },
                  {
                      name: "Real",
                      dates: realValueHistory.map((r) => String(r.date)),
                      values: realValueHistory.map((r) => r.Value as number),
                      color: "#f97316",
                  },
              ]
            : [];
    const rollingChartData =
        rollingMetrics?.dates.map((date, index) => ({
            date,
            sharpe: rollingMetrics.sharpe[index],
            volatility: rollingMetrics.volatility[index],
            beta: rollingMetrics.beta?.[index] ?? null,
        })) ?? [];
    const allocationSeriesKeys = Object.keys(allocationHistory[0] ?? {}).filter(
        (key) => key !== "date" && key !== "index",
    );
    const allocationChartData = allocationHistory.map((row) => {
        const chartRow: Record<string, unknown> = {
            date: String(row.date ?? row.index ?? ""),
        };
        allocationSeriesKeys.forEach((key) => {
            const value = row[key];
            chartRow[key] = typeof value === "number" ? value : null;
        });
        return chartRow;
    });
    let targetWeightMap: Record<string, number> = {};
    const noRebalanceWeights =
        lastRunRequest?.strategy_params["equity_proportions"];
    const rebalanceWeights =
        lastRunRequest?.strategy_params["rebal_proportions"];
    if (
        lastRunRequest?.strategy === "NoRebalance" &&
        Array.isArray(noRebalanceWeights)
    ) {
        targetWeightMap = Object.fromEntries(
            lastRunRequest.tickers.map((tickerSymbol, index) => [
                tickerSymbol,
                Number(noRebalanceWeights[index]),
            ]),
        );
    } else if (
        lastRunRequest?.strategy === "Rebalance" &&
        Array.isArray(rebalanceWeights)
    ) {
        targetWeightMap = Object.fromEntries(
            lastRunRequest.tickers.map((tickerSymbol, index) => [
                tickerSymbol,
                Number(rebalanceWeights[index]),
            ]),
        );
    }
    const latestAllocation = allocationHistory[allocationHistory.length - 1];
    const allocationDriftSummary = Object.keys(targetWeightMap).map(
        (tickerSymbol) => {
            const latestWeight = latestAllocation?.[tickerSymbol];
            let maxDrift = 0;
            allocationHistory.forEach((row) => {
                const rowValue = row[tickerSymbol];
                if (typeof rowValue === "number") {
                    maxDrift = Math.max(
                        maxDrift,
                        Math.abs(rowValue - targetWeightMap[tickerSymbol]),
                    );
                }
            });
            return {
                ticker: tickerSymbol,
                target_weight: targetWeightMap[tickerSymbol],
                latest_weight:
                    typeof latestWeight === "number" ? latestWeight : null,
                max_drift: maxDrift,
            };
        },
    );
    const comparisonChartSeries =
        result?.value_history && result.value_history.length > 0
            ? [
                  {
                      name: "Portfolio",
                      dates: result.value_history.map((r) => String(r.date)),
                      values: result.value_history.map(
                          (r) => r.Value as number,
                      ),
                      color: "#3b82f6",
                  },
                  ...(benchmarkStats && benchmarkValueHistory.length > 0
                      ? [
                            {
                                name: benchmarkStats.benchmark_name,
                                dates: benchmarkValueHistory.map((r) =>
                                    String(r.date),
                                ),
                                values: benchmarkValueHistory.map(
                                    (r) => r.Value as number,
                                ),
                                color: "#22c55e",
                            },
                        ]
                      : []),
              ]
            : [];
    const visiblePortfolioChartSeries = comparisonChartSeries.filter((series) => {
        if (series.name === "Portfolio") {
            return showPortfolioSeries;
        }
        return showBenchmarkSeries;
    });
    const normalizedCurrentCostAssumptions: BacktestCostAssumptions = {
        ...costAssumptions,
        commission_per_share: Number(costAssumptions.commission_per_share),
        commission_bps: Number(costAssumptions.commission_bps),
        commission_minimum: Number(costAssumptions.commission_minimum),
        spread_bps: Number(costAssumptions.spread_bps),
        slippage_bps: Number(costAssumptions.slippage_bps),
    };
    const currentInputSignature = normalizeRequestForSignature(
        (() => {
            const strategyParams: Record<string, unknown> = { ...params };
            let currentTickers = [ticker.trim().toUpperCase()];
            const currentRecurringCashflows: RecurringCashflowRule[] = [];
            const currentOneTimeCashflows = oneTimeCashflows
                .filter(
                    (event) =>
                        event.date.trim().length > 0 ||
                        event.amount !== 0 ||
                        (event.label?.trim().length ?? 0) > 0,
                )
                .map((event) => ({
                    date: event.date.trim(),
                    amount: Number(event.amount),
                    label: event.label?.trim() || undefined,
                }));

            if (isAllocationStrategy) {
                const cleanedAssets = cloneAssets(portfolioAssets).filter(
                    (asset) => asset.ticker.length > 0,
                );
                currentTickers = cleanedAssets.map((asset) => asset.ticker);
                const currentWeights = cleanedAssets.map(
                    (asset) => asset.weight / 100,
                );
                if (strategy === "NoRebalance") {
                    strategyParams.equity_proportions = currentWeights;
                }
                if (strategy === "Rebalance") {
                    strategyParams.rebal_proportions = currentWeights;
                }
            } else if (needsMultiAsset) {
                currentTickers = [
                    ticker.trim().toUpperCase(),
                    altTicker.trim().toUpperCase(),
                ];
            }

            if (recurringContribution > 0) {
                currentRecurringCashflows.push({
                    amount: recurringContribution,
                    frequency: contributionFrequency,
                    start_date: startDate,
                    end_date: endDate,
                    label: `Recurring contribution (${contributionFrequency})`,
                });
            }
            if (recurringWithdrawal > 0) {
                currentRecurringCashflows.push({
                    amount: -recurringWithdrawal,
                    frequency: withdrawalFrequency,
                    start_date: startDate,
                    end_date: endDate,
                    label: `Recurring withdrawal (${withdrawalFrequency})`,
                });
            }

            return {
                tickers: currentTickers,
                strategy,
                strategy_params: strategyParams,
                start_date: startDate,
                end_date: endDate,
                initial_cash: cash,
                benchmark_ticker: benchmarkTicker.trim()
                    ? benchmarkTicker.trim().toUpperCase()
                    : undefined,
                risk_free_rate: riskFreeRate,
                recurring_cashflows:
                    currentRecurringCashflows.length > 0
                        ? currentRecurringCashflows
                        : undefined,
                one_time_cashflows:
                    currentOneTimeCashflows.length > 0
                        ? currentOneTimeCashflows
                        : undefined,
                inflation_rate: inflationRate,
                missing_data_policy: missingDataPolicy,
                cost_assumptions: normalizedCurrentCostAssumptions,
            };
        })(),
    );
    const lastRunInputSignature = normalizeRequestForSignature(lastRunRequest);
    const hasStaleResults = Boolean(
        result &&
            lastRunInputSignature &&
            currentInputSignature !== lastRunInputSignature,
    );
    const comparisonRows: ComparisonMetricsRow[] = comparisonRuns.map((run) => ({
        portfolio: run.portfolio.label,
        status: run.error ? "Error" : "Complete",
        ending_value: getEndingValue(run.result ?? undefined),
        cagr: getNumericStat(run.result?.stats, "CAGR"),
        roi: getNumericStat(run.result?.stats, "ROI"),
        sharpe: getNumericStat(run.result?.stats, "Sharpe"),
        max_drawdown: getNumericStat(run.result?.stats, "Max Drawdown"),
        error: run.error ?? "",
    }));
    const comparisonResultSeries = comparisonRuns
        .filter((run) => run.result?.value_history?.length)
        .map((run, index) => ({
            name: run.portfolio.label,
            dates: run.result?.value_history.map((row) => String(row.date)) ?? [],
            values:
                run.result?.value_history.map((row) => {
                    const firstValue = run.result?.value_history[0]?.Value;
                    const currentValue = row.Value;
                    if (
                        typeof firstValue === "number" &&
                        firstValue !== 0 &&
                        typeof currentValue === "number"
                    ) {
                        return (currentValue / firstValue) * 100;
                    }
                    return null;
                }) ?? [],
            color:
                index === 0
                    ? "#3b82f6"
                    : index === 1
                      ? "#22c55e"
                      : index === 2
                        ? "#f97316"
                        : index === 3
                          ? "#a855f7"
                          : "#06b6d4",
        }));
    const comparisonDrawdownSeries = comparisonResultSeries.map((series) => ({
        ...series,
        values: buildDrawdownValues(series.values),
    }));
    const overviewExportBaseName = buildExportBaseName(lastRunRequest);
    const comparisonExportBaseName = buildExportBaseName(
        lastComparisonRequest ?? lastRunRequest,
    );
    const hasResultWorkspace = Boolean(stats || comparisonRuns.length > 0);

    return {
        stats,
        benchmarkStats,
        benchmarkValueHistory,
        cashflowEvents,
        realValueHistory,
        withdrawalDurability,
        rebalanceEvents,
        rollingMetrics,
        appliedCostAssumptions,
        costSummary,
        missingDataSummary,
        walkForwardRequest,
        regimeReferenceTicker,
        regimeSummary,
        regimePeriods,
        monthlyReturns,
        annualReturns,
        walkForwardHref,
        resultSummaryRequest,
        costBySymbolRows,
        inflationAdjustedSeries,
        rollingChartData,
        allocationSeriesKeys,
        allocationChartData,
        allocationDriftSummary,
        comparisonChartSeries,
        visiblePortfolioChartSeries,
        hasStaleResults,
        comparisonRows,
        comparisonResultSeries,
        comparisonDrawdownSeries,
        overviewExportBaseName,
        comparisonExportBaseName,
        hasResultWorkspace,
    };
}
