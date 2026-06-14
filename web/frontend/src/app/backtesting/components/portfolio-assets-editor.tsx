"use client";

import { Plus, Save, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { formatNumber } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { PortfolioAsset } from "@/stores/backtest-store";

interface PortfolioAssetsEditorProps {
    portfolioAssets: PortfolioAsset[];
    allocationIsBalanced: boolean;
    allocationWeightTotal: number;
    onEqualizeWeights: () => void;
    onNormalizeWeights: () => void;
    onClearAssets: () => void;
    onSavePortfolio: () => void;
    onAddCurrentToComparison: () => void;
    onAddAsset: () => void;
    onUpdateTicker: (index: number, value: string) => void;
    onUpdateWeight: (index: number, value: string) => void;
    onRemoveAsset: (index: number) => void;
}

export function PortfolioAssetsEditor({
    portfolioAssets,
    allocationIsBalanced,
    allocationWeightTotal,
    onEqualizeWeights,
    onNormalizeWeights,
    onClearAssets,
    onSavePortfolio,
    onAddCurrentToComparison,
    onAddAsset,
    onUpdateTicker,
    onUpdateWeight,
    onRemoveAsset,
}: PortfolioAssetsEditorProps) {
    return (
        <div className="space-y-4 col-span-full">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <Label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                        Assets and Weights
                    </Label>
                    <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                        Build the allocation on this page. Total target weight
                        must equal 100%.
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
    );
}
