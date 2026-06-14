"use client";

import { ConfigSection } from "@/components/common/config-panel";
import { ComparisonQueuePanel } from "@/app/backtesting/components/comparison-queue-panel";
import { PortfolioAssetsEditor } from "@/app/backtesting/components/portfolio-assets-editor";
import { PortfolioPresetGrid } from "@/app/backtesting/components/portfolio-preset-grid";
import { SavedPortfoliosPanel } from "@/app/backtesting/components/saved-portfolios-panel";
import { formatNumber } from "@/lib/format";
import { cn } from "@/lib/utils";
import type {
    ComparisonPortfolio,
    PortfolioAsset,
    SavedPortfolio,
} from "@/stores/backtest-store";
import type { PortfolioPreset } from "@/app/backtesting/backtesting-options";

interface PortfolioBuilderSectionProps {
    portfolioAssets: PortfolioAsset[];
    allocationIsBalanced: boolean;
    allocationWeightTotal: number;
    presetFilter: string;
    filteredPortfolioPresets: PortfolioPreset[];
    savedPortfolios: SavedPortfolio[];
    comparisonPortfolios: ComparisonPortfolio[];
    comparisonIsPending: boolean;
    onPresetFilterChange: (value: string) => void;
    onApplyPreset: (preset: PortfolioPreset) => void;
    onAddPresetToComparison: (preset: PortfolioPreset) => void;
    onEqualizeWeights: () => void;
    onNormalizeWeights: () => void;
    onClearAssets: () => void;
    onSavePortfolio: () => void;
    onAddCurrentToComparison: () => void;
    onAddAsset: () => void;
    onUpdateTicker: (index: number, value: string) => void;
    onUpdateWeight: (index: number, value: string) => void;
    onRemoveAsset: (index: number) => void;
    onApplySavedPortfolio: (portfolio: SavedPortfolio) => void;
    onAddSavedToComparison: (portfolio: SavedPortfolio) => void;
    onRemoveSavedPortfolio: (id: string) => void;
    onRunComparison: () => void;
    onRemoveComparisonPortfolio: (id: string) => void;
}

export function PortfolioBuilderSection({
    portfolioAssets,
    allocationIsBalanced,
    allocationWeightTotal,
    presetFilter,
    filteredPortfolioPresets,
    savedPortfolios,
    comparisonPortfolios,
    comparisonIsPending,
    onPresetFilterChange,
    onApplyPreset,
    onAddPresetToComparison,
    onEqualizeWeights,
    onNormalizeWeights,
    onClearAssets,
    onSavePortfolio,
    onAddCurrentToComparison,
    onAddAsset,
    onUpdateTicker,
    onUpdateWeight,
    onRemoveAsset,
    onApplySavedPortfolio,
    onAddSavedToComparison,
    onRemoveSavedPortfolio,
    onRunComparison,
    onRemoveComparisonPortfolio,
}: PortfolioBuilderSectionProps) {
    return (
        <ConfigSection
            title="Portfolio"
            description="Build or load the allocation that will be tested."
            summary={
                <>
                    <span>
                        {portfolioAssets.map((asset) => asset.ticker).join(", ")}
                    </span>
                    <span
                        className={cn(
                            allocationIsBalanced
                                ? "text-emerald-600 dark:text-emerald-400"
                                : "text-amber-600 dark:text-amber-400",
                        )}
                    >
                        {formatNumber(allocationWeightTotal, 1)}%
                    </span>
                </>
            }
        >
            <PortfolioPresetGrid
                presetFilter={presetFilter}
                filteredPortfolioPresets={filteredPortfolioPresets}
                onPresetFilterChange={onPresetFilterChange}
                onApplyPreset={onApplyPreset}
                onAddPresetToComparison={onAddPresetToComparison}
            />

            <PortfolioAssetsEditor
                portfolioAssets={portfolioAssets}
                allocationIsBalanced={allocationIsBalanced}
                allocationWeightTotal={allocationWeightTotal}
                onEqualizeWeights={onEqualizeWeights}
                onNormalizeWeights={onNormalizeWeights}
                onClearAssets={onClearAssets}
                onSavePortfolio={onSavePortfolio}
                onAddCurrentToComparison={onAddCurrentToComparison}
                onAddAsset={onAddAsset}
                onUpdateTicker={onUpdateTicker}
                onUpdateWeight={onUpdateWeight}
                onRemoveAsset={onRemoveAsset}
            />

            {(savedPortfolios.length > 0 ||
                comparisonPortfolios.length > 0) && (
                <div className="grid grid-cols-1 gap-6 xl:grid-cols-2 col-span-full">
                    {savedPortfolios.length > 0 && (
                        <SavedPortfoliosPanel
                            savedPortfolios={savedPortfolios}
                            onApplySavedPortfolio={onApplySavedPortfolio}
                            onAddSavedToComparison={onAddSavedToComparison}
                            onRemoveSavedPortfolio={onRemoveSavedPortfolio}
                        />
                    )}

                    {comparisonPortfolios.length > 0 && (
                        <ComparisonQueuePanel
                            comparisonPortfolios={comparisonPortfolios}
                            comparisonIsPending={comparisonIsPending}
                            onRunComparison={onRunComparison}
                            onRemoveComparisonPortfolio={
                                onRemoveComparisonPortfolio
                            }
                        />
                    )}
                </div>
            )}
        </ConfigSection>
    );
}
