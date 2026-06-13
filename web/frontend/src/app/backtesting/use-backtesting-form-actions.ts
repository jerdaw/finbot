"use client";

import {
    STRATEGY_FALLBACK_PARAMS,
} from "@/app/backtesting/backtesting-options";
import type { BacktestState } from "@/stores/backtest-store";
import {
    DEFAULT_COST_ASSUMPTIONS,
} from "@/stores/backtest-store";
import type {
    BacktestCostAssumptions,
    BacktestRequest,
    OneTimeCashflowEvent,
    StrategyInfo,
} from "@/types/api";

interface UseBacktestingFormActionsArgs {
    strategies: StrategyInfo[] | undefined;
    startDate: string;
    endDate: string;
    setTicker: BacktestState["setTicker"];
    setAltTicker: BacktestState["setAltTicker"];
    setPortfolioAssets: BacktestState["setPortfolioAssets"];
    setStrategy: BacktestState["setStrategy"];
    setStartDate: BacktestState["setStartDate"];
    setEndDate: BacktestState["setEndDate"];
    setCash: BacktestState["setCash"];
    setBenchmarkTicker: BacktestState["setBenchmarkTicker"];
    setRiskFreeRate: BacktestState["setRiskFreeRate"];
    setRecurringContribution: BacktestState["setRecurringContribution"];
    setContributionFrequency: BacktestState["setContributionFrequency"];
    setRecurringWithdrawal: BacktestState["setRecurringWithdrawal"];
    setWithdrawalFrequency: BacktestState["setWithdrawalFrequency"];
    setInflationRate: BacktestState["setInflationRate"];
    setOneTimeCashflows: BacktestState["setOneTimeCashflows"];
    setMissingDataPolicy: BacktestState["setMissingDataPolicy"];
    setCostAssumptions: BacktestState["setCostAssumptions"];
    setParams: BacktestState["setParams"];
}

export function useBacktestingFormActions({
    strategies,
    startDate,
    endDate,
    setTicker,
    setAltTicker,
    setPortfolioAssets,
    setStrategy,
    setStartDate,
    setEndDate,
    setCash,
    setBenchmarkTicker,
    setRiskFreeRate,
    setRecurringContribution,
    setContributionFrequency,
    setRecurringWithdrawal,
    setWithdrawalFrequency,
    setInflationRate,
    setOneTimeCashflows,
    setMissingDataPolicy,
    setCostAssumptions,
    setParams,
}: UseBacktestingFormActionsArgs) {
    const applyStrategy = (name: string) => {
        setStrategy(name);
        const selectedStrategy = strategies?.find(
            (candidate) => candidate.name === name,
        );
        if (selectedStrategy) {
            const defaults: Record<string, number> = {};
            selectedStrategy.params.forEach((param) => {
                defaults[param.name] = param.default as number;
            });
            setParams(defaults);
            return;
        }
        setParams(STRATEGY_FALLBACK_PARAMS[name] ?? {});
    };

    const updateCostAssumption = <K extends keyof BacktestCostAssumptions>(
        key: K,
        value: BacktestCostAssumptions[K],
    ) => {
        setCostAssumptions((current) => ({
            ...current,
            [key]: value,
        }));
    };

    const updateOneTimeCashflow = (
        index: number,
        patch: Partial<OneTimeCashflowEvent>,
    ) => {
        setOneTimeCashflows((current) =>
            current.map((event, eventIndex) =>
                eventIndex === index ? { ...event, ...patch } : event,
            ),
        );
    };

    const addOneTimeCashflow = () => {
        setOneTimeCashflows((current) => [
            ...current,
            { date: startDate, amount: 0, label: "" },
        ]);
    };

    const removeOneTimeCashflow = (index: number) => {
        setOneTimeCashflows((current) =>
            current.filter((_, eventIndex) => eventIndex !== index),
        );
    };

    const applyBacktestRequestToForm = (request: BacktestRequest) => {
        setStrategy(request.strategy);
        setStartDate(request.start_date ?? startDate);
        setEndDate(request.end_date ?? endDate);
        setCash(request.initial_cash);
        setBenchmarkTicker(request.benchmark_ticker ?? "");
        setRiskFreeRate(request.risk_free_rate ?? 0.04);
        setMissingDataPolicy(request.missing_data_policy ?? "forward_fill");
        setCostAssumptions(request.cost_assumptions ?? DEFAULT_COST_ASSUMPTIONS);
        const contributionRule = request.recurring_cashflows?.find(
            (rule) => rule.amount > 0,
        );
        const withdrawalRule = request.recurring_cashflows?.find(
            (rule) => rule.amount < 0,
        );
        setRecurringContribution(contributionRule?.amount ?? 0);
        if (contributionRule?.frequency) {
            setContributionFrequency(contributionRule.frequency);
        }
        setRecurringWithdrawal(Math.abs(withdrawalRule?.amount ?? 0));
        if (withdrawalRule?.frequency) {
            setWithdrawalFrequency(withdrawalRule.frequency);
        }
        setOneTimeCashflows(request.one_time_cashflows ?? []);
        setInflationRate(request.inflation_rate ?? 0.03);

        if (
            request.strategy === "NoRebalance" ||
            request.strategy === "Rebalance"
        ) {
            const proportions =
                request.strategy === "NoRebalance"
                    ? request.strategy_params.equity_proportions
                    : request.strategy_params.rebal_proportions;
            const weights = Array.isArray(proportions)
                ? proportions.map((value) => Number(value) * 100)
                : request.tickers.map(() =>
                      Number((100 / request.tickers.length).toFixed(2)),
                  );
            setPortfolioAssets(
                request.tickers.map((requestTicker, index) => ({
                    ticker: requestTicker,
                    weight: weights[index] ?? 0,
                })),
            );
        } else {
            setTicker(request.tickers[0] ?? "SPY");
            setAltTicker(request.tickers[1] ?? "TLT");
        }

        setParams(
            Object.fromEntries(
                Object.entries(request.strategy_params ?? {}).filter(
                    ([, value]) => typeof value === "number",
                ),
            ) as Record<string, number>,
        );
    };

    return {
        applyStrategy,
        updateCostAssumption,
        updateOneTimeCashflow,
        addOneTimeCashflow,
        removeOneTimeCashflow,
        applyBacktestRequestToForm,
    };
}
