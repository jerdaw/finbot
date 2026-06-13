"use client";

import { toast } from "sonner";
import { ToolLayout } from "@/components/common/tool-layout";
import { EmptyState } from "@/components/common/empty-state";
import { InlineError } from "@/components/common/inline-error";
import {
    ChartSkeleton,
    CardSkeleton,
} from "@/components/common/loading-skeleton";
import {
    Activity,
} from "lucide-react";
import { formatCurrencyPrecise } from "@/lib/format";
import { useBacktestStore } from "@/stores/backtest-store";
import type {
    BacktestRequest,
} from "@/types/api";
import type {
    ComparisonPortfolio,
} from "@/stores/backtest-store";
import { PORTFOLIO_PRESETS } from "@/app/backtesting/backtesting-options";
import {
    getEndingValue,
} from "@/lib/backtest-utils";
import { BacktestingConfigurationPanel } from "@/app/backtesting/components/backtesting-configuration-panel";
import { BacktestingPageHeader } from "@/app/backtesting/components/backtesting-page-header";
import { ResultWorkspaceSection } from "@/app/backtesting/components/result-workspace-section";
import { useBacktestExports } from "@/app/backtesting/use-backtest-exports";
import { buildBacktestResultData } from "@/app/backtesting/backtesting-result-data";
import {
    buildBacktestRequestPayload,
    buildComparisonBacktestRequest,
} from "@/app/backtesting/backtesting-request-builder";
import { useBacktestingConfigurationData } from "@/app/backtesting/use-backtesting-configuration-data";
import { useBacktestingFormActions } from "@/app/backtesting/use-backtesting-form-actions";
import { useBacktestingMutations } from "@/app/backtesting/use-backtesting-mutations";
import { useBacktestingPortfolioActions } from "@/app/backtesting/use-backtesting-portfolio-actions";
import { useBacktestingRunActions } from "@/app/backtesting/use-backtesting-run-actions";

