"use client";

import { EmptyState } from "@/components/common/empty-state";
import { InlineError } from "@/components/common/inline-error";
import {
    CardSkeleton,
    ChartSkeleton,
} from "@/components/common/loading-skeleton";
import { ToolLayout } from "@/components/common/tool-layout";
import { PORTFOLIO_PRESETS } from "@/app/backtesting/backtesting-options";
import { BacktestingConfigurationPanel } from "@/app/backtesting/components/backtesting-configuration-panel";
import { BacktestingPageHeader } from "@/app/backtesting/components/backtesting-page-header";
import { ResultWorkspaceSection } from "@/app/backtesting/components/result-workspace-section";
import type { BacktestingPageController } from "@/app/backtesting/use-backtesting-page-controller";
import { getEndingValue } from "@/lib/backtest-utils";
import { formatCurrencyPrecise } from "@/lib/format";
import { Activity } from "lucide-react";

interface BacktestingWorkspaceProps {
    controller: BacktestingPageController;
}

export function BacktestingWorkspace({ controller }: BacktestingWorkspaceProps) {
    const {
        form,
        configuration,
        mutations,
        result,
        resultData,
        actions,
    } = controller;
    const {
        mutation,
        saveExperimentMutation,
        comparisonMutation,
    } = mutations;

    return (
        <div className="space-y-8">
            <BacktestingPageHeader
                result={result}
                walkForwardRequest={resultData.walkForwardRequest}
                walkForwardHref={resultData.walkForwardHref}
                saveExperimentIsPending={saveExperimentMutation.isPending}
                canSaveExperiment={Boolean(form.lastRunRequest)}
                onShareConfig={actions.handleShareConfig}
                onExportCsv={actions.handleExportCsv}
                onExportReturnsCsv={actions.handleExportReturnsCsv}
                onExportTradesCsv={actions.handleExportTradesCsv}
                onExportJson={actions.handleExportJson}
                onSaveExperiment={actions.handleSaveExperiment}
            />

            <ToolLayout
                configPanel={
                    <BacktestingConfigurationPanel
                        strategy={form.strategy}
                        strategies={configuration.strategies}
                        currentStrategy={configuration.currentStrategy}
                        isAllocationStrategy={configuration.isAllocationStrategy}
                        ticker={form.ticker}
                        altTicker={form.altTicker}
                        needsMultiAsset={Boolean(configuration.needsMultiAsset)}
                        portfolioAssets={form.portfolioAssets}
                        allocationIsBalanced={configuration.allocationIsBalanced}
                        allocationWeightTotal={configuration.allocationWeightTotal}
                        presetFilter={form.presetFilter}
                        filteredPortfolioPresets={configuration.filteredPortfolioPresets}
                        savedPortfolios={form.savedPortfolios}
                        comparisonPortfolios={form.comparisonPortfolios}
                        comparisonIsPending={comparisonMutation.isPending}
                        startDate={form.startDate}
                        endDate={form.endDate}
                        cash={form.cash}
                        benchmarkTicker={form.benchmarkTicker}
                        riskFreeRate={form.riskFreeRate}
                        missingDataPolicy={form.missingDataPolicy}
                        costAssumptions={form.costAssumptions}
                        recurringContribution={form.recurringContribution}
                        contributionFrequency={form.contributionFrequency}
                        recurringWithdrawal={form.recurringWithdrawal}
                        withdrawalFrequency={form.withdrawalFrequency}
                        inflationRate={form.inflationRate}
                        oneTimeCashflows={form.oneTimeCashflows}
                        params={form.params}
                        runIsPending={mutation.isPending}
                        onStrategyChange={actions.applyStrategy}
                        onTickerChange={actions.setTicker}
                        onAltTickerChange={actions.setAltTicker}
                        onPresetFilterChange={actions.setPresetFilter}
                        onApplyPreset={actions.applyPortfolioPreset}
                        onAddPresetToComparison={actions.handleAddPresetToComparison}
                        onEqualizeWeights={actions.equalizePortfolioWeights}
                        onNormalizeWeights={actions.normalizePortfolioWeights}
                        onClearAssets={actions.clearPortfolioAssets}
                        onSavePortfolio={actions.handleSavePortfolio}
                        onAddCurrentToComparison={actions.handleAddCurrentPortfolioToComparison}
                        onAddAsset={actions.addPortfolioAsset}
                        onUpdateTicker={actions.updatePortfolioTicker}
                        onUpdateWeight={actions.updatePortfolioWeight}
                        onRemoveAsset={actions.removePortfolioAsset}
                        onApplySavedPortfolio={actions.applySavedPortfolio}
                        onAddSavedToComparison={actions.handleAddSavedToComparison}
                        onRemoveSavedPortfolio={actions.removeSavedPortfolio}
                        onRunComparison={actions.handleRunComparison}
                        onRemoveComparisonPortfolio={actions.removeComparisonPortfolio}
                        onStartDateChange={actions.setStartDate}
                        onEndDateChange={actions.setEndDate}
                        onCashChange={actions.setCash}
                        onBenchmarkTickerChange={actions.setBenchmarkTicker}
                        onRiskFreeRateChange={actions.setRiskFreeRate}
                        onMissingDataPolicyChange={actions.setMissingDataPolicy}
                        onCostAssumptionChange={actions.updateCostAssumption}
                        onRecurringContributionChange={actions.setRecurringContribution}
                        onContributionFrequencyChange={actions.setContributionFrequency}
                        onRecurringWithdrawalChange={actions.setRecurringWithdrawal}
                        onWithdrawalFrequencyChange={actions.setWithdrawalFrequency}
                        onInflationRateChange={actions.setInflationRate}
                        onOneTimeCashflowChange={actions.updateOneTimeCashflow}
                        onAddOneTimeCashflow={actions.addOneTimeCashflow}
                        onRemoveOneTimeCashflow={actions.removeOneTimeCashflow}
                        onParamsChange={actions.setParams}
                        onRun={actions.handleRun}
                    />
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
                    </>
                )}

                {resultData.hasResultWorkspace && (
                    <ResultWorkspaceSection
                        stats={resultData.stats}
                        title={
                            resultData.resultSummaryRequest?.tickers.join(" / ") ??
                            "Portfolio comparison"
                        }
                        strategy={resultData.resultSummaryRequest?.strategy}
                        detail={
                            result
                                ? `${form.lastRunRequest?.start_date} to ${form.lastRunRequest?.end_date} / ${formatCurrencyPrecise(getEndingValue(result))} ending value`
                                : `${form.comparisonRuns.length} portfolio${form.comparisonRuns.length === 1 ? "" : "s"} compared with shared dates, cashflows, costs, and data policy`
                        }
                        hasStaleResults={resultData.hasStaleResults}
                        activeTab={form.activeResultTab}
                        savedExperiment={form.savedExperiment}
                        costSummary={resultData.costSummary}
                        appliedCostAssumptions={resultData.appliedCostAssumptions}
                        costBySymbolRows={resultData.costBySymbolRows}
                        missingDataSummary={resultData.missingDataSummary}
                        walkForwardRequest={resultData.walkForwardRequest}
                        walkForwardHref={resultData.walkForwardHref}
                        withdrawalDurability={resultData.withdrawalDurability}
                        inflationAdjustedSeries={resultData.inflationAdjustedSeries}
                        cashflowEvents={resultData.cashflowEvents}
                        benchmarkStats={resultData.benchmarkStats}
                        comparisonChartSeries={resultData.comparisonChartSeries}
                        visiblePortfolioChartSeries={resultData.visiblePortfolioChartSeries}
                        valueHistory={result?.value_history ?? []}
                        portfolioChartLogScale={form.portfolioChartLogScale}
                        showPortfolioSeries={form.showPortfolioSeries}
                        showBenchmarkSeries={form.showBenchmarkSeries}
                        overviewExportBaseName={resultData.overviewExportBaseName}
                        rollingMetrics={resultData.rollingMetrics}
                        rollingChartData={resultData.rollingChartData}
                        regimeSummary={resultData.regimeSummary}
                        regimePeriods={resultData.regimePeriods}
                        regimeReferenceTicker={resultData.regimeReferenceTicker}
                        allocationChartData={resultData.allocationChartData}
                        allocationSeriesKeys={resultData.allocationSeriesKeys}
                        allocationDriftSummary={resultData.allocationDriftSummary}
                        rebalanceEvents={resultData.rebalanceEvents}
                        comparisonRuns={form.comparisonRuns}
                        comparisonRows={resultData.comparisonRows}
                        comparisonResultSeries={resultData.comparisonResultSeries}
                        comparisonDrawdownSeries={resultData.comparisonDrawdownSeries}
                        comparisonExportBaseName={resultData.comparisonExportBaseName}
                        monthlyReturns={resultData.monthlyReturns}
                        annualReturns={resultData.annualReturns}
                        trades={result?.trades ?? []}
                        onTabChange={actions.setActiveResultTab}
                        onTogglePortfolioSeries={() =>
                            actions.setShowPortfolioSeries((value) => !value)
                        }
                        onToggleBenchmarkSeries={() =>
                            actions.setShowBenchmarkSeries((value) => !value)
                        }
                        onToggleLogScale={() =>
                            actions.setPortfolioChartLogScale((value) => !value)
                        }
                        onExportComparisonCsv={actions.handleExportComparisonCsv}
                    />
                )}

                {mutation.isError && (
                    <InlineError
                        message={mutation.error?.message ?? "Backtest failed"}
                        onRetry={actions.handleRun}
                    />
                )}

                {!mutation.isPending &&
                    !mutation.isError &&
                    !result &&
                    form.comparisonRuns.length === 0 && (
                    <EmptyState
                        icon={Activity}
                        message="Configure parameters and click Run Backtest to see results."
                        presets={[
                            {
                                label: "SPY Buy & Hold",
                                onClick: () =>
                                    actions.applyPortfolioPreset(PORTFOLIO_PRESETS[0]),
                            },
                            {
                                label: "60/40 Rebalance",
                                onClick: () =>
                                    actions.applyPortfolioPreset(PORTFOLIO_PRESETS[1]),
                            },
                            {
                                label: "SPY SMA Crossover",
                                onClick: () => {
                                    actions.setTicker("SPY");
                                    actions.applyStrategy("SMACrossover");
                                },
                            },
                        ]}
                    />
                )}
            </ToolLayout>
        </div>
    );
}
