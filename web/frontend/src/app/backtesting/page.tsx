"use client";

import { useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { PageHeader } from "@/components/common/page-header";
import { ConfigPanel, ConfigSection } from "@/components/common/config-panel";
import { ChartCard } from "@/components/common/chart-card";
import { ToolLayout } from "@/components/common/tool-layout";
import { EmptyState } from "@/components/common/empty-state";
import { InlineError } from "@/components/common/inline-error";
import {
    ChartSkeleton,
    CardSkeleton,
} from "@/components/common/loading-skeleton";
import {
    Activity,
    BarChart3,
    Download,
    Plus,
    Save,
    Share2,
    Trash2,
    X,
} from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";
import {
    formatPercent,
    formatNumber,
    formatCurrencyPrecise,
} from "@/lib/format";
import { cn } from "@/lib/utils";
import { useBacktestStore } from "@/stores/backtest-store";
import type {
    AppliedBacktestCostAssumptions,
    StrategyInfo,
    BacktestCostAssumptions,
    BacktestCostSummary,
    BacktestRequest,
    BacktestBenchmarkStats,
    BacktestMissingDataSummary,
    CashflowEventRecord,
    BacktestResponse,
    MissingDataPolicy,
    OneTimeCashflowEvent,
    RebalanceEventRecord,
    RecurringCashflowRule,
    RollingMetricsResponse,
    SaveExperimentRequest,
    SaveExperimentResponse,
    WithdrawalDurabilitySummary,
    WalkForwardHandoff,
} from "@/types/api";
import type {
    SavedPortfolio,
    ComparisonPortfolio,
    ComparisonRun,
} from "@/stores/backtest-store";
import { DEFAULT_COST_ASSUMPTIONS } from "@/stores/backtest-store";
import {
    CASHFLOW_FREQUENCY_OPTIONS,
    COMMISSION_MODE_OPTIONS,
    MAX_COMPARISON_PORTFOLIOS,
    MISSING_DATA_POLICY_OPTIONS,
    PORTFOLIO_PRESETS,
    STRATEGY_FALLBACK_PARAMS,
    type PortfolioPreset,
} from "@/app/backtesting/backtesting-options";
import {
    buildDrawdownValues,
    buildPortfolioLabel,
    buildPortfolioStrategyParams,
    buildWalkForwardHref,
    cloneAssets,
    decodeSharedConfig,
    encodeSharedConfig,
    formatBenchmarkValue,
    getEndingValue,
    getMetricTrend,
    getNumericStat,
    normalizeRequestForSignature,
} from "@/lib/backtest-utils";
import {
    buildCsv,
    buildExportBaseName,
    downloadFile,
} from "@/lib/export-utils";
import {
    ComparisonResultsTab,
    type ComparisonMetricsRow,
} from "@/app/backtesting/components/comparison-results-tab";
import { ReturnsTab } from "@/app/backtesting/components/returns-tab";
import { AuditTab } from "@/app/backtesting/components/audit-tab";
import { DiagnosticsTab } from "@/app/backtesting/components/diagnostics-tab";
import { CashflowsTab } from "@/app/backtesting/components/cashflows-tab";
import { OverviewTab } from "@/app/backtesting/components/overview-tab";
import { ResultWorkspaceSummary } from "@/app/backtesting/components/result-workspace-summary";

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
        const strategyParams: Record<string, unknown> = { ...params };
        let tickers: string[] = [];
        const recurringCashflows: RecurringCashflowRule[] = [];
        const normalizedCostAssumptions: BacktestCostAssumptions = {
            ...costAssumptions,
            commission_per_share: Number(costAssumptions.commission_per_share),
            commission_bps: Number(costAssumptions.commission_bps),
            commission_minimum: Number(costAssumptions.commission_minimum),
            spread_bps: Number(costAssumptions.spread_bps),
            slippage_bps: Number(costAssumptions.slippage_bps),
        };

        if (
            Object.values(normalizedCostAssumptions)
                .filter((value) => typeof value === "number")
                .some(
                    (value) =>
                        !Number.isFinite(value as number) ||
                        (value as number) < 0,
                )
        ) {
            toast.error(
                "Cost assumptions must be finite, non-negative numbers.",
            );
            return null;
        }
        if (
            normalizedCostAssumptions.commission_mode === "per_share" &&
            normalizedCostAssumptions.commission_per_share <= 0
        ) {
            toast.error("Per-share commission must be greater than 0.");
            return null;
        }
        if (
            normalizedCostAssumptions.commission_mode === "percentage" &&
            normalizedCostAssumptions.commission_bps <= 0
        ) {
            toast.error("Percentage commission must be greater than 0 bps.");
            return null;
        }

        if (recurringContribution > 0) {
            recurringCashflows.push({
                amount: recurringContribution,
                frequency: contributionFrequency,
                start_date: startDate,
                end_date: endDate,
                label: `Recurring contribution (${contributionFrequency})`,
            });
        }
        if (recurringWithdrawal > 0) {
            recurringCashflows.push({
                amount: -recurringWithdrawal,
                frequency: withdrawalFrequency,
                start_date: startDate,
                end_date: endDate,
                label: `Recurring withdrawal (${withdrawalFrequency})`,
            });
        }

        const normalizedOneTimeCashflows = oneTimeCashflows
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

        for (const event of normalizedOneTimeCashflows) {
            if (!event.date) {
                toast.error("Each one-time cashflow needs an applied date.");
                return null;
            }
            if (!Number.isFinite(event.amount) || event.amount === 0) {
                toast.error("Each one-time cashflow needs a non-zero amount.");
                return null;
            }
        }

        if (isAllocationStrategy) {
            const cleanedAssets = portfolioAssets
                .map((asset) => ({
                    ticker: asset.ticker.trim().toUpperCase(),
                    weight: asset.weight,
                }))
                .filter((asset) => asset.ticker.length > 0);

            if (cleanedAssets.length === 0) {
                toast.error(
                    "Add at least one asset before running the allocation backtest.",
                );
                return null;
            }
            if (cleanedAssets.some((asset) => asset.weight <= 0)) {
                toast.error("Allocation weights must be greater than 0%.");
                return null;
            }
            if (
                new Set(cleanedAssets.map((asset) => asset.ticker)).size !==
                cleanedAssets.length
            ) {
                toast.error("Each asset ticker must be unique.");
                return null;
            }

            const totalWeight = cleanedAssets.reduce(
                (total, asset) => total + asset.weight,
                0,
            );
            if (Math.abs(totalWeight - 100) > 0.1) {
                toast.error("Allocation weights must add up to 100%.");
                return null;
            }

            tickers = cleanedAssets.map((asset) => asset.ticker);
            const normalizedWeights = cleanedAssets.map(
                (asset) => asset.weight / 100,
            );
            if (strategy === "NoRebalance") {
                strategyParams.equity_proportions = normalizedWeights;
            }
            if (strategy === "Rebalance") {
                strategyParams.rebal_proportions = normalizedWeights;
            }
        } else {
            const primaryTicker = ticker.trim().toUpperCase();
            if (!primaryTicker) {
                toast.error(
                    "Enter an asset ticker before running the backtest.",
                );
                return null;
            }

            tickers = [primaryTicker];
            if (needsMultiAsset) {
                const secondaryTicker = altTicker.trim().toUpperCase();
                if (!secondaryTicker) {
                    toast.error(
                        "Enter a second asset for the selected strategy.",
                    );
                    return null;
                }
                if (secondaryTicker === primaryTicker) {
                    toast.error(
                        "Use two distinct assets for the selected strategy.",
                    );
                    return null;
                }
                tickers = [primaryTicker, secondaryTicker];
            }
        }

        return {
            tickers,
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
                recurringCashflows.length > 0 ? recurringCashflows : undefined,
            one_time_cashflows:
                normalizedOneTimeCashflows.length > 0
                    ? normalizedOneTimeCashflows
                    : undefined,
            inflation_rate: inflationRate,
            missing_data_policy: missingDataPolicy,
            cost_assumptions: normalizedCostAssumptions,
        };
    };

    const buildComparisonRequest = (
        portfolio: ComparisonPortfolio,
        baseRequest: BacktestRequest,
    ): BacktestRequest => {
        const cleanedAssets = cloneAssets(portfolio.assets).filter(
            (asset) => asset.ticker.length > 0,
        );
        const weights = cleanedAssets.map((asset) => asset.weight / 100);
        const strategyParams: Record<string, unknown> = {};

        if (portfolio.strategy === "NoRebalance") {
            strategyParams.equity_proportions = weights;
        } else {
            strategyParams.rebal_proportions = weights;
            strategyParams.rebal_interval =
                typeof portfolio.strategyParams?.rebal_interval === "number"
                    ? portfolio.strategyParams.rebal_interval
                    : typeof params.rebal_interval === "number"
                    ? params.rebal_interval
                    : STRATEGY_FALLBACK_PARAMS.Rebalance.rebal_interval;
        }

        return {
            ...baseRequest,
            tickers: cleanedAssets.map((asset) => asset.ticker),
            strategy: portfolio.strategy,
            strategy_params: strategyParams,
        };
    };

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

    const result = mutation.data;
    const stats = result?.stats;
    const benchmarkStats: BacktestBenchmarkStats | null | undefined =
        result?.benchmark_stats;
    const benchmarkValueHistory = result?.benchmark_value_history ?? [];
    const cashflowEvents: CashflowEventRecord[] = result?.cashflow_events ?? [];
    const realValueHistory = result?.real_value_history ?? [];
    const withdrawalDurability: WithdrawalDurabilitySummary | null | undefined =
        result?.withdrawal_durability;
    const allocationHistory = result?.allocation_history ?? [];
    const rebalanceEvents: RebalanceEventRecord[] =
        result?.rebalance_events ?? [];
    const rollingMetrics: RollingMetricsResponse | null | undefined =
        result?.rolling_metrics;
    const appliedCostAssumptions: AppliedBacktestCostAssumptions | undefined =
        result?.applied_cost_assumptions;
    const costSummary: BacktestCostSummary | null | undefined =
        result?.cost_summary;
    const missingDataSummary: BacktestMissingDataSummary | undefined =
        result?.missing_data_summary;
    const walkForwardRequest: WalkForwardHandoff | null | undefined =
        result?.walk_forward_request;
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
                const currentWeights = cleanedAssets.map((asset) => asset.weight / 100);
                if (strategy === "NoRebalance") {
                    strategyParams.equity_proportions = currentWeights;
                }
                if (strategy === "Rebalance") {
                    strategyParams.rebal_proportions = currentWeights;
                }
            } else if (needsMultiAsset) {
                currentTickers = [ticker.trim().toUpperCase(), altTicker.trim().toUpperCase()];
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
    const hasStaleResults =
        Boolean(result && lastRunInputSignature && currentInputSignature !== lastRunInputSignature);
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
    const comparisonExportBaseName = buildExportBaseName(
        lastComparisonRequest ?? lastRunRequest,
    );
    const hasResultWorkspace = Boolean(stats || comparisonRuns.length > 0);

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
                    <ConfigPanel title="Configuration">
                        <ConfigSection
                            title="Strategy"
                            description="Select the backtest template and review its default behavior."
                            summary={strategy}
                        >
                            <div className="space-y-2 col-span-full md:col-span-2 lg:col-span-1">
                                <Label className="text-xs text-muted-foreground">
                                    Strategy
                                </Label>
                                <Select
                                    value={strategy}
                                    onValueChange={applyStrategy}
                                >
                                    <SelectTrigger className="border-border/50 bg-background/50">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                                        {strategies?.map((s) => (
                                            <SelectItem
                                                key={s.name}
                                                value={s.name}
                                            >
                                                {s.name}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                                {currentStrategy && (
                                    <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                                        {currentStrategy.description}
                                    </p>
                                )}
                            </div>
                        </ConfigSection>

                        {isAllocationStrategy ? (
                            <ConfigSection
                                title="Portfolio"
                                description="Build or load the allocation that will be tested."
                                summary={
                                    <>
                                        <span>
                                            {portfolioAssets
                                                .map((asset) => asset.ticker)
                                                .join(", ")}
                                        </span>
                                        <span
                                            className={cn(
                                                allocationIsBalanced
                                                    ? "text-emerald-600 dark:text-emerald-400"
                                                    : "text-amber-600 dark:text-amber-400",
                                            )}
                                        >
                                            {formatNumber(
                                                allocationWeightTotal,
                                                1,
                                            )}
                                            %
                                        </span>
                                    </>
                                }
                            >
                                <div className="space-y-4 col-span-full">
                                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                                        <Label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                            Preset Portfolios
                                        </Label>
                                        <Input
                                            value={presetFilter}
                                            onChange={(event) =>
                                                setPresetFilter(
                                                    event.target.value,
                                                )
                                            }
                                            placeholder="Search presets or tickers"
                                            className="h-8 border-border/50 bg-background/50 text-xs sm:max-w-64"
                                        />
                                    </div>
                                    <div className="grid grid-cols-[repeat(auto-fill,minmax(280px,1fr))] gap-4">
                                        {filteredPortfolioPresets.map((preset) => (
                                            <div
                                                key={preset.label}
                                                data-testid={`portfolio-preset-${preset.id}`}
                                                className="rounded-lg border border-border/50 bg-card/40 p-3"
                                            >
                                                <div className="flex items-start justify-between gap-2">
                                                    <div className="min-w-0">
                                                        <p className="truncate text-sm font-semibold text-foreground">
                                                            {preset.label}
                                                        </p>
                                                        <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-muted-foreground">
                                                            {preset.description}
                                                        </p>
                                                    </div>
                                                    <span className="shrink-0 rounded-md border border-border/50 px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
                                                        {preset.assumption}
                                                    </span>
                                                </div>
                                                <p className="mt-2 text-[11px] text-muted-foreground/80">
                                                    {preset.assets
                                                        .map(
                                                            (asset) =>
                                                                `${asset.ticker} ${formatNumber(asset.weight, 0)}%`,
                                                        )
                                                        .join(" / ")}
                                                </p>
                                                <div className="mt-3 flex flex-wrap gap-2">
                                                    <Button
                                                        type="button"
                                                        variant="outline"
                                                        size="xs"
                                                        onClick={() =>
                                                            applyPortfolioPreset(
                                                                preset,
                                                            )
                                                        }
                                                    >
                                                        Load
                                                    </Button>
                                                    <Button
                                                        type="button"
                                                        variant="ghost"
                                                        size="xs"
                                                        onClick={() =>
                                                            handleAddPresetToComparison(
                                                                preset,
                                                            )
                                                        }
                                                    >
                                                        <Plus />
                                                        Compare
                                                    </Button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div className="space-y-4 col-span-full">
                                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                                        <div>
                                            <Label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                                Assets and Weights
                                            </Label>
                                            <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                                                Build the allocation on this
                                                page. Total target weight must
                                                equal 100%.
                                            </p>
                                        </div>
                                        <div className="flex flex-wrap items-center gap-2">
                                            <span
                                                className={cn(
                                                    "text-xs font-medium",
                                                    allocationIsBalanced
                                                        ? "text-emerald-600 dark:text-emerald-400"
                                                        : "text-amber-600 dark:text-amber-400",
                                                )}
                                            >
                                                Total{" "}
                                                {formatNumber(
                                                    allocationWeightTotal,
                                                    1,
                                                )}
                                                %
                                            </span>
                                            <Button
                                                type="button"
                                                variant="outline"
                                                size="xs"
                                                onClick={
                                                    equalizePortfolioWeights
                                                }
                                            >
                                                Equal Weight
                                            </Button>
                                            <Button
                                                type="button"
                                                variant="outline"
                                                size="xs"
                                                onClick={
                                                    normalizePortfolioWeights
                                                }
                                            >
                                                Normalize
                                            </Button>
                                            <Button
                                                type="button"
                                                variant="ghost"
                                                size="xs"
                                                onClick={clearPortfolioAssets}
                                            >
                                                Clear
                                            </Button>
                                            <Button
                                                type="button"
                                                variant="outline"
                                                size="xs"
                                                onClick={handleSavePortfolio}
                                            >
                                                <Save />
                                                Save
                                            </Button>
                                            <Button
                                                type="button"
                                                variant="outline"
                                                size="xs"
                                                onClick={
                                                    handleAddCurrentPortfolioToComparison
                                                }
                                            >
                                                <Plus />
                                                Compare
                                            </Button>
                                            <Button
                                                type="button"
                                                variant="outline"
                                                size="xs"
                                                onClick={addPortfolioAsset}
                                            >
                                                <Plus />
                                                Add Asset
                                            </Button>
                                        </div>
                                    </div>

                                    <div className="space-y-2">
                                        {portfolioAssets.map((asset, index) => (
                                            <div
                                                key={`${asset.ticker}-${index}`}
                                                className="grid grid-cols-1 gap-2 sm:grid-cols-[minmax(0,1fr)_96px_auto]"
                                            >
                                                <Input
                                                    value={asset.ticker}
                                                    onChange={(e) =>
                                                        updatePortfolioTicker(
                                                            index,
                                                            e.target.value,
                                                        )
                                                    }
                                                    placeholder={`Ticker ${index + 1}`}
                                                    className="border-border/50 bg-background/50"
                                                />
                                                <Input
                                                    type="number"
                                                    min={0}
                                                    step={0.1}
                                                    value={asset.weight}
                                                    onChange={(e) =>
                                                        updatePortfolioWeight(
                                                            index,
                                                            e.target.value,
                                                        )
                                                    }
                                                    className="border-border/50 bg-background/50"
                                                    aria-label={`Weight for asset ${index + 1}`}
                                                />
                                                <Button
                                                    type="button"
                                                    variant="ghost"
                                                    size="icon-xs"
                                                    onClick={() =>
                                                        removePortfolioAsset(
                                                            index,
                                                        )
                                                    }
                                                    disabled={
                                                        portfolioAssets.length ===
                                                        1
                                                    }
                                                    aria-label={`Remove asset ${index + 1}`}
                                                >
                                                    <Trash2 />
                                                </Button>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {(savedPortfolios.length > 0 ||
                                    comparisonPortfolios.length > 0) && (
                                    <div className="grid grid-cols-1 gap-6 xl:grid-cols-2 col-span-full">
                                        {savedPortfolios.length > 0 && (
                                            <div className="rounded-lg border border-border/50 bg-background/50 p-4">
                                                <div className="mb-3 flex items-center justify-between gap-3">
                                                    <Label className="text-xs text-muted-foreground">
                                                        Saved Portfolios
                                                    </Label>
                                                    <span className="text-[11px] text-muted-foreground/70">
                                                        {savedPortfolios.length}
                                                    </span>
                                                </div>
                                                <div className="space-y-2">
                                                    {savedPortfolios.map(
                                                        (saved) => (
                                                            <div
                                                                key={saved.id}
                                                                className="flex flex-col gap-2 rounded-md border border-border/40 bg-card/30 p-2 sm:flex-row sm:items-center sm:justify-between"
                                                            >
                                                                <div className="min-w-0">
                                                                    <p className="truncate text-xs font-medium text-foreground">
                                                                        {saved.label}
                                                                    </p>
                                                                    <p className="text-[11px] text-muted-foreground/70">
                                                                        {saved.strategy}
                                                                    </p>
                                                                </div>
                                                                <div className="flex flex-wrap gap-1.5">
                                                                    <Button
                                                                        type="button"
                                                                        variant="outline"
                                                                        size="xs"
                                                                        onClick={() =>
                                                                            applySavedPortfolio(
                                                                                saved,
                                                                            )
                                                                        }
                                                                    >
                                                                        Load
                                                                    </Button>
                                                                    <Button
                                                                        type="button"
                                                                        variant="ghost"
                                                                        size="xs"
                                                                        onClick={() =>
                                                                            handleAddSavedToComparison(
                                                                                saved,
                                                                            )
                                                                        }
                                                                    >
                                                                        Compare
                                                                    </Button>
                                                                    <Button
                                                                        type="button"
                                                                        variant="ghost"
                                                                        size="icon-xs"
                                                                        onClick={() =>
                                                                            removeSavedPortfolio(
                                                                                saved.id,
                                                                            )
                                                                        }
                                                                        aria-label={`Remove ${saved.label}`}
                                                                    >
                                                                        <X />
                                                                    </Button>
                                                                </div>
                                                            </div>
                                                        ),
                                                    )}
                                                </div>
                                            </div>
                                        )}

                                        {comparisonPortfolios.length > 0 && (
                                            <div className="rounded-lg border border-border/50 bg-background/50 p-3">
                                                <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                                                    <div>
                                                        <Label className="text-xs text-muted-foreground">
                                                            Comparison Queue
                                                        </Label>
                                                        <p className="text-[11px] text-muted-foreground/70">
                                                            Shared dates,
                                                            cashflows,
                                                            costs, and data
                                                            policy.
                                                        </p>
                                                    </div>
                                                    <Button
                                                        type="button"
                                                        variant="outline"
                                                        size="xs"
                                                        onClick={
                                                            handleRunComparison
                                                        }
                                                        disabled={
                                                            comparisonMutation.isPending ||
                                                            comparisonPortfolios.length <
                                                                2
                                                        }
                                                    >
                                                        <BarChart3 />
                                                        {comparisonMutation.isPending
                                                            ? "Comparing..."
                                                            : "Run Comparison"}
                                                    </Button>
                                                </div>
                                                <div className="space-y-2">
                                                    {comparisonPortfolios.map(
                                                        (portfolio) => (
                                                            <div
                                                                key={
                                                                    portfolio.id
                                                                }
                                                                className="flex items-center justify-between gap-3 rounded-md border border-border/40 bg-card/30 p-2"
                                                            >
                                                                <div className="min-w-0">
                                                                    <p className="truncate text-xs font-medium text-foreground">
                                                                        {
                                                                            portfolio.label
                                                                        }
                                                                    </p>
                                                                    <p className="text-[11px] text-muted-foreground/70">
                                                                        {
                                                                            portfolio.strategy
                                                                        }{" "}
                                                                        /{" "}
                                                                        {
                                                                            portfolio.source
                                                                        }
                                                                    </p>
                                                                </div>
                                                                <Button
                                                                    type="button"
                                                                    variant="ghost"
                                                                    size="icon-xs"
                                                                    onClick={() =>
                                                                        removeComparisonPortfolio(
                                                                            portfolio.id,
                                                                        )
                                                                    }
                                                                    aria-label={`Remove ${portfolio.label}`}
                                                                >
                                                                    <X />
                                                                </Button>
                                                            </div>
                                                        ),
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </ConfigSection>
                        ) : (
                            <ConfigSection
                                title="Assets"
                                description="Choose the instruments used by this strategy."
                                defaultOpen={false}
                                summary={
                                    needsMultiAsset
                                        ? `${ticker}, ${altTicker}`
                                        : ticker
                                }
                            >
                                <div className="space-y-2">
                                    <Label className="text-xs text-muted-foreground">
                                        Asset
                                    </Label>
                                    <Input
                                        value={ticker}
                                        onChange={(e) =>
                                            setTicker(e.target.value)
                                        }
                                        className="border-border/50 bg-background/50"
                                    />
                                </div>

                                {needsMultiAsset && (
                                    <div className="space-y-2">
                                        <Label className="text-xs text-muted-foreground">
                                            Second Asset
                                        </Label>
                                        <Input
                                            value={altTicker}
                                            onChange={(e) =>
                                                setAltTicker(e.target.value)
                                            }
                                            className="border-border/50 bg-background/50"
                                        />
                                    </div>
                                )}
                            </ConfigSection>
                        )}

                        <ConfigSection
                            title="Run setup"
                            description="Set the date window, capital base, benchmark, and risk-free rate."
                            defaultOpen={false}
                            summary={`${startDate} to ${endDate} / $${formatNumber(cash, 0)}`}
                        >
                        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:col-span-2">
                            <div className="space-y-1.5">
                                <Label className="text-xs text-muted-foreground">
                                    Start
                                </Label>
                                <Input
                                    type="date"
                                    value={startDate}
                                    onChange={(e) =>
                                        setStartDate(e.target.value)
                                    }
                                    className="border-border/50 bg-background/50"
                                />
                            </div>
                            <div className="space-y-1.5">
                                <Label className="text-xs text-muted-foreground">
                                    End
                                </Label>
                                <Input
                                    type="date"
                                    value={endDate}
                                    onChange={(e) => setEndDate(e.target.value)}
                                    className="border-border/50 bg-background/50"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">
                                Initial Cash ($)
                            </Label>
                            <Input
                                type="number"
                                value={cash}
                                onChange={(e) =>
                                    setCash(Number(e.target.value))
                                }
                                className="border-border/50 bg-background/50"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">
                                Benchmark Ticker
                            </Label>
                            <Input
                                value={benchmarkTicker}
                                onChange={(e) =>
                                    setBenchmarkTicker(e.target.value)
                                }
                                placeholder="Leave blank to skip benchmark analysis"
                                className="border-border/50 bg-background/50"
                            />
                            <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                                Compare the backtest to a benchmark on the same
                                date range. Leave blank to keep the existing
                                no-benchmark workflow.
                            </p>
                        </div>

                        <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">
                                Risk-Free Rate
                            </Label>
                            <Input
                                type="number"
                                step={0.01}
                                min={0}
                                max={1}
                                value={riskFreeRate}
                                onChange={(e) =>
                                    setRiskFreeRate(Number(e.target.value))
                                }
                                className="border-border/50 bg-background/50"
                            />
                        </div>
                        </ConfigSection>

                        <ConfigSection
                            title="Data and execution assumptions"
                            description="Surface the gap-handling policy and estimated trade frictions used to contextualize this run."
                            defaultOpen={false}
                            summary={`${
                                MISSING_DATA_POLICY_OPTIONS.find(
                                    (option) =>
                                        option.value === missingDataPolicy,
                                )?.label ?? missingDataPolicy
                            } / ${costAssumptions.commission_mode}`}
                        >
                            <div className="space-y-2 lg:col-span-2">
                                <Label className="text-xs text-muted-foreground">
                                    Missing Data Policy
                                </Label>
                                <Select
                                    value={missingDataPolicy}
                                    onValueChange={(value) =>
                                        setMissingDataPolicy(
                                            value as MissingDataPolicy,
                                        )
                                    }
                                >
                                    <SelectTrigger className="border-border/50 bg-background/50">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                                        {MISSING_DATA_POLICY_OPTIONS.map(
                                            (option) => (
                                                <SelectItem
                                                    key={option.value}
                                                    value={option.value}
                                                >
                                                    {option.label}
                                                </SelectItem>
                                            ),
                                        )}
                                    </SelectContent>
                                </Select>
                                <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                                    {
                                        MISSING_DATA_POLICY_OPTIONS.find(
                                            (option) =>
                                                option.value ===
                                                missingDataPolicy,
                                        )?.description
                                    }
                                </p>
                            </div>

                            <div className="space-y-2">
                                <Label className="text-xs text-muted-foreground">
                                    Commission Model
                                </Label>
                                <Select
                                    value={costAssumptions.commission_mode}
                                    onValueChange={(value) =>
                                        updateCostAssumption(
                                            "commission_mode",
                                            value as BacktestCostAssumptions["commission_mode"],
                                        )
                                    }
                                >
                                    <SelectTrigger className="border-border/50 bg-background/50">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                                        {COMMISSION_MODE_OPTIONS.map(
                                            (option) => (
                                                <SelectItem
                                                    key={option.value}
                                                    value={option.value}
                                                >
                                                    {option.label}
                                                </SelectItem>
                                            ),
                                        )}
                                    </SelectContent>
                                </Select>
                            </div>

                            {costAssumptions.commission_mode ===
                                "per_share" && (
                                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                                    <div className="space-y-1.5">
                                        <Label className="text-xs text-muted-foreground">
                                            Per Share ($)
                                        </Label>
                                        <Input
                                            type="number"
                                            min={0}
                                            step={0.0001}
                                            value={
                                                costAssumptions.commission_per_share
                                            }
                                            onChange={(e) =>
                                                updateCostAssumption(
                                                    "commission_per_share",
                                                    Number(e.target.value),
                                                )
                                            }
                                            className="border-border/50 bg-background/50"
                                        />
                                    </div>
                                    <div className="space-y-1.5">
                                        <Label className="text-xs text-muted-foreground">
                                            Minimum ($)
                                        </Label>
                                        <Input
                                            type="number"
                                            min={0}
                                            step={0.01}
                                            value={
                                                costAssumptions.commission_minimum
                                            }
                                            onChange={(e) =>
                                                updateCostAssumption(
                                                    "commission_minimum",
                                                    Number(e.target.value),
                                                )
                                            }
                                            className="border-border/50 bg-background/50"
                                        />
                                    </div>
                                </div>
                            )}

                            {costAssumptions.commission_mode ===
                                "percentage" && (
                                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                                    <div className="space-y-1.5">
                                        <Label className="text-xs text-muted-foreground">
                                            Commission (bps)
                                        </Label>
                                        <Input
                                            type="number"
                                            min={0}
                                            step={0.1}
                                            value={
                                                costAssumptions.commission_bps
                                            }
                                            onChange={(e) =>
                                                updateCostAssumption(
                                                    "commission_bps",
                                                    Number(e.target.value),
                                                )
                                            }
                                            className="border-border/50 bg-background/50"
                                        />
                                    </div>
                                    <div className="space-y-1.5">
                                        <Label className="text-xs text-muted-foreground">
                                            Minimum ($)
                                        </Label>
                                        <Input
                                            type="number"
                                            min={0}
                                            step={0.01}
                                            value={
                                                costAssumptions.commission_minimum
                                            }
                                            onChange={(e) =>
                                                updateCostAssumption(
                                                    "commission_minimum",
                                                    Number(e.target.value),
                                                )
                                            }
                                            className="border-border/50 bg-background/50"
                                        />
                                    </div>
                                </div>
                            )}

                            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:col-span-2">
                                <div className="space-y-1.5">
                                    <Label className="text-xs text-muted-foreground">
                                        Spread (bps)
                                    </Label>
                                    <Input
                                        type="number"
                                        min={0}
                                        step={0.1}
                                        value={costAssumptions.spread_bps}
                                        onChange={(e) =>
                                            updateCostAssumption(
                                                "spread_bps",
                                                Number(e.target.value),
                                            )
                                        }
                                        className="border-border/50 bg-background/50"
                                    />
                                </div>
                                <div className="space-y-1.5">
                                    <Label className="text-xs text-muted-foreground">
                                        Slippage (bps)
                                    </Label>
                                    <Input
                                        type="number"
                                        min={0}
                                        step={0.1}
                                        value={costAssumptions.slippage_bps}
                                        onChange={(e) =>
                                            updateCostAssumption(
                                                "slippage_bps",
                                                Number(e.target.value),
                                            )
                                        }
                                        className="border-border/50 bg-background/50"
                                    />
                                </div>
                            </div>
                        </ConfigSection>

                        <ConfigSection
                            title="Cashflow planning"
                            description="Model recurring savings, portfolio-funded withdrawals, and dated one-off events in the same backtest run."
                            summary={
                                recurringContribution ||
                                recurringWithdrawal ||
                                oneTimeCashflows.length
                                    ? `${oneTimeCashflows.length} one-time event${
                                          oneTimeCashflows.length === 1
                                              ? ""
                                              : "s"
                                      }`
                                    : "No cashflows"
                            }
                        >
                            <div className="grid grid-cols-1 gap-2 sm:grid-cols-[minmax(0,1fr)_132px] lg:col-span-2">
                                <Input
                                    type="number"
                                    value={recurringContribution}
                                    onChange={(e) =>
                                        setRecurringContribution(
                                            Number(e.target.value),
                                        )
                                    }
                                    placeholder="Recurring contribution"
                                    className="border-border/50 bg-background/50"
                                />
                                <Select
                                    value={contributionFrequency}
                                    onValueChange={(value) =>
                                        setContributionFrequency(
                                            value as RecurringCashflowRule["frequency"],
                                        )
                                    }
                                >
                                    <SelectTrigger className="border-border/50 bg-background/50">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                                        {CASHFLOW_FREQUENCY_OPTIONS.map(
                                            (option) => (
                                                <SelectItem
                                                    key={`contrib-${option.value}`}
                                                    value={option.value}
                                                >
                                                    {option.label}
                                                </SelectItem>
                                            ),
                                        )}
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="grid grid-cols-1 gap-2 sm:grid-cols-[minmax(0,1fr)_132px] lg:col-span-2">
                                <Input
                                    type="number"
                                    value={recurringWithdrawal}
                                    onChange={(e) =>
                                        setRecurringWithdrawal(
                                            Number(e.target.value),
                                        )
                                    }
                                    placeholder="Recurring withdrawal"
                                    className="border-border/50 bg-background/50"
                                />
                                <Select
                                    value={withdrawalFrequency}
                                    onValueChange={(value) =>
                                        setWithdrawalFrequency(
                                            value as RecurringCashflowRule["frequency"],
                                        )
                                    }
                                >
                                    <SelectTrigger className="border-border/50 bg-background/50">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                                        {CASHFLOW_FREQUENCY_OPTIONS.map(
                                            (option) => (
                                                <SelectItem
                                                    key={`withdraw-${option.value}`}
                                                    value={option.value}
                                                >
                                                    {option.label}
                                                </SelectItem>
                                            ),
                                        )}
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="space-y-2 lg:col-span-2">
                                <Label className="text-xs text-muted-foreground">
                                    Inflation Rate
                                </Label>
                                <Input
                                    type="number"
                                    step={0.01}
                                    min={0}
                                    max={1}
                                    value={inflationRate}
                                    onChange={(e) =>
                                        setInflationRate(Number(e.target.value))
                                    }
                                    className="border-border/50 bg-background/50"
                                />
                            </div>

                            <div className="space-y-2">
                                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                                    <div>
                                        <Label className="text-xs text-muted-foreground">
                                            One-Time Events
                                        </Label>
                                        <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                                            Positive amounts add capital.
                                            Negative amounts withdraw it.
                                        </p>
                                    </div>
                                    <Button
                                        type="button"
                                        variant="outline"
                                        size="xs"
                                        onClick={addOneTimeCashflow}
                                    >
                                        <Plus />
                                        Add Event
                                    </Button>
                                </div>

                                {oneTimeCashflows.length > 0 && (
                                    <div className="space-y-2">
                                        {oneTimeCashflows.map(
                                            (event, index) => (
                                                <div
                                                    key={`${event.date}-${index}`}
                                                    className="grid grid-cols-1 gap-2 sm:grid-cols-[132px_minmax(0,1fr)_minmax(0,1fr)_auto]"
                                                >
                                                    <Input
                                                        type="date"
                                                        value={event.date}
                                                        onChange={(e) =>
                                                            updateOneTimeCashflow(
                                                                index,
                                                                {
                                                                    date: e
                                                                        .target
                                                                        .value,
                                                                },
                                                            )
                                                        }
                                                        className="border-border/50 bg-background/50"
                                                        aria-label={`Date for cashflow event ${index + 1}`}
                                                    />
                                                    <Input
                                                        type="number"
                                                        value={event.amount}
                                                        onChange={(e) =>
                                                            updateOneTimeCashflow(
                                                                index,
                                                                {
                                                                    amount: Number(
                                                                        e.target
                                                                            .value,
                                                                    ),
                                                                },
                                                            )
                                                        }
                                                        placeholder="Amount"
                                                        className="border-border/50 bg-background/50"
                                                        aria-label={`Amount for cashflow event ${index + 1}`}
                                                    />
                                                    <Input
                                                        value={
                                                            event.label ?? ""
                                                        }
                                                        onChange={(e) =>
                                                            updateOneTimeCashflow(
                                                                index,
                                                                {
                                                                    label: e
                                                                        .target
                                                                        .value,
                                                                },
                                                            )
                                                        }
                                                        placeholder="Optional label"
                                                        className="border-border/50 bg-background/50"
                                                        aria-label={`Label for cashflow event ${index + 1}`}
                                                    />
                                                    <Button
                                                        type="button"
                                                        variant="ghost"
                                                        size="icon-xs"
                                                        onClick={() =>
                                                            removeOneTimeCashflow(
                                                                index,
                                                            )
                                                        }
                                                        aria-label={`Remove cashflow event ${index + 1}`}
                                                    >
                                                        <Trash2 />
                                                    </Button>
                                                </div>
                                            ),
                                        )}
                                    </div>
                                )}
                            </div>
                        </ConfigSection>

                        {/* Dynamic strategy params */}
                        {currentStrategy && currentStrategy.params.length > 0 ? (
                            <ConfigSection
                                title="Strategy parameters"
                                description="Fine-tune the selected strategy's numeric inputs."
                                defaultOpen={false}
                            >
                                {currentStrategy.params.map((p) => (
                                    <div key={p.name} className="space-y-1.5">
                                        <Label className="text-xs text-muted-foreground">
                                            {p.description || p.name}
                                        </Label>
                                        <Input
                                            type="number"
                                            step={p.type === "float" ? 0.01 : 1}
                                            value={params[p.name] ?? p.default}
                                            onChange={(e) =>
                                                setParams((prev) => ({
                                                    ...prev,
                                                    [p.name]: Number(
                                                        e.target.value,
                                                    ),
                                                }))
                                            }
                                            className="border-border/50 bg-background/50"
                                        />
                                    </div>
                                ))}
                            </ConfigSection>
                        ) : null}

                        <div className="col-span-full flex justify-end border-t border-border/40 pt-4">
                            <div className="w-full sm:w-auto sm:min-w-48">
                                <Button
                                    className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
                                    onClick={handleRun}
                                    disabled={mutation.isPending}
                                >
                                    {mutation.isPending
                                        ? "Running..."
                                        : "Run Backtest"}
                                </Button>
                            </div>
                        </div>
                    </ConfigPanel>
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
                    <>
                        <ResultWorkspaceSummary
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
                            onTabChange={setActiveResultTab}
                        />

                        {activeResultTab === "audit" && (
                            <AuditTab
                                savedExperiment={savedExperiment}
                                costSummary={costSummary}
                                appliedCostAssumptions={appliedCostAssumptions}
                                costBySymbolRows={costBySymbolRows}
                                missingDataSummary={missingDataSummary}
                                walkForwardRequest={walkForwardRequest}
                                walkForwardHref={walkForwardHref}
                                stats={stats}
                            />
                        )}

                        {activeResultTab === "cashflows" && (
                            <CashflowsTab
                                withdrawalDurability={withdrawalDurability}
                                inflationAdjustedSeries={
                                    inflationAdjustedSeries
                                }
                                cashflowEvents={cashflowEvents}
                            />
                        )}

                        {activeResultTab === "overview" && (
                            <OverviewTab
                                benchmarkStats={benchmarkStats}
                                comparisonChartSeries={comparisonChartSeries}
                                visiblePortfolioChartSeries={
                                    visiblePortfolioChartSeries
                                }
                                valueHistory={result?.value_history ?? []}
                                portfolioChartLogScale={
                                    portfolioChartLogScale
                                }
                                showPortfolioSeries={showPortfolioSeries}
                                showBenchmarkSeries={showBenchmarkSeries}
                                exportBaseName={buildExportBaseName(
                                    lastRunRequest,
                                )}
                                onTogglePortfolioSeries={() =>
                                    setShowPortfolioSeries((value) => !value)
                                }
                                onToggleBenchmarkSeries={() =>
                                    setShowBenchmarkSeries((value) => !value)
                                }
                                onToggleLogScale={() =>
                                    setPortfolioChartLogScale(
                                        (value) => !value,
                                    )
                                }
                            />
                        )}

                        {activeResultTab === "diagnostics" && (
                            <DiagnosticsTab
                                rollingMetrics={rollingMetrics}
                                rollingChartData={rollingChartData}
                                regimeSummary={regimeSummary}
                                regimePeriods={regimePeriods}
                                regimeReferenceTicker={regimeReferenceTicker}
                                allocationChartData={allocationChartData}
                                allocationSeriesKeys={allocationSeriesKeys}
                                allocationDriftSummary={allocationDriftSummary}
                                rebalanceEvents={rebalanceEvents}
                            />
                        )}

                        {activeResultTab === "comparison" && (
                            <ComparisonResultsTab
                                comparisonRuns={comparisonRuns}
                                comparisonRows={comparisonRows}
                                comparisonResultSeries={comparisonResultSeries}
                                comparisonDrawdownSeries={
                                    comparisonDrawdownSeries
                                }
                                exportBaseName={comparisonExportBaseName}
                                onExportCsv={handleExportComparisonCsv}
                            />
                        )}

                        {activeResultTab === "returns" && (
                            <ReturnsTab
                                monthlyReturns={monthlyReturns}
                                annualReturns={annualReturns}
                                trades={result?.trades ?? []}
                            />
                        )}

                    </>
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
