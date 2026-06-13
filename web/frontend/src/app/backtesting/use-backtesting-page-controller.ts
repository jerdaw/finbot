"use client";

import { useBacktestStore } from "@/stores/backtest-store";
import { useBacktestExports } from "@/app/backtesting/use-backtest-exports";
import { buildBacktestResultData } from "@/app/backtesting/backtesting-result-data";
import { useBacktestingConfigurationData } from "@/app/backtesting/use-backtesting-configuration-data";
import { useBacktestingFormActions } from "@/app/backtesting/use-backtesting-form-actions";
import { useBacktestingMutations } from "@/app/backtesting/use-backtesting-mutations";
import { useBacktestingPortfolioActions } from "@/app/backtesting/use-backtesting-portfolio-actions";
import { useBacktestingRequestBuilders } from "@/app/backtesting/use-backtesting-request-builders";
import { useBacktestingRunActions } from "@/app/backtesting/use-backtesting-run-actions";

export function useBacktestingPageController() {
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

    const configuration = useBacktestingConfigurationData({
        strategy,
        portfolioAssets,
        presetFilter,
    });

    const {
        strategies,
        isAllocationStrategy,
        needsMultiAsset,
        allocationIsBalanced,
    } = configuration;

    const formActions = useBacktestingFormActions({
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

    const requestBuilders = useBacktestingRequestBuilders({
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

    const {
        buildBacktestRequest,
        buildComparisonRequest,
    } = requestBuilders;

    const mutations = useBacktestingMutations({
        buildBacktestRequest,
        buildComparisonRequest,
        setLastRunRequest,
        setLastComparisonRequest,
        setSavedExperiment,
        setComparisonRuns,
        setActiveResultTab,
    });

    const {
        mutation,
        saveExperimentMutation,
        comparisonMutation,
    } = mutations;

    const portfolioActions = useBacktestingPortfolioActions({
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
        applyStrategy: formActions.applyStrategy,
        onRunComparison: comparisonMutation.mutate,
    });

    const result = mutation.data;
    const runActions = useBacktestingRunActions({
        buildBacktestRequest,
        runBacktest: mutation.mutate,
        saveExperiment: saveExperimentMutation.mutate,
        result,
        lastRunRequest,
        applyBacktestRequestToForm: formActions.applyBacktestRequestToForm,
    });

    const resultData = buildBacktestResultData({
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

    const exportActions = useBacktestExports({
        result,
        lastRunRequest,
        lastComparisonRequest,
        savedExperiment,
        benchmarkValueHistory: resultData.benchmarkValueHistory,
        realValueHistory: resultData.realValueHistory,
        rollingMetrics: resultData.rollingMetrics,
        monthlyReturns: resultData.monthlyReturns,
        annualReturns: resultData.annualReturns,
        comparisonRuns,
    });

    return {
        form: {
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
            inflationRate,
            oneTimeCashflows,
            missingDataPolicy,
            costAssumptions,
            params,
            lastRunRequest,
            savedExperiment,
            activeResultTab,
            portfolioChartLogScale,
            showPortfolioSeries,
            showBenchmarkSeries,
            comparisonPortfolios,
            comparisonRuns,
            savedPortfolios,
            presetFilter,
        },
        configuration,
        mutations,
        result,
        resultData,
        actions: {
            setTicker,
            setAltTicker,
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
            setMissingDataPolicy,
            setParams,
            setPresetFilter,
            setActiveResultTab,
            setPortfolioChartLogScale,
            setShowPortfolioSeries,
            setShowBenchmarkSeries,
            ...formActions,
            ...portfolioActions,
            ...runActions,
            ...exportActions,
        },
    };
}

export type BacktestingPageController = ReturnType<typeof useBacktestingPageController>;
