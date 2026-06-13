"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import { PORTFOLIO_PRESETS } from "@/app/backtesting/backtesting-options";
import type { StrategyInfo } from "@/types/api";
import type { PortfolioAsset } from "@/stores/backtest-store";

interface UseBacktestingConfigurationDataArgs {
    strategy: string;
    portfolioAssets: PortfolioAsset[];
    presetFilter: string;
}

export function useBacktestingConfigurationData({
    strategy,
    portfolioAssets,
    presetFilter,
}: UseBacktestingConfigurationDataArgs) {
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

    return {
        strategies,
        currentStrategy,
        isAllocationStrategy,
        needsMultiAsset,
        allocationWeightTotal,
        allocationIsBalanced,
        filteredPortfolioPresets,
    };
}
