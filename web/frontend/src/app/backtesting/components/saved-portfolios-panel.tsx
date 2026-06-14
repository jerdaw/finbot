"use client";

import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import type { SavedPortfolio } from "@/stores/backtest-store";

interface SavedPortfoliosPanelProps {
    savedPortfolios: SavedPortfolio[];
    onApplySavedPortfolio: (portfolio: SavedPortfolio) => void;
    onAddSavedToComparison: (portfolio: SavedPortfolio) => void;
    onRemoveSavedPortfolio: (id: string) => void;
}

export function SavedPortfoliosPanel({
    savedPortfolios,
    onApplySavedPortfolio,
    onAddSavedToComparison,
    onRemoveSavedPortfolio,
}: SavedPortfoliosPanelProps) {
    return (
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
                                onClick={() => onApplySavedPortfolio(saved)}
                            >
                                Load
                            </Button>
                            <Button
                                type="button"
                                variant="ghost"
                                size="xs"
                                onClick={() => onAddSavedToComparison(saved)}
                            >
                                Compare
                            </Button>
                            <Button
                                type="button"
                                variant="ghost"
                                size="icon-xs"
                                onClick={() => onRemoveSavedPortfolio(saved.id)}
                                aria-label={`Remove ${saved.label}`}
                            >
                                <X />
                            </Button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
