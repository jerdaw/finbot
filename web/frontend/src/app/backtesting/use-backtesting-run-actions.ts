"use client";

import { useEffect } from "react";
import { toast } from "sonner";
import {
    decodeSharedConfig,
    encodeSharedConfig,
} from "@/lib/backtest-utils";
import type {
    BacktestRequest,
    BacktestResponse,
    SaveExperimentRequest,
} from "@/types/api";

interface UseBacktestingRunActionsArgs {
    buildBacktestRequest: () => BacktestRequest | null;
    runBacktest: (request: BacktestRequest) => void;
    saveExperiment: (request: SaveExperimentRequest) => void;
    result: BacktestResponse | undefined;
    lastRunRequest: BacktestRequest | null;
    applyBacktestRequestToForm: (request: BacktestRequest) => void;
}

export function useBacktestingRunActions({
    buildBacktestRequest,
    runBacktest,
    saveExperiment,
    result,
    lastRunRequest,
    applyBacktestRequestToForm,
}: UseBacktestingRunActionsArgs) {
    const handleRun = () => {
        const request = buildBacktestRequest();
        if (!request) {
            return;
        }
        runBacktest(request);
    };

    const handleShareConfig = async () => {
        const request = buildBacktestRequest();
        if (!request) {
            return;
        }

        const url = new URL(window.location.href);
        url.searchParams.set("config", encodeSharedConfig(request));
        window.history.replaceState(null, "", url.toString());

        try {
            await navigator.clipboard.writeText(url.toString());
            toast.success("Share link copied");
        } catch {
            toast.success("Share link added to the address bar");
        }
    };

    useEffect(() => {
        const encodedConfig = new URLSearchParams(window.location.search).get(
            "config",
        );
        if (encodedConfig) {
            const sharedRequest = decodeSharedConfig(encodedConfig);
            if (sharedRequest) {
                applyBacktestRequestToForm(sharedRequest);
                toast.success("Shared backtest configuration loaded");
            }
        }
        // Shared links should hydrate only once.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const handleSaveExperiment = () => {
        if (!result?.stats || !lastRunRequest) {
            toast.error("Run a backtest before saving an experiment.");
            return;
        }

        saveExperiment({
            ...lastRunRequest,
            stats: result.stats,
        });
    };

    return {
        handleRun,
        handleShareConfig,
        handleSaveExperiment,
    };
}
