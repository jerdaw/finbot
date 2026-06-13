"use client";

import { StatCard } from "@/components/common/stat-card";
import {
    Tabs,
    TabsList,
    TabsTrigger,
} from "@/components/ui/tabs";
import { formatNumber, formatPercent } from "@/lib/format";

interface ResultWorkspaceSummaryProps {
    stats: Record<string, unknown> | null | undefined;
    title: string;
    strategy?: string;
    detail: string;
    hasStaleResults: boolean;
    activeTab: string;
    onTabChange: (value: string) => void;
}

export function ResultWorkspaceSummary({
    stats,
    title,
    strategy,
    detail,
    hasStaleResults,
    activeTab,
    onTabChange,
}: ResultWorkspaceSummaryProps) {
    return (
        <>
            {stats && (
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    <StatCard
                        label="CAGR"
                        value={formatPercent(stats["CAGR"] as number)}
                        trend={
                            (stats["CAGR"] as number) > 0 ? "up" : "down"
                        }
                    />
                    <StatCard
                        label="Sharpe Ratio"
                        value={formatNumber(stats["Sharpe"] as number, 3)}
                        trend={
                            (stats["Sharpe"] as number) > 0 ? "up" : "down"
                        }
                    />
                    <StatCard
                        label="Max Drawdown"
                        value={formatPercent(
                            stats["Max Drawdown"] as number,
                        )}
                        trend="down"
                    />
                    <StatCard
                        label="ROI"
                        value={formatPercent(stats["ROI"] as number)}
                        trend={(stats["ROI"] as number) > 0 ? "up" : "down"}
                    />
                </div>
            )}

            <div className="sticky top-16 z-20 rounded-lg border border-border/60 bg-background/90 p-3 shadow-sm backdrop-blur-xl">
                <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                    <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                            <p className="truncate text-sm font-semibold text-foreground">
                                <span data-testid="backtest-result-summary-title">
                                    {title}
                                </span>
                            </p>
                            {strategy && (
                                <span className="rounded-md border border-border/60 bg-muted/30 px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
                                    {strategy}
                                </span>
                            )}
                            {hasStaleResults && (
                                <span className="rounded-md border border-amber-500/40 bg-amber-500/10 px-2 py-0.5 text-[11px] font-medium text-amber-600 dark:text-amber-300">
                                    Inputs changed
                                </span>
                            )}
                        </div>
                        <p className="mt-1 text-xs text-muted-foreground">
                            {detail}
                        </p>
                    </div>
                    <Tabs
                        value={activeTab}
                        onValueChange={onTabChange}
                        className="min-w-0"
                    >
                        <TabsList>
                            <TabsTrigger value="overview">Overview</TabsTrigger>
                            <TabsTrigger value="comparison">Compare</TabsTrigger>
                            <TabsTrigger value="audit">Audit</TabsTrigger>
                            <TabsTrigger value="cashflows">Cashflows</TabsTrigger>
                            <TabsTrigger value="diagnostics">
                                Diagnostics
                            </TabsTrigger>
                            <TabsTrigger value="returns">Returns</TabsTrigger>
                        </TabsList>
                    </Tabs>
                </div>
            </div>
        </>
    );
}
