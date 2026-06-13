"use client";

import { useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/common/page-header";
import { ToolLayout } from "@/components/common/tool-layout";
import { EmptyState } from "@/components/common/empty-state";
import { InlineError } from "@/components/common/inline-error";
import {
    ChartSkeleton,
    CardSkeleton,
} from "@/components/common/loading-skeleton";
import {
    Activity,
    Download,
    Share2,
} from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";
import { formatCurrencyPrecise } from "@/lib/format";
import { useBacktestStore } from "@/stores/backtest-store";
import type {
    StrategyInfo,
    BacktestCostAssumptions,
    BacktestRequest,
    BacktestResponse,
    OneTimeCashflowEvent,
    SaveExperimentRequest,
    SaveExperimentResponse,
} from "@/types/api";
import type {
    SavedPortfolio,
    ComparisonPortfolio,
    ComparisonRun,
} from "@/stores/backtest-store";
import { DEFAULT_COST_ASSUMPTIONS } from "@/stores/backtest-store";
import {
    MAX_COMPARISON_PORTFOLIOS,
    PORTFOLIO_PRESETS,
    STRATEGY_FALLBACK_PARAMS,
    type PortfolioPreset,
} from "@/app/backtesting/backtesting-options";
import {
    buildPortfolioLabel,
    buildPortfolioStrategyParams,
    cloneAssets,
    decodeSharedConfig,
    encodeSharedConfig,
    getEndingValue,
} from "@/lib/backtest-utils";
import { BacktestingConfigurationPanel } from "@/app/backtesting/components/backtesting-configuration-panel";
import { ResultWorkspaceSection } from "@/app/backtesting/components/result-workspace-section";
import { useBacktestExports } from "@/app/backtesting/use-backtest-exports";
import { buildBacktestResultData } from "@/app/backtesting/backtesting-result-data";
import {
    buildBacktestRequestPayload,
    buildComparisonBacktestRequest,
} from "@/app/backtesting/backtesting-request-builder";

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

    const { data: strategies } = useQuery({
        queryKey: ["strategies"],
        queryFn: () => apiGet<StrategyInfo[]>("/api/backtesting/strategies"),
    });

    const currentStrategy = strategies?.find((s) => s.name === strategy);
    const isAllocationStrategy =
        strategy === "NoRebalance" || strategy === "Rebalance";
    const needsMultiAsset =
        !isAllocationStrategy &&
        currentStrategy &&
        currentStrategy.min_assets > 1;
    const allocationWeightTotal = portfolioAssets.reduce(
        (total, asset) => total + asset.weight,
        0,
    );
    const allocationIsBalanced =
        Math.abs(allocationWeightTotal - 100) <= 0.1 &&
        portfolioAssets.every(
            (asset) => asset.weight > 0 && asset.ticker.trim().length > 0,
        );
    const filteredPortfolioPresets = PORTFOLIO_PRESETS.filter((preset) => {
        const query = presetFilter.trim().toLowerCase();
        if (!query) {
            return true;
        }
        return [
            preset.label,
            preset.description,
            preset.category,
            preset.assumption,
            ...preset.assets.map((asset) => asset.ticker),
        ]
            .join(" ")
            .toLowerCase()
            .includes(query);
    });

    const mutation = useMutation({
        mutationFn: (req: BacktestRequest) =>
            apiPost<BacktestResponse>("/api/backtesting/run", req, 120000),
        onSuccess: (_data, variables) => {
            setLastRunRequest(variables);
            setSavedExperiment(null);
            toast.success("Backtest complete");
        },
        onError: (e) => toast.error(`Backtest failed: ${e.message}`),
    });

    const saveExperimentMutation = useMutation({
        mutationFn: (req: SaveExperimentRequest) =>
            apiPost<SaveExperimentResponse>("/api/experiments/save", req),
        onSuccess: (data) => {
            setSavedExperiment(data);
            toast.success("Experiment saved");
        },
        onError: (e) => toast.error(`Save failed: ${e.message}`),
    });

    const comparisonMutation = useMutation({
        mutationFn: async (portfolios: ComparisonPortfolio[]) => {
            const baseRequest = buildBacktestRequest();
            if (!baseRequest) {
                throw new Error("Fix the current run configuration before comparing portfolios.");
            }

            const runs = await Promise.all(
                portfolios.map(async (portfolio): Promise<ComparisonRun> => {
                    const request = buildComparisonRequest(portfolio, baseRequest);
                    try {
                        const comparisonResult = await apiPost<BacktestResponse>(
                            "/api/backtesting/run",
                            request,
                            120000,
                        );
                        return {
                            portfolio,
                            request,
                            result: comparisonResult,
                        };
                    } catch (error) {
                        return {
                            portfolio,
                            request,
                            result: null,
                            error:
                                error instanceof Error
                                    ? error.message
                                    : "Comparison run failed",
                        };
                    }
                }),
            );
            return runs;
        },
        onSuccess: (runs) => {
            setComparisonRuns(runs);
            const firstRequest = runs.find((run) => run.request)?.request;
            if (firstRequest) {
                setLastComparisonRequest(firstRequest);
            }
            const failed = runs.filter((run) => run.error).length;
            if (failed > 0) {
                toast.error(`${failed} comparison run${failed === 1 ? "" : "s"} failed`);
            } else {
                toast.success("Comparison complete");
            }
            setActiveResultTab("comparison");
        },
        onError: (e) => toast.error(`Comparison failed: ${e.message}`),
    });

    const applyStrategy = (name: string) => {
        setStrategy(name);
        const selectedStrategy = strategies?.find(
            (candidate) => candidate.name === name,
        );
        if (selectedStrategy) {
            const defaults: Record<string, number> = {};
            selectedStrategy.params.forEach((param) => {
                defaults[param.name] = param.default as number;
            });
            setParams(defaults);
            return;
        }
        setParams(STRATEGY_FALLBACK_PARAMS[name] ?? {});
    };

    const applyPortfolioPreset = (preset: PortfolioPreset) => {
        applyStrategy(preset.strategy);
        if (preset.strategy === "Rebalance" && preset.rebalInterval) {
            const rebalInterval = preset.rebalInterval;
            setParams((current) => ({
                ...current,
                rebal_interval: rebalInterval,
            }));
        }
        setPortfolioAssets(preset.assets.map((asset) => ({ ...asset })));
    };

    const updatePortfolioTicker = (index: number, value: string) => {
        setPortfolioAssets((current) =>
            current.map((asset, assetIndex) =>
                assetIndex === index ? { ...asset, ticker: value } : asset,
            ),
        );
    };

    const updatePortfolioWeight = (index: number, value: string) => {
        const nextWeight = Number(value);
        setPortfolioAssets((current) =>
            current.map((asset, assetIndex) =>
                assetIndex === index
                    ? {
                          ...asset,
                          weight: Number.isFinite(nextWeight) ? nextWeight : 0,
                      }
                    : asset,
            ),
        );
    };

    const addPortfolioAsset = () => {
        setPortfolioAssets((current) => [
            ...current,
            { ticker: "", weight: 0 },
        ]);
    };

    const updateCostAssumption = <K extends keyof BacktestCostAssumptions>(
        key: K,
        value: BacktestCostAssumptions[K],
    ) => {
        setCostAssumptions((current) => ({
            ...current,
            [key]: value,
        }));
    };

    const updateOneTimeCashflow = (
        index: number,
        patch: Partial<OneTimeCashflowEvent>,
    ) => {
        setOneTimeCashflows((current) =>
            current.map((event, eventIndex) =>
                eventIndex === index ? { ...event, ...patch } : event,
            ),
        );
    };

    const addOneTimeCashflow = () => {
        setOneTimeCashflows((current) => [
            ...current,
            { date: startDate, amount: 0, label: "" },
        ]);
    };

    const removeOneTimeCashflow = (index: number) => {
        setOneTimeCashflows((current) =>
            current.filter((_, eventIndex) => eventIndex !== index),
        );
    };

    const removePortfolioAsset = (index: number) => {
        setPortfolioAssets((current) => {
            if (current.length === 1) {
                return current;
            }
            return current.filter((_, assetIndex) => assetIndex !== index);
        });
    };

    const equalizePortfolioWeights = () => {
        setPortfolioAssets((current) => {
            if (current.length === 0) {
                return current;
            }

            const evenWeight = Number((100 / current.length).toFixed(2));
            const finalWeight = Number(
                (100 - evenWeight * (current.length - 1)).toFixed(2),
            );
            return current.map((asset, assetIndex) => ({
                ...asset,
                weight:
                    assetIndex === current.length - 1
                        ? finalWeight
                        : evenWeight,
            }));
        });
    };

    const normalizePortfolioWeights = () => {
        setPortfolioAssets((current) => {
            const totalWeight = current.reduce(
                (total, asset) => total + Number(asset.weight),
                0,
            );
            if (totalWeight <= 0) {
                toast.error("Enter positive weights before normalizing.");
                return current;
            }

            const normalized = current.map((asset) => ({
                ...asset,
                weight: Number(((asset.weight / totalWeight) * 100).toFixed(2)),
            }));
            const roundedTotal = normalized.reduce(
                (total, asset) => total + asset.weight,
                0,
            );
            const delta = Number((100 - roundedTotal).toFixed(2));
            return normalized.map((asset, index) =>
                index === normalized.length - 1
                    ? { ...asset, weight: Number((asset.weight + delta).toFixed(2)) }
                    : asset,
            );
        });
    };

    const clearPortfolioAssets = () => {
        setPortfolioAssets([{ ticker: "", weight: 0 }]);
    };

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

    const applyBacktestRequestToForm = (request: BacktestRequest) => {
        setStrategy(request.strategy);
        setStartDate(request.start_date ?? startDate);
        setEndDate(request.end_date ?? endDate);
        setCash(request.initial_cash);
        setBenchmarkTicker(request.benchmark_ticker ?? "");
        setRiskFreeRate(request.risk_free_rate ?? 0.04);
        setMissingDataPolicy(request.missing_data_policy ?? "forward_fill");
        setCostAssumptions(request.cost_assumptions ?? DEFAULT_COST_ASSUMPTIONS);
        const contributionRule = request.recurring_cashflows?.find(
            (rule) => rule.amount > 0,
        );
        const withdrawalRule = request.recurring_cashflows?.find(
            (rule) => rule.amount < 0,
        );
        setRecurringContribution(
            contributionRule?.amount ?? 0,
        );
        if (contributionRule?.frequency) {
            setContributionFrequency(contributionRule.frequency);
        }
        setRecurringWithdrawal(
            Math.abs(withdrawalRule?.amount ?? 0),
        );
        if (withdrawalRule?.frequency) {
            setWithdrawalFrequency(withdrawalRule.frequency);
        }
        setOneTimeCashflows(request.one_time_cashflows ?? []);
        setInflationRate(request.inflation_rate ?? 0.03);

        if (request.strategy === "NoRebalance" || request.strategy === "Rebalance") {
            const proportions =
                request.strategy === "NoRebalance"
                    ? request.strategy_params.equity_proportions
                    : request.strategy_params.rebal_proportions;
            const weights = Array.isArray(proportions)
                ? proportions.map((value) => Number(value) * 100)
                : request.tickers.map(() => Number((100 / request.tickers.length).toFixed(2)));
            setPortfolioAssets(
                request.tickers.map((requestTicker, index) => ({
                    ticker: requestTicker,
                    weight: weights[index] ?? 0,
                })),
            );
        } else {
            setTicker(request.tickers[0] ?? "SPY");
            setAltTicker(request.tickers[1] ?? "TLT");
        }

        setParams(
            Object.fromEntries(
                Object.entries(request.strategy_params ?? {}).filter(
                    ([, value]) => typeof value === "number",
                ),
            ) as Record<string, number>,
        );
    };

    const handleRun = () => {
        const request = buildBacktestRequest();
        if (!request) {
            return;
        }
        mutation.mutate(request);
    };

    const handleShareConfig = async () => {
        const request = buildBacktestRequest();
        if (!request) {
            return;
        }

        const url = new URL(window.location.href);
        url.searchParams.set("config", encodeSharedConfig(request));
        window.history.replaceState(null, "", url.toString());

        try {
            await navigator.clipboard.writeText(url.toString());
            toast.success("Share link copied");
        } catch {
            toast.success("Share link added to the address bar");
        }
    };

    const handleSavePortfolio = () => {
        if (!isAllocationStrategy || !allocationIsBalanced) {
            toast.error("Save a balanced allocation portfolio first.");
            return;
        }

        const saved: SavedPortfolio = {
            id: `portfolio-${Date.now()}`,
            label: buildPortfolioLabel(portfolioAssets),
            strategy: strategy as "NoRebalance" | "Rebalance",
            assets: cloneAssets(portfolioAssets),
            strategyParams: buildPortfolioStrategyParams(
                strategy as "NoRebalance" | "Rebalance",
                params,
                STRATEGY_FALLBACK_PARAMS.Rebalance.rebal_interval,
            ),
            createdAt: new Date().toISOString(),
        };
        setSavedPortfolios((current) => [saved, ...current].slice(0, 12));
        toast.success("Portfolio saved");
    };

    const applySavedPortfolio = (portfolio: SavedPortfolio) => {
        applyStrategy(portfolio.strategy);
        setPortfolioAssets(cloneAssets(portfolio.assets));
        if (portfolio.strategyParams) {
            setParams((current) => ({
                ...current,
                ...portfolio.strategyParams,
            }));
        }
    };

    const removeSavedPortfolio = (id: string) => {
        setSavedPortfolios((current) => current.filter((portfolio) => portfolio.id !== id));
    };

    const addComparisonPortfolio = (
        portfolio: Omit<ComparisonPortfolio, "id">,
    ) => {
        setComparisonPortfolios((current) => {
            if (current.length >= MAX_COMPARISON_PORTFOLIOS) {
                toast.error(`Compare up to ${MAX_COMPARISON_PORTFOLIOS} portfolios at a time.`);
                return current;
            }
            return [
                ...current,
                {
                    ...portfolio,
                    id: `comparison-${Date.now()}-${current.length}`,
                    assets: cloneAssets(portfolio.assets),
                    strategyParams: portfolio.strategyParams
                        ? { ...portfolio.strategyParams }
                        : undefined,
                },
            ];
        });
    };

    const handleAddCurrentPortfolioToComparison = () => {
        if (!isAllocationStrategy || !allocationIsBalanced) {
            toast.error("Add a balanced allocation portfolio before comparing.");
            return;
        }

        addComparisonPortfolio({
            label: buildPortfolioLabel(portfolioAssets),
            strategy: strategy as "NoRebalance" | "Rebalance",
            assets: portfolioAssets,
            strategyParams: buildPortfolioStrategyParams(
                strategy as "NoRebalance" | "Rebalance",
                params,
                STRATEGY_FALLBACK_PARAMS.Rebalance.rebal_interval,
            ),
            source: "current",
        });
    };

    const handleAddPresetToComparison = (preset: PortfolioPreset) => {
        addComparisonPortfolio({
            label: preset.label,
            strategy: preset.strategy,
            assets: preset.assets,
            strategyParams: buildPortfolioStrategyParams(
                preset.strategy,
                {
                    rebal_interval:
                        preset.rebalInterval ??
                        STRATEGY_FALLBACK_PARAMS.Rebalance.rebal_interval,
                },
                STRATEGY_FALLBACK_PARAMS.Rebalance.rebal_interval,
            ),
            source: "preset",
        });
    };

    const handleAddSavedToComparison = (portfolio: SavedPortfolio) => {
        addComparisonPortfolio({
            label: portfolio.label,
            strategy: portfolio.strategy,
            assets: portfolio.assets,
            strategyParams: portfolio.strategyParams,
            source: "saved",
        });
    };

    const removeComparisonPortfolio = (id: string) => {
        setComparisonPortfolios((current) => current.filter((portfolio) => portfolio.id !== id));
    };

    const handleRunComparison = () => {
        if (comparisonPortfolios.length < 2) {
            toast.error("Add at least two portfolios to compare.");
            return;
        }
        comparisonMutation.mutate(comparisonPortfolios);
    };


    // Load shared backtest configuration from URL ?config= param (once on mount).
    // Note: savedPortfolios is now persisted automatically by the zustand store.
    useEffect(() => {
        const encodedConfig = new URLSearchParams(window.location.search).get("config");
        if (encodedConfig) {
            const sharedRequest = decodeSharedConfig(encodedConfig);
            if (sharedRequest) {
                applyBacktestRequestToForm(sharedRequest);
                toast.success("Shared backtest configuration loaded");
            }
        }
        // Shared links should hydrate only once.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);


    const handleSaveExperiment = () => {
        if (!result?.stats || !lastRunRequest) {
            toast.error("Run a backtest before saving an experiment.");
            return;
        }

        saveExperimentMutation.mutate({
            ...lastRunRequest,
            stats: result.stats,
        });
    };

    const result = mutation.data;
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
            <PageHeader
                title="Strategy Backtester"
                description="Run allocation backtests or trading strategies on historical data"
                actions={
                    <>
                        <Button
                            type="button"
                            variant="outline"
                            onClick={handleShareConfig}
                        >
                            <Share2 className="h-3.5 w-3.5" />
                            Share Setup
                        </Button>
                        {result ? (
                        <>
                            {walkForwardRequest && (
                                <Button asChild type="button" variant="outline">
                                    <Link href={walkForwardHref}>
                                        Continue to Walk-Forward
                                    </Link>
                                </Button>
                            )}
                            <Button
                                type="button"
                                variant="outline"
                                onClick={handleExportCsv}
                            >
                                <Download className="h-3.5 w-3.5" />
                                Export CSV
                            </Button>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={handleExportReturnsCsv}
                            >
                                <Download className="h-3.5 w-3.5" />
                                Returns
                            </Button>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={handleExportTradesCsv}
                            >
                                <Download className="h-3.5 w-3.5" />
                                Trades
                            </Button>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={handleExportJson}
                            >
                                <Download className="h-3.5 w-3.5" />
                                Export JSON
                            </Button>
                            <Button
                                onClick={handleSaveExperiment}
                                disabled={
                                    saveExperimentMutation.isPending ||
                                    !lastRunRequest
                                }
                                className="bg-gradient-to-r from-emerald-600 to-emerald-500 font-medium text-white shadow-lg shadow-emerald-500/20"
                            >
                                {saveExperimentMutation.isPending
                                    ? "Saving..."
                                    : "Save Experiment"}
                            </Button>
                        </>
                        ) : null}
                    </>
                }
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
