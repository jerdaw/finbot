"use client";

import Link from "next/link";
import { Download, Share2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/common/page-header";
import type { BacktestResponse, WalkForwardHandoff } from "@/types/api";

interface BacktestingPageHeaderProps {
    result: BacktestResponse | undefined;
    walkForwardRequest: WalkForwardHandoff | null | undefined;
    walkForwardHref: string;
    saveExperimentIsPending: boolean;
    canSaveExperiment: boolean;
    onShareConfig: () => void;
    onExportCsv: () => void;
    onExportReturnsCsv: () => void;
    onExportTradesCsv: () => void;
    onExportJson: () => void;
    onSaveExperiment: () => void;
}

export function BacktestingPageHeader({
    result,
    walkForwardRequest,
    walkForwardHref,
    saveExperimentIsPending,
    canSaveExperiment,
    onShareConfig,
    onExportCsv,
    onExportReturnsCsv,
    onExportTradesCsv,
    onExportJson,
    onSaveExperiment,
}: BacktestingPageHeaderProps) {
    return (
        <PageHeader
            title="Strategy Backtester"
            description="Run allocation backtests or trading strategies on historical data"
            actions={
                <>
                    <Button
                        type="button"
                        variant="outline"
                        onClick={onShareConfig}
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
                                onClick={onExportCsv}
                            >
                                <Download className="h-3.5 w-3.5" />
                                Export CSV
                            </Button>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={onExportReturnsCsv}
                            >
                                <Download className="h-3.5 w-3.5" />
                                Returns
                            </Button>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={onExportTradesCsv}
                            >
                                <Download className="h-3.5 w-3.5" />
                                Trades
                            </Button>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={onExportJson}
                            >
                                <Download className="h-3.5 w-3.5" />
                                Export JSON
                            </Button>
                            <Button
                                onClick={onSaveExperiment}
                                disabled={
                                    saveExperimentIsPending ||
                                    !canSaveExperiment
                                }
                                className="bg-gradient-to-r from-emerald-600 to-emerald-500 font-medium text-white shadow-lg shadow-emerald-500/20"
                            >
                                {saveExperimentIsPending
                                    ? "Saving..."
                                    : "Save Experiment"}
                            </Button>
                        </>
                    ) : null}
                </>
            }
        />
    );
}
