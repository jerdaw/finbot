"use client";

import { toast } from "sonner";
import {
    MAX_COMPARISON_PORTFOLIOS,
    STRATEGY_FALLBACK_PARAMS,
    type PortfolioPreset,
} from "@/app/backtesting/backtesting-options";
import {
    buildPortfolioLabel,
    buildPortfolioStrategyParams,
    cloneAssets,
} from "@/lib/backtest-utils";
import type {
    BacktestState,
    ComparisonPortfolio,
    PortfolioAsset,
    SavedPortfolio,
} from "@/stores/backtest-store";

interface UseBacktestingPortfolioActionsArgs {
    strategy: string;
    params: Record<string, number>;
    portfolioAssets: PortfolioAsset[];
    isAllocationStrategy: boolean;
    allocationIsBalanced: boolean;
    comparisonPortfolios: ComparisonPortfolio[];
    setPortfolioAssets: BacktestState["setPortfolioAssets"];
    setSavedPortfolios: BacktestState["setSavedPortfolios"];
    setComparisonPortfolios: BacktestState["setComparisonPortfolios"];
    setParams: BacktestState["setParams"];
    applyStrategy: (name: string) => void;
    onRunComparison: (portfolios: ComparisonPortfolio[]) => void;
}

export function useBacktestingPortfolioActions({
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
    onRunComparison,
}: UseBacktestingPortfolioActionsArgs) {
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
                    ? {
                          ...asset,
                          weight: Number((asset.weight + delta).toFixed(2)),
                      }
                    : asset,
            );
        });
    };

    const clearPortfolioAssets = () => {
        setPortfolioAssets([{ ticker: "", weight: 0 }]);
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
        setSavedPortfolios((current) =>
            current.filter((portfolio) => portfolio.id !== id),
        );
    };

    const addComparisonPortfolio = (
        portfolio: Omit<ComparisonPortfolio, "id">,
    ) => {
        setComparisonPortfolios((current) => {
            if (current.length >= MAX_COMPARISON_PORTFOLIOS) {
                toast.error(
                    `Compare up to ${MAX_COMPARISON_PORTFOLIOS} portfolios at a time.`,
                );
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
        setComparisonPortfolios((current) =>
            current.filter((portfolio) => portfolio.id !== id),
        );
    };

    const handleRunComparison = () => {
        if (comparisonPortfolios.length < 2) {
            toast.error("Add at least two portfolios to compare.");
            return;
        }
        onRunComparison(comparisonPortfolios);
    };

    return {
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
    };
}
