"use client";

import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { formatNumber } from "@/lib/format";
import type { PortfolioPreset } from "@/app/backtesting/backtesting-options";

interface PortfolioPresetGridProps {
    presetFilter: string;
    filteredPortfolioPresets: PortfolioPreset[];
    onPresetFilterChange: (value: string) => void;
    onApplyPreset: (preset: PortfolioPreset) => void;
    onAddPresetToComparison: (preset: PortfolioPreset) => void;
}

export function PortfolioPresetGrid({
    presetFilter,
    filteredPortfolioPresets,
    onPresetFilterChange,
    onApplyPreset,
    onAddPresetToComparison,
}: PortfolioPresetGridProps) {
    return (
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
                                onClick={() => onAddPresetToComparison(preset)}
                            >
                                <Plus />
                                Compare
                            </Button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
