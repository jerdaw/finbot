"use client";

import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { apiPost } from "@/lib/api";
import type {
    BacktestRequest,
    BacktestResponse,
    SaveExperimentRequest,
    SaveExperimentResponse,
} from "@/types/api";
import type {
    BacktestState,
    ComparisonPortfolio,
    ComparisonRun,
} from "@/stores/backtest-store";

interface UseBacktestingMutationsArgs {
    buildBacktestRequest: () => BacktestRequest | null;
    buildComparisonRequest: (
        portfolio: ComparisonPortfolio,
        baseRequest: BacktestRequest,
    ) => BacktestRequest;
    setLastRunRequest: BacktestState["setLastRunRequest"];
    setLastComparisonRequest: BacktestState["setLastComparisonRequest"];
    setSavedExperiment: BacktestState["setSavedExperiment"];
    setComparisonRuns: BacktestState["setComparisonRuns"];
    setActiveResultTab: BacktestState["setActiveResultTab"];
}

export function useBacktestingMutations({
    buildBacktestRequest,
    buildComparisonRequest,
    setLastRunRequest,
    setLastComparisonRequest,
    setSavedExperiment,
    setComparisonRuns,
    setActiveResultTab,
}: UseBacktestingMutationsArgs) {
    const mutation = useMutation({
        mutationFn: (req: BacktestRequest) =>
            apiPost<BacktestResponse>("/api/backtesting/run", req, 120000),
        onSuccess: (_data, variables) => {
            setLastRunRequest(variables);
            setSavedExperiment(null);
            toast.success("Backtest complete");
        },
        onError: (e) => toast.error(`Backtest failed: ${e.message}`),
    });

    const saveExperimentMutation = useMutation({
        mutationFn: (req: SaveExperimentRequest) =>
            apiPost<SaveExperimentResponse>("/api/experiments/save", req),
        onSuccess: (data) => {
            setSavedExperiment(data);
            toast.success("Experiment saved");
        },
        onError: (e) => toast.error(`Save failed: ${e.message}`),
    });

    const comparisonMutation = useMutation({
        mutationFn: async (portfolios: ComparisonPortfolio[]) => {
            const baseRequest = buildBacktestRequest();
            if (!baseRequest) {
                throw new Error(
                    "Fix the current run configuration before comparing portfolios.",
                );
            }

            const runs = await Promise.all(
                portfolios.map(async (portfolio): Promise<ComparisonRun> => {
                    const request = buildComparisonRequest(
                        portfolio,
                        baseRequest,
                    );
                    try {
                        const comparisonResult = await apiPost<BacktestResponse>(
                            "/api/backtesting/run",
                            request,
                            120000,
                        );
                        return {
                            portfolio,
                            request,
                            result: comparisonResult,
                        };
                    } catch (error) {
                        return {
                            portfolio,
                            request,
                            result: null,
                            error:
                                error instanceof Error
                                    ? error.message
                                    : "Comparison run failed",
                        };
                    }
                }),
            );
            return runs;
        },
        onSuccess: (runs) => {
            setComparisonRuns(runs);
            const firstRequest = runs.find((run) => run.request)?.request;
            if (firstRequest) {
                setLastComparisonRequest(firstRequest);
            }
            const failed = runs.filter((run) => run.error).length;
            if (failed > 0) {
                toast.error(
                    `${failed} comparison run${failed === 1 ? "" : "s"} failed`,
                );
            } else {
                toast.success("Comparison complete");
            }
            setActiveResultTab("comparison");
        },
        onError: (e) => toast.error(`Comparison failed: ${e.message}`),
    });

    return {
        mutation,
        saveExperimentMutation,
        comparisonMutation,
    };
}
