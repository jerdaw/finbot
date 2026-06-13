import { STRATEGY_FALLBACK_PARAMS } from "@/app/backtesting/backtesting-options";
import { cloneAssets } from "@/lib/backtest-utils";
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

interface BuildBacktestRequestArgs {
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

type BuildBacktestRequestResult =
    | { request: BacktestRequest; error: null }
    | { request: null; error: string };

function invalid(error: string): BuildBacktestRequestResult {
    return { request: null, error };
}

export function buildBacktestRequestPayload({
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
}: BuildBacktestRequestArgs): BuildBacktestRequestResult {
    const strategyParams: Record<string, unknown> = { ...params };
    let tickers: string[] = [];
    const recurringCashflows: RecurringCashflowRule[] = [];
    const normalizedCostAssumptions: BacktestCostAssumptions = {
        ...costAssumptions,
        commission_per_share: Number(costAssumptions.commission_per_share),
        commission_bps: Number(costAssumptions.commission_bps),
        commission_minimum: Number(costAssumptions.commission_minimum),
        spread_bps: Number(costAssumptions.spread_bps),
        slippage_bps: Number(costAssumptions.slippage_bps),
    };

    if (
        Object.values(normalizedCostAssumptions)
            .filter((value) => typeof value === "number")
            .some(
                (value) =>
                    !Number.isFinite(value as number) ||
                    (value as number) < 0,
            )
    ) {
        return invalid("Cost assumptions must be finite, non-negative numbers.");
    }
    if (
        normalizedCostAssumptions.commission_mode === "per_share" &&
        normalizedCostAssumptions.commission_per_share <= 0
    ) {
        return invalid("Per-share commission must be greater than 0.");
    }
    if (
        normalizedCostAssumptions.commission_mode === "percentage" &&
        normalizedCostAssumptions.commission_bps <= 0
    ) {
        return invalid("Percentage commission must be greater than 0 bps.");
    }

    if (recurringContribution > 0) {
        recurringCashflows.push({
            amount: recurringContribution,
            frequency: contributionFrequency,
            start_date: startDate,
            end_date: endDate,
            label: `Recurring contribution (${contributionFrequency})`,
        });
    }
    if (recurringWithdrawal > 0) {
        recurringCashflows.push({
            amount: -recurringWithdrawal,
            frequency: withdrawalFrequency,
            start_date: startDate,
            end_date: endDate,
            label: `Recurring withdrawal (${withdrawalFrequency})`,
        });
    }

    const normalizedOneTimeCashflows = oneTimeCashflows
        .filter(
            (event) =>
                event.date.trim().length > 0 ||
                event.amount !== 0 ||
                (event.label?.trim().length ?? 0) > 0,
        )
        .map((event) => ({
            date: event.date.trim(),
            amount: Number(event.amount),
            label: event.label?.trim() || undefined,
        }));

    for (const event of normalizedOneTimeCashflows) {
        if (!event.date) {
            return invalid("Each one-time cashflow needs an applied date.");
        }
        if (!Number.isFinite(event.amount) || event.amount === 0) {
            return invalid("Each one-time cashflow needs a non-zero amount.");
        }
    }

    if (isAllocationStrategy) {
        const cleanedAssets = portfolioAssets
            .map((asset) => ({
                ticker: asset.ticker.trim().toUpperCase(),
                weight: asset.weight,
            }))
            .filter((asset) => asset.ticker.length > 0);

        if (cleanedAssets.length === 0) {
            return invalid(
                "Add at least one asset before running the allocation backtest.",
            );
        }
        if (cleanedAssets.some((asset) => asset.weight <= 0)) {
            return invalid("Allocation weights must be greater than 0%.");
        }
        if (
            new Set(cleanedAssets.map((asset) => asset.ticker)).size !==
            cleanedAssets.length
        ) {
            return invalid("Each asset ticker must be unique.");
        }

        const totalWeight = cleanedAssets.reduce(
            (total, asset) => total + asset.weight,
            0,
        );
        if (Math.abs(totalWeight - 100) > 0.1) {
            return invalid("Allocation weights must add up to 100%.");
        }

        tickers = cleanedAssets.map((asset) => asset.ticker);
        const normalizedWeights = cleanedAssets.map(
            (asset) => asset.weight / 100,
        );
        if (strategy === "NoRebalance") {
            strategyParams.equity_proportions = normalizedWeights;
        }
        if (strategy === "Rebalance") {
            strategyParams.rebal_proportions = normalizedWeights;
        }
    } else {
        const primaryTicker = ticker.trim().toUpperCase();
        if (!primaryTicker) {
            return invalid("Enter an asset ticker before running the backtest.");
        }

        tickers = [primaryTicker];
        if (needsMultiAsset) {
            const secondaryTicker = altTicker.trim().toUpperCase();
            if (!secondaryTicker) {
                return invalid(
                    "Enter a second asset for the selected strategy.",
                );
            }
            if (secondaryTicker === primaryTicker) {
                return invalid(
                    "Use two distinct assets for the selected strategy.",
                );
            }
            tickers = [primaryTicker, secondaryTicker];
        }
    }

    return {
        request: {
            tickers,
            strategy,
            strategy_params: strategyParams,
            start_date: startDate,
            end_date: endDate,
            initial_cash: cash,
            benchmark_ticker: benchmarkTicker.trim()
                ? benchmarkTicker.trim().toUpperCase()
                : undefined,
            risk_free_rate: riskFreeRate,
            recurring_cashflows:
                recurringCashflows.length > 0 ? recurringCashflows : undefined,
            one_time_cashflows:
                normalizedOneTimeCashflows.length > 0
                    ? normalizedOneTimeCashflows
                    : undefined,
            inflation_rate: inflationRate,
            missing_data_policy: missingDataPolicy,
            cost_assumptions: normalizedCostAssumptions,
        },
        error: null,
    };
}

export function buildComparisonBacktestRequest({
    portfolio,
    baseRequest,
    params,
}: {
    portfolio: ComparisonPortfolio;
    baseRequest: BacktestRequest;
    params: Record<string, number>;
}): BacktestRequest {
    const cleanedAssets = cloneAssets(portfolio.assets).filter(
        (asset) => asset.ticker.length > 0,
    );
    const weights = cleanedAssets.map((asset) => asset.weight / 100);
    const strategyParams: Record<string, unknown> = {};

    if (portfolio.strategy === "NoRebalance") {
        strategyParams.equity_proportions = weights;
    } else {
        strategyParams.rebal_proportions = weights;
        strategyParams.rebal_interval =
            typeof portfolio.strategyParams?.rebal_interval === "number"
                ? portfolio.strategyParams.rebal_interval
                : typeof params.rebal_interval === "number"
                  ? params.rebal_interval
                  : STRATEGY_FALLBACK_PARAMS.Rebalance.rebal_interval;
    }

    return {
        ...baseRequest,
        tickers: cleanedAssets.map((asset) => asset.ticker),
        strategy: portfolio.strategy,
        strategy_params: strategyParams,
    };
}
