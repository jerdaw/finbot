"use client";

import { BarChart3, Plus, Save, Trash2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ConfigSection } from "@/components/common/config-panel";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
            <div className="space-y-4 col-span-full">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <Label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                        Preset Portfolios
                    </Label>
                    <Input
                        value={presetFilter}
                        onChange={(event) =>
                            onPresetFilterChange(event.target.value)
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
                                    onClick={() => onApplyPreset(preset)}
                                >
                                    Load
                                </Button>
                                <Button
                                    type="button"
                                    variant="ghost"
                                    size="xs"
                                    onClick={() =>
                                        onAddPresetToComparison(preset)
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
                            Build the allocation on this page. Total target
                            weight must equal 100%.
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
                            Total {formatNumber(allocationWeightTotal, 1)}%
                        </span>
                        <Button
                            type="button"
                            variant="outline"
                            size="xs"
                            onClick={onEqualizeWeights}
                        >
                            Equal Weight
                        </Button>
                        <Button
                            type="button"
                            variant="outline"
                            size="xs"
                            onClick={onNormalizeWeights}
                        >
                            Normalize
                        </Button>
                        <Button
                            type="button"
                            variant="ghost"
                            size="xs"
                            onClick={onClearAssets}
                        >
                            Clear
                        </Button>
                        <Button
                            type="button"
                            variant="outline"
                            size="xs"
                            onClick={onSavePortfolio}
                        >
                            <Save />
                            Save
                        </Button>
                        <Button
                            type="button"
                            variant="outline"
                            size="xs"
                            onClick={onAddCurrentToComparison}
                        >
                            <Plus />
                            Compare
                        </Button>
                        <Button
                            type="button"
                            variant="outline"
                            size="xs"
                            onClick={onAddAsset}
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
                                onChange={(event) =>
                                    onUpdateTicker(index, event.target.value)
                                }
                                placeholder={`Ticker ${index + 1}`}
                                className="border-border/50 bg-background/50"
                            />
                            <Input
                                type="number"
                                min={0}
                                step={0.1}
                                value={asset.weight}
                                onChange={(event) =>
                                    onUpdateWeight(index, event.target.value)
                                }
                                className="border-border/50 bg-background/50"
                                aria-label={`Weight for asset ${index + 1}`}
                            />
                            <Button
                                type="button"
                                variant="ghost"
                                size="icon-xs"
                                onClick={() => onRemoveAsset(index)}
                                disabled={portfolioAssets.length === 1}
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
                                {savedPortfolios.map((saved) => (
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
                                                    onApplySavedPortfolio(saved)
                                                }
                                            >
                                                Load
                                            </Button>
                                            <Button
                                                type="button"
                                                variant="ghost"
                                                size="xs"
                                                onClick={() =>
                                                    onAddSavedToComparison(
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
                                                    onRemoveSavedPortfolio(
                                                        saved.id,
                                                    )
                                                }
                                                aria-label={`Remove ${saved.label}`}
                                            >
                                                <X />
                                            </Button>
                                        </div>
                                    </div>
                                ))}
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
                                        Shared dates, cashflows, costs, and data
                                        policy.
                                    </p>
                                </div>
                                <Button
                                    type="button"
                                    variant="outline"
                                    size="xs"
                                    onClick={onRunComparison}
                                    disabled={
                                        comparisonIsPending ||
                                        comparisonPortfolios.length < 2
                                    }
                                >
                                    <BarChart3 />
                                    {comparisonIsPending
                                        ? "Comparing..."
                                        : "Run Comparison"}
                                </Button>
                            </div>
                            <div className="space-y-2">
                                {comparisonPortfolios.map((portfolio) => (
                                    <div
                                        key={portfolio.id}
                                        className="flex items-center justify-between gap-3 rounded-md border border-border/40 bg-card/30 p-2"
                                    >
                                        <div className="min-w-0">
                                            <p className="truncate text-xs font-medium text-foreground">
                                                {portfolio.label}
                                            </p>
                                            <p className="text-[11px] text-muted-foreground/70">
                                                {portfolio.strategy} /{" "}
                                                {portfolio.source}
                                            </p>
                                        </div>
                                        <Button
                                            type="button"
                                            variant="ghost"
                                            size="icon-xs"
                                            onClick={() =>
                                                onRemoveComparisonPortfolio(
                                                    portfolio.id,
                                                )
                                            }
                                            aria-label={`Remove ${portfolio.label}`}
                                        >
                                            <X />
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </ConfigSection>
    );
}