export default function BacktestingPage() {
    // ---------------------------------------------------------------------------
    // Centralised state — all fields persisted to localStorage via zustand/persist
    // ---------------------------------------------------------------------------
    const {
        ticker, setTicker,
        altTicker, setAltTicker,
        portfolioAssets, setPortfolioAssets,
        strategy, setStrategy,
        startDate, setStartDate,
        endDate, setEndDate,
        cash, setCash,
        benchmarkTicker, setBenchmarkTicker,
        riskFreeRate, setRiskFreeRate,
        recurringContribution, setRecurringContribution,
        contributionFrequency, setContributionFrequency,
        recurringWithdrawal, setRecurringWithdrawal,
        withdrawalFrequency, setWithdrawalFrequency,
        inflationRate, setInflationRate,
        oneTimeCashflows, setOneTimeCashflows,
        missingDataPolicy, setMissingDataPolicy,
        costAssumptions, setCostAssumptions,
        params, setParams,
        lastRunRequest, setLastRunRequest,
        lastComparisonRequest, setLastComparisonRequest,
        savedExperiment, setSavedExperiment,
        activeResultTab, setActiveResultTab,
        portfolioChartLogScale, setPortfolioChartLogScale,
        showPortfolioSeries, setShowPortfolioSeries,
        showBenchmarkSeries, setShowBenchmarkSeries,
        comparisonPortfolios, setComparisonPortfolios,
        comparisonRuns, setComparisonRuns,
        savedPortfolios, setSavedPortfolios,
        presetFilter, setPresetFilter,
    } = useBacktestStore();

    const {
        strategies,
        currentStrategy,
        isAllocationStrategy,
        needsMultiAsset,
        allocationWeightTotal,
        allocationIsBalanced,
        filteredPortfolioPresets,
    } = useBacktestingConfigurationData({
        strategy,
        portfolioAssets,
        presetFilter,
    });

    const {
        applyStrategy,
        updateCostAssumption,
        updateOneTimeCashflow,
        addOneTimeCashflow,
        removeOneTimeCashflow,
        applyBacktestRequestToForm,
    } = useBacktestingFormActions({
        strategies,
        startDate,
        endDate,
        setTicker,
        setAltTicker,
        setPortfolioAssets,
        setStrategy,
        setStartDate,
        setEndDate,
        setCash,
        setBenchmarkTicker,
        setRiskFreeRate,
        setRecurringContribution,
        setContributionFrequency,
        setRecurringWithdrawal,
        setWithdrawalFrequency,
        setInflationRate,
        setOneTimeCashflows,
        setMissingDataPolicy,
        setCostAssumptions,
        setParams,
    });

    const buildBacktestRequest = (): BacktestRequest | null => {
        const requestResult = buildBacktestRequestPayload({
            params,
            costAssumptions,
            recurringContribution,
            contributionFrequency,
            recurringWithdrawal,
            withdrawalFrequency,
            startDate,
            endDate,
            oneTimeCashflows,
            isAllocationStrategy,
            portfolioAssets,
            strategy,
            ticker,
            altTicker,
            needsMultiAsset,
            cash,
            benchmarkTicker,
            riskFreeRate,
            inflationRate,
            missingDataPolicy,
        });
        if (requestResult.error) {
            toast.error(requestResult.error);
            return null;
        }

        return requestResult.request;
    };

    const buildComparisonRequest = (
        portfolio: ComparisonPortfolio,
        baseRequest: BacktestRequest,
    ): BacktestRequest =>
        buildComparisonBacktestRequest({ portfolio, baseRequest, params });

    const {
        mutation,
        saveExperimentMutation,
        comparisonMutation,
    } = useBacktestingMutations({
        buildBacktestRequest,
        buildComparisonRequest,
        setLastRunRequest,
        setLastComparisonRequest,
        setSavedExperiment,
        setComparisonRuns,
        setActiveResultTab,
    });

    const {
        applyPortfolioPreset,
        updatePortfolioTicker,
        updatePortfolioWeight,
        addPortfolioAsset,
        removePortfolioAsset,
        equalizePortfolioWeights,
        normalizePortfolioWeights,
        clearPortfolioAssets,
        handleSavePortfolio,
        applySavedPortfolio,
        removeSavedPortfolio,
        handleAddCurrentPortfolioToComparison,
        handleAddPresetToComparison,
        handleAddSavedToComparison,
        removeComparisonPortfolio,
        handleRunComparison,
    } = useBacktestingPortfolioActions({
        strategy,
        params,
        portfolioAssets,
        isAllocationStrategy,
        allocationIsBalanced,
        comparisonPortfolios,
        setPortfolioAssets,
        setSavedPortfolios,
        setComparisonPortfolios,
        setParams,
        applyStrategy,
        onRunComparison: comparisonMutation.mutate,
    });

    const result = mutation.data;
    const {
        handleRun,
        handleShareConfig,
        handleSaveExperiment,
    } = useBacktestingRunActions({
        buildBacktestRequest,
        runBacktest: mutation.mutate,
        saveExperiment: saveExperimentMutation.mutate,
        result,
        lastRunRequest,
        applyBacktestRequestToForm,
    });
    const {
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
    } = buildBacktestResultData({
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
    });
    const {
        handleExportJson,
        handleExportCsv,
        handleExportReturnsCsv,
        handleExportTradesCsv,
        handleExportComparisonCsv,
    } = useBacktestExports({
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
    });

    return (
        <div className="space-y-8">
            <BacktestingPageHeader
                result={result}
                walkForwardRequest={walkForwardRequest}
                walkForwardHref={walkForwardHref}
                saveExperimentIsPending={saveExperimentMutation.isPending}
                canSaveExperiment={Boolean(lastRunRequest)}
                onShareConfig={handleShareConfig}
                onExportCsv={handleExportCsv}
                onExportReturnsCsv={handleExportReturnsCsv}
                onExportTradesCsv={handleExportTradesCsv}
                onExportJson={handleExportJson}
                onSaveExperiment={handleSaveExperiment}
            />

            <ToolLayout
                configPanel={
                    <BacktestingConfigurationPanel
                        strategy={strategy}
                        strategies={strategies}
                        currentStrategy={currentStrategy}
                        isAllocationStrategy={isAllocationStrategy}
                        ticker={ticker}
                        altTicker={altTicker}
                        needsMultiAsset={Boolean(needsMultiAsset)}
                        portfolioAssets={portfolioAssets}
                        allocationIsBalanced={allocationIsBalanced}
                        allocationWeightTotal={allocationWeightTotal}
                        presetFilter={presetFilter}
                        filteredPortfolioPresets={filteredPortfolioPresets}
                        savedPortfolios={savedPortfolios}
                        comparisonPortfolios={comparisonPortfolios}
                        comparisonIsPending={comparisonMutation.isPending}
                        startDate={startDate}
                        endDate={endDate}
                        cash={cash}
                        benchmarkTicker={benchmarkTicker}
                        riskFreeRate={riskFreeRate}
                        missingDataPolicy={missingDataPolicy}
                        costAssumptions={costAssumptions}
                        recurringContribution={recurringContribution}
                        contributionFrequency={contributionFrequency}
                        recurringWithdrawal={recurringWithdrawal}
                        withdrawalFrequency={withdrawalFrequency}
                        inflationRate={inflationRate}
                        oneTimeCashflows={oneTimeCashflows}
                        params={params}
                        runIsPending={mutation.isPending}
                        onStrategyChange={applyStrategy}
                        onTickerChange={setTicker}
                        onAltTickerChange={setAltTicker}
                        onPresetFilterChange={setPresetFilter}
                        onApplyPreset={applyPortfolioPreset}
                        onAddPresetToComparison={handleAddPresetToComparison}
                        onEqualizeWeights={equalizePortfolioWeights}
                        onNormalizeWeights={normalizePortfolioWeights}
                        onClearAssets={clearPortfolioAssets}
                        onSavePortfolio={handleSavePortfolio}
                        onAddCurrentToComparison={
                            handleAddCurrentPortfolioToComparison
                        }
                        onAddAsset={addPortfolioAsset}
                        onUpdateTicker={updatePortfolioTicker}
                        onUpdateWeight={updatePortfolioWeight}
                        onRemoveAsset={removePortfolioAsset}
                        onApplySavedPortfolio={applySavedPortfolio}
                        onAddSavedToComparison={handleAddSavedToComparison}
                        onRemoveSavedPortfolio={removeSavedPortfolio}
                        onRunComparison={handleRunComparison}
                        onRemoveComparisonPortfolio={
                            removeComparisonPortfolio
                        }
                        onStartDateChange={setStartDate}
                        onEndDateChange={setEndDate}
                        onCashChange={setCash}
                        onBenchmarkTickerChange={setBenchmarkTicker}
                        onRiskFreeRateChange={setRiskFreeRate}
                        onMissingDataPolicyChange={setMissingDataPolicy}
                        onCostAssumptionChange={updateCostAssumption}
                        onRecurringContributionChange={
                            setRecurringContribution
                        }
                        onContributionFrequencyChange={setContributionFrequency}
                        onRecurringWithdrawalChange={setRecurringWithdrawal}
                        onWithdrawalFrequencyChange={setWithdrawalFrequency}
                        onInflationRateChange={setInflationRate}
                        onOneTimeCashflowChange={updateOneTimeCashflow}
                        onAddOneTimeCashflow={addOneTimeCashflow}
                        onRemoveOneTimeCashflow={removeOneTimeCashflow}
                        onParamsChange={setParams}
                        onRun={handleRun}
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

                {hasResultWorkspace && (
                    <ResultWorkspaceSection
                        stats={stats}
                        title={
                            resultSummaryRequest?.tickers.join(" / ") ??
                            "Portfolio comparison"
                        }
                        strategy={resultSummaryRequest?.strategy}
                        detail={
                            result
                                ? `${lastRunRequest?.start_date} to ${lastRunRequest?.end_date} / ${formatCurrencyPrecise(getEndingValue(result))} ending value`
                                : `${comparisonRuns.length} portfolio${comparisonRuns.length === 1 ? "" : "s"} compared with shared dates, cashflows, costs, and data policy`
                        }
                        hasStaleResults={hasStaleResults}
                        activeTab={activeResultTab}
                        savedExperiment={savedExperiment}
                        costSummary={costSummary}
                        appliedCostAssumptions={appliedCostAssumptions}
                        costBySymbolRows={costBySymbolRows}
                        missingDataSummary={missingDataSummary}
                        walkForwardRequest={walkForwardRequest}
                        walkForwardHref={walkForwardHref}
                        withdrawalDurability={withdrawalDurability}
                        inflationAdjustedSeries={inflationAdjustedSeries}
                        cashflowEvents={cashflowEvents}
                        benchmarkStats={benchmarkStats}
                        comparisonChartSeries={comparisonChartSeries}
                        visiblePortfolioChartSeries={
                            visiblePortfolioChartSeries
                        }
                        valueHistory={result?.value_history ?? []}
                        portfolioChartLogScale={portfolioChartLogScale}
                        showPortfolioSeries={showPortfolioSeries}
                        showBenchmarkSeries={showBenchmarkSeries}
                        overviewExportBaseName={overviewExportBaseName}
                        rollingMetrics={rollingMetrics}
                        rollingChartData={rollingChartData}
                        regimeSummary={regimeSummary}
                        regimePeriods={regimePeriods}
                        regimeReferenceTicker={regimeReferenceTicker}
                        allocationChartData={allocationChartData}
                        allocationSeriesKeys={allocationSeriesKeys}
                        allocationDriftSummary={allocationDriftSummary}
                        rebalanceEvents={rebalanceEvents}
                        comparisonRuns={comparisonRuns}
                        comparisonRows={comparisonRows}
                        comparisonResultSeries={comparisonResultSeries}
                        comparisonDrawdownSeries={comparisonDrawdownSeries}
                        comparisonExportBaseName={comparisonExportBaseName}
                        monthlyReturns={monthlyReturns}
                        annualReturns={annualReturns}
                        trades={result?.trades ?? []}
                        onTabChange={setActiveResultTab}
                        onTogglePortfolioSeries={() =>
                            setShowPortfolioSeries((value) => !value)
                        }
                        onToggleBenchmarkSeries={() =>
                            setShowBenchmarkSeries((value) => !value)
                        }
                        onToggleLogScale={() =>
                            setPortfolioChartLogScale((value) => !value)
                        }
                        onExportComparisonCsv={handleExportComparisonCsv}
                    />
                )}

                {mutation.isError && (
                    <InlineError
                        message={mutation.error?.message ?? "Backtest failed"}
                        onRetry={handleRun}
                    />
                )}

                {!mutation.isPending &&
                    !mutation.isError &&
                    !result &&
                    comparisonRuns.length === 0 && (
                    <EmptyState
                        icon={Activity}
                        message="Configure parameters and click Run Backtest to see results."
                        presets={[
                            {
                                label: "SPY Buy & Hold",
                                onClick: () =>
                                    applyPortfolioPreset(PORTFOLIO_PRESETS[0]),
                            },
                            {
                                label: "60/40 Rebalance",
                                onClick: () =>
                                    applyPortfolioPreset(PORTFOLIO_PRESETS[1]),
                            },
                            {
                                label: "SPY SMA Crossover",
                                onClick: () => {
                                    setTicker("SPY");
                                    applyStrategy("SMACrossover");
                                },
                            },
                        ]}
                    />
                )}
            </ToolLayout>
        </div>
    );
}
