"use client";

import { toast } from "sonner";
import {
    buildBacktestRequestPayload,
    buildComparisonBacktestRequest,
} from "@/app/backtesting/backtesting-request-builder";
import type {
    BacktestCostAssumptions,
    BacktestRequest,
    MissingDataPolicy,
    OneTimeCashflowEvent,
    RecurringCashflowRule,
} from "@/types/api";
import type {
    ComparisonPortfolio,
    PortfolioAsset,
} from "@/stores/backtest-store";

interface UseBacktestingRequestBuildersArgs {
    params: Record<string, number>;
    costAssumptions: BacktestCostAssumptions;
    recurringContribution: number;
    contributionFrequency: RecurringCashflowRule["frequency"];
    recurringWithdrawal: number;
    withdrawalFrequency: RecurringCashflowRule["frequency"];
    startDate: string;
    endDate: string;
    oneTimeCashflows: OneTimeCashflowEvent[];
    isAllocationStrategy: boolean;
    portfolioAssets: PortfolioAsset[];
    strategy: string;
    ticker: string;
    altTicker: string;
    needsMultiAsset: boolean | undefined;
    cash: number;
    benchmarkTicker: string;
    riskFreeRate: number;
    inflationRate: number;
    missingDataPolicy: MissingDataPolicy;
}

export function useBacktestingRequestBuilders({
    params,
    costAssumptions,
    recurringContribution,
    contributionFrequency,
    recurringWithdrawal,
    withdrawalFrequency,
    startDate,
    endDate,
    oneTimeCashflows,
    isAllocationStrategy,
    portfolioAssets,
    strategy,
    ticker,
    altTicker,
    needsMultiAsset,
    cash,
    benchmarkTicker,
    riskFreeRate,
    inflationRate,
    missingDataPolicy,
}: UseBacktestingRequestBuildersArgs) {
    const buildBacktestRequest = (): BacktestRequest | null => {
        const requestResult = buildBacktestRequestPayload({
            params,
            costAssumptions,
            recurringContribution,
            contributionFrequency,
            recurringWithdrawal,
            withdrawalFrequency,
            startDate,
            endDate,
            oneTimeCashflows,
            isAllocationStrategy,
            portfolioAssets,
            strategy,
            ticker,
            altTicker,
            needsMultiAsset,
            cash,
            benchmarkTicker,
            riskFreeRate,
            inflationRate,
            missingDataPolicy,
        });
        if (requestResult.error) {
            toast.error(requestResult.error);
            return null;
        }

        return requestResult.request;
    };

    const buildComparisonRequest = (
        portfolio: ComparisonPortfolio,
        baseRequest: BacktestRequest,
    ): BacktestRequest =>
        buildComparisonBacktestRequest({ portfolio, baseRequest, params });

    return {
        buildBacktestRequest,
        buildComparisonRequest,
    };
}
