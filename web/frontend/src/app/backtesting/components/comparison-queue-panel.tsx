"use client";

import { BarChart3, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import type { ComparisonPortfolio } from "@/stores/backtest-store";

interface ComparisonQueuePanelProps {
    comparisonPortfolios: ComparisonPortfolio[];
    comparisonIsPending: boolean;
    onRunComparison: () => void;
    onRemoveComparisonPortfolio: (id: string) => void;
}

export function ComparisonQueuePanel({
    comparisonPortfolios,
    comparisonIsPending,
    onRunComparison,
    onRemoveComparisonPortfolio,
}: ComparisonQueuePanelProps) {
    return (
        <div className="rounded-lg border border-border/50 bg-background/50 p-3">
            <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <Label className="text-xs text-muted-foreground">
                        Comparison Queue
                    </Label>
                    <p className="text-[11px] text-muted-foreground/70">
                        Shared dates, cashflows, costs, and data policy.
                    </p>
                </div>
                <Button
                    type="button"
                    variant="outline"
                    size="xs"
                    onClick={onRunComparison}
                    disabled={comparisonIsPending || comparisonPortfolios.length < 2}
                >
                    <BarChart3 />
                    {comparisonIsPending ? "Comparing..." : "Run Comparison"}
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
                                {portfolio.strategy} / {portfolio.source}
                            </p>
                        </div>
                        <Button
                            type="button"
                            variant="ghost"
                            size="icon-xs"
                            onClick={() =>
                                onRemoveComparisonPortfolio(portfolio.id)
                            }
                            aria-label={`Remove ${portfolio.label}`}
                        >
                            <X />
                        </Button>
                    </div>
                ))}
            </div>
        </div>
    );
}
