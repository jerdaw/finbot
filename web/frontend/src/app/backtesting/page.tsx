"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { LightweightChart } from "@/components/charts/lightweight-chart";
import { DrawdownChart } from "@/components/charts/drawdown-chart";
import { LineChartWrapper } from "@/components/charts/line-chart-wrapper";
import { DataTable } from "@/components/common/data-table";
import { StatCard } from "@/components/common/stat-card";
import { PageHeader } from "@/components/common/page-header";
import { ConfigPanel } from "@/components/common/config-panel";
import { ChartCard } from "@/components/common/chart-card";
import { ToolLayout } from "@/components/common/tool-layout";
import { EmptyState } from "@/components/common/empty-state";
import { InlineError } from "@/components/common/inline-error";
import {
    ChartSkeleton,
    CardSkeleton,
} from "@/components/common/loading-skeleton";
import { Activity, Plus, Trash2 } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";
import {
    formatPercent,
    formatNumber,
    formatCurrencyPrecise,
} from "@/lib/format";
import { cn } from "@/lib/utils";
import type {
    AppliedBacktestCostAssumptions,
    StrategyInfo,
    BacktestCostAssumptions,
    BacktestCostSummary,
    BacktestRequest,
    BacktestBenchmarkStats,
    BacktestMissingDataSummary,
    CashflowEventRecord,
    BacktestRegimePeriod,
    BacktestRegimeSummary,
    BacktestResponse,
    MissingDataPolicy,
    OneTimeCashflowEvent,
    RebalanceEventRecord,
    RecurringCashflowRule,
    ReturnTableRow,
    RollingMetricsResponse,
    SaveExperimentRequest,
    SaveExperimentResponse,
    WithdrawalDurabilitySummary,
    WalkForwardHandoff,
} from "@/types/api";

interface PortfolioAsset {
    ticker: string;
    weight: number;
}

interface PortfolioPreset {
    label: string;
    strategy: "NoRebalance" | "Rebalance";
    assets: PortfolioAsset[];
}

const DEFAULT_PORTFOLIO_ASSETS: PortfolioAsset[] = [
    { ticker: "SPY", weight: 100 },
];

const PORTFOLIO_PRESETS: PortfolioPreset[] = [
    {
        label: "SPY Buy & Hold",
        strategy: "NoRebalance",
        assets: [{ ticker: "SPY", weight: 100 }],
    },
    {
        label: "60/40",
        strategy: "Rebalance",
        assets: [
            { ticker: "SPY", weight: 60 },
            { ticker: "TLT", weight: 40 },
        ],
    },
    {
        label: "Three-Fund",
        strategy: "Rebalance",
        assets: [
            { ticker: "VTI", weight: 50 },
            { ticker: "VXUS", weight: 30 },
            { ticker: "BND", weight: 20 },
        ],
    },
    {
        label: "All Weather",
        strategy: "Rebalance",
        assets: [
            { ticker: "SPY", weight: 30 },
            { ticker: "TLT", weight: 40 },
            { ticker: "IEF", weight: 15 },
            { ticker: "GLD", weight: 7.5 },
            { ticker: "DBC", weight: 7.5 },
        ],
    },
    {
        label: "Golden Butterfly",
        strategy: "Rebalance",
        assets: [
            { ticker: "SPY", weight: 20 },
            { ticker: "IJS", weight: 20 },
            { ticker: "TLT", weight: 20 },
            { ticker: "SHY", weight: 20 },
            { ticker: "GLD", weight: 20 },
        ],
    },
];

const STRATEGY_FALLBACK_PARAMS: Record<string, Record<string, number>> = {
    Rebalance: { rebal_interval: 63 },
    SMACrossover: { fast_ma: 50, slow_ma: 200 },
};

const CASHFLOW_FREQUENCY_OPTIONS = [
    { label: "Monthly", value: "monthly" },
    { label: "Quarterly", value: "quarterly" },
    { label: "Yearly", value: "yearly" },
] as const;

const MISSING_DATA_POLICY_OPTIONS: Array<{
    label: string;
    value: MissingDataPolicy;
    description: string;
}> = [
    {
        label: "Forward Fill",
        value: "forward_fill",
        description: "Carry the last observed price across gaps.",
    },
    {
        label: "Drop Gaps",
        value: "drop",
        description: "Remove dates that still contain missing values.",
    },
    {
        label: "Error",
        value: "error",
        description:
            "Fail fast when a selected series contains missing values.",
    },
    {
        label: "Interpolate",
        value: "interpolate",
        description:
            "Linearly interpolate missing prices between observations.",
    },
    {
        label: "Backfill",
        value: "backfill",
        description:
            "Use the next observed price. This can introduce look-ahead bias.",
    },
];

const COMMISSION_MODE_OPTIONS = [
    { label: "None", value: "none" },
    { label: "Per Share", value: "per_share" },
    { label: "Percentage", value: "percentage" },
] as const;

const DEFAULT_COST_ASSUMPTIONS: BacktestCostAssumptions = {
    commission_mode: "none",
    commission_per_share: 0.001,
    commission_bps: 1,
    commission_minimum: 0,
    spread_bps: 0,
    slippage_bps: 0,
};

function getMetricTrend(
    value: number | null | undefined,
): "up" | "down" | "neutral" {
    if (value == null) {
        return "neutral";
    }
    return value > 0 ? "up" : value < 0 ? "down" : "neutral";
}

function formatBenchmarkValue(
    value: number | null | undefined,
    formatter: (value: number | null | undefined) => string,
): string {
    return value == null ? "N/A" : formatter(value);
}

function downloadFile(
    content: string,
    fileName: string,
    mimeType: string,
): void {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = fileName;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
}

function escapeCsvValue(value: unknown): string {
    if (value == null) {
        return "";
    }

    const normalized = String(value).replace(/"/g, '""');
    return /[",\n]/.test(normalized) ? `"${normalized}"` : normalized;
}

function buildCsv(
    rows: Array<Record<string, unknown>>,
    columns: string[],
): string {
    const header = columns.join(",");
    const body = rows.map((row) =>
        columns.map((column) => escapeCsvValue(row[column])).join(","),
    );
    return [header, ...body].join("\n");
}

function buildExportBaseName(request: BacktestRequest | null): string {
    if (!request) {
        return "finbot-backtest";
    }

    const slug = [request.strategy, ...request.tickers]
        .join("-")
        .toLowerCase()
        .replace(/[^a-z0-9-]+/g, "-")
        .replace(/-+/g, "-")
        .replace(/^-|-$/g, "");

    return slug ? `finbot-${slug}` : "finbot-backtest";
}

function buildWalkForwardHref(
    request: WalkForwardHandoff | null | undefined,
): string {
    if (!request) {
        return "/walk-forward";
    }

    const params = new URLSearchParams();
    params.set("tickers", request.tickers.join(","));
    params.set("strategy", request.strategy);
    params.set("start_date", request.start_date);
    params.set("end_date", request.end_date);
    params.set("initial_cash", String(request.initial_cash));
    params.set("train_window", String(request.train_window));
    params.set("test_window", String(request.test_window));
    params.set("step_size", String(request.step_size));
    params.set("anchored", String(request.anchored));
    params.set("include_train", String(request.include_train));
    if (Object.keys(request.strategy_params).length > 0) {
        params.set("strategy_params", JSON.stringify(request.strategy_params));
    }
    return `/walk-forward?${params.toString()}`;
}

export default function BacktestingPage() {
    const [ticker, setTicker] = useState("SPY");
    const [altTicker, setAltTicker] = useState("TLT");
    const [portfolioAssets, setPortfolioAssets] = useState<PortfolioAsset[]>(
        DEFAULT_PORTFOLIO_ASSETS,
    );
    const [strategy, setStrategy] = useState("NoRebalance");
    const [startDate, setStartDate] = useState("2015-01-01");
    const [endDate, setEndDate] = useState("2024-12-31");
    const [cash, setCash] = useState(10000);
    const [benchmarkTicker, setBenchmarkTicker] = useState("");
    const [riskFreeRate, setRiskFreeRate] = useState(0.04);
    const [recurringContribution, setRecurringContribution] = useState(0);
    const [contributionFrequency, setContributionFrequency] =
        useState<RecurringCashflowRule["frequency"]>("monthly");
    const [recurringWithdrawal, setRecurringWithdrawal] = useState(0);
    const [withdrawalFrequency, setWithdrawalFrequency] =
        useState<RecurringCashflowRule["frequency"]>("monthly");
    const [inflationRate, setInflationRate] = useState(0.03);
    const [oneTimeCashflows, setOneTimeCashflows] = useState<
        OneTimeCashflowEvent[]
    >([]);
    const [missingDataPolicy, setMissingDataPolicy] =
        useState<MissingDataPolicy>("forward_fill");
    const [costAssumptions, setCostAssumptions] =
        useState<BacktestCostAssumptions>(DEFAULT_COST_ASSUMPTIONS);
    const [params, setParams] = useState<Record<string, number>>({});
    const [lastRunRequest, setLastRunRequest] =
        useState<BacktestRequest | null>(null);
    const [savedExperiment, setSavedExperiment] =
        useState<SaveExperimentResponse | null>(null);

    const { data: strategies } = useQuery({
        queryKey: ["strategies"],
        queryFn: () => apiGet<StrategyInfo[]>("/api/backtesting/strategies"),
    });

    const currentStrategy = strategies?.find((s) => s.name === strategy);
    const isAllocationStrategy =
        strategy === "NoRebalance" || strategy === "Rebalance";
    const needsMultiAsset =
        !isAllocationStrategy &&
        currentStrategy &&
        currentStrategy.min_assets > 1;
    const allocationWeightTotal = portfolioAssets.reduce(
        (total, asset) => total + asset.weight,
        0,
    );
    const allocationIsBalanced =
        Math.abs(allocationWeightTotal - 100) <= 0.1 &&
        portfolioAssets.every(
            (asset) => asset.weight > 0 && asset.ticker.trim().length > 0,
        );

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

    const applyPortfolioPreset = (preset: PortfolioPreset) => {
        applyStrategy(preset.strategy);
        setPortfolioAssets(preset.assets.map((asset) => ({ ...asset })));
    };

    const updatePortfolioTicker = (index: number, value: string) => {
        setPortfolioAssets((current) =>
            current.map((asset, assetIndex) =>
                assetIndex === index ? { ...asset, ticker: value } : asset,
            ),
        );
    };

    const updatePortfolioWeight = (index: number, value: string) => {
        const nextWeight = Number(value);
        setPortfolioAssets((current) =>
            current.map((asset, assetIndex) =>
                assetIndex === index
                    ? {
                          ...asset,
                          weight: Number.isFinite(nextWeight) ? nextWeight : 0,
                      }
                    : asset,
            ),
        );
    };

    const addPortfolioAsset = () => {
        setPortfolioAssets((current) => [
            ...current,
            { ticker: "", weight: 0 },
        ]);
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

    const removePortfolioAsset = (index: number) => {
        setPortfolioAssets((current) => {
            if (current.length === 1) {
                return current;
            }
            return current.filter((_, assetIndex) => assetIndex !== index);
        });
    };

    const equalizePortfolioWeights = () => {
        setPortfolioAssets((current) => {
            if (current.length === 0) {
                return current;
            }

            const evenWeight = Number((100 / current.length).toFixed(2));
            const finalWeight = Number(
                (100 - evenWeight * (current.length - 1)).toFixed(2),
            );
            return current.map((asset, assetIndex) => ({
                ...asset,
                weight:
                    assetIndex === current.length - 1
                        ? finalWeight
                        : evenWeight,
            }));
        });
    };

    const buildBacktestRequest = (): BacktestRequest | null => {
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
            toast.error(
                "Cost assumptions must be finite, non-negative numbers.",
            );
            return null;
        }
        if (
            normalizedCostAssumptions.commission_mode === "per_share" &&
            normalizedCostAssumptions.commission_per_share <= 0
        ) {
            toast.error("Per-share commission must be greater than 0.");
            return null;
        }
        if (
            normalizedCostAssumptions.commission_mode === "percentage" &&
            normalizedCostAssumptions.commission_bps <= 0
        ) {
            toast.error("Percentage commission must be greater than 0 bps.");
            return null;
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
                toast.error("Each one-time cashflow needs an applied date.");
                return null;
            }
            if (!Number.isFinite(event.amount) || event.amount === 0) {
                toast.error("Each one-time cashflow needs a non-zero amount.");
                return null;
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
                toast.error(
                    "Add at least one asset before running the allocation backtest.",
                );
                return null;
            }
            if (cleanedAssets.some((asset) => asset.weight <= 0)) {
                toast.error("Allocation weights must be greater than 0%.");
                return null;
            }
            if (
                new Set(cleanedAssets.map((asset) => asset.ticker)).size !==
                cleanedAssets.length
            ) {
                toast.error("Each asset ticker must be unique.");
                return null;
            }

            const totalWeight = cleanedAssets.reduce(
                (total, asset) => total + asset.weight,
                0,
            );
            if (Math.abs(totalWeight - 100) > 0.1) {
                toast.error("Allocation weights must add up to 100%.");
                return null;
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
                toast.error(
                    "Enter an asset ticker before running the backtest.",
                );
                return null;
            }

            tickers = [primaryTicker];
            if (needsMultiAsset) {
                const secondaryTicker = altTicker.trim().toUpperCase();
                if (!secondaryTicker) {
                    toast.error(
                        "Enter a second asset for the selected strategy.",
                    );
                    return null;
                }
                if (secondaryTicker === primaryTicker) {
                    toast.error(
                        "Use two distinct assets for the selected strategy.",
                    );
                    return null;
                }
                tickers = [primaryTicker, secondaryTicker];
            }
        }

        return {
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
        };
    };

    const handleRun = () => {
        const request = buildBacktestRequest();
        if (!request) {
            return;
        }
        mutation.mutate(request);
    };

    const handleSaveExperiment = () => {
        if (!result?.stats || !lastRunRequest) {
            toast.error("Run a backtest before saving an experiment.");
            return;
        }

        saveExperimentMutation.mutate({
            ...lastRunRequest,
            stats: result.stats,
        });
    };

    const handleExportJson = () => {
        if (!result) {
            toast.error("Run a backtest before exporting results.");
            return;
        }

        downloadFile(
            JSON.stringify(
                {
                    request: lastRunRequest,
                    result,
                    saved_experiment: savedExperiment,
                },
                null,
                2,
            ),
            `${buildExportBaseName(lastRunRequest)}-run.json`,
            "application/json;charset=utf-8",
        );
        toast.success("Backtest JSON exported");
    };

    const handleExportCsv = () => {
        if (!result?.value_history || result.value_history.length === 0) {
            toast.error("Run a backtest before exporting results.");
            return;
        }

        const benchmarkByDate = new Map(
            benchmarkValueHistory.map((row) => [
                String(row.date ?? row.index ?? ""),
                row.Value ?? null,
            ]),
        );
        const realByDate = new Map(
            realValueHistory.map((row) => [
                String(row.date ?? row.index ?? ""),
                row.Value ?? null,
            ]),
        );
        const rollingByDate = new Map(
            (rollingMetrics?.dates ?? []).map((date, index) => [
                date,
                {
                    sharpe: rollingMetrics?.sharpe[index] ?? null,
                    volatility: rollingMetrics?.volatility[index] ?? null,
                    beta: rollingMetrics?.beta?.[index] ?? null,
                },
            ]),
        );

        const rows = result.value_history.map((row) => {
            const date = String(row.date ?? row.index ?? "");
            const rolling = rollingByDate.get(date);
            return {
                date,
                portfolio_value: row.Value ?? null,
                real_portfolio_value: realByDate.get(date) ?? null,
                benchmark_value: benchmarkByDate.get(date) ?? null,
                rolling_sharpe: rolling?.sharpe ?? null,
                rolling_volatility: rolling?.volatility ?? null,
                rolling_beta: rolling?.beta ?? null,
            };
        });

        downloadFile(
            buildCsv(rows, [
                "date",
                "portfolio_value",
                "real_portfolio_value",
                "benchmark_value",
                "rolling_sharpe",
                "rolling_volatility",
                "rolling_beta",
            ]),
            `${buildExportBaseName(lastRunRequest)}-timeseries.csv`,
            "text/csv;charset=utf-8",
        );
        toast.success("Backtest CSV exported");
    };

    const result = mutation.data;
    const stats = result?.stats;
    const benchmarkStats: BacktestBenchmarkStats | null | undefined =
        result?.benchmark_stats;
    const benchmarkValueHistory = result?.benchmark_value_history ?? [];
    const cashflowEvents: CashflowEventRecord[] = result?.cashflow_events ?? [];
    const realValueHistory = result?.real_value_history ?? [];
    const withdrawalDurability: WithdrawalDurabilitySummary | null | undefined =
        result?.withdrawal_durability;
    const allocationHistory = result?.allocation_history ?? [];
    const rebalanceEvents: RebalanceEventRecord[] =
        result?.rebalance_events ?? [];
    const rollingMetrics: RollingMetricsResponse | null | undefined =
        result?.rolling_metrics;
    const appliedCostAssumptions: AppliedBacktestCostAssumptions | undefined =
        result?.applied_cost_assumptions;
    const costSummary: BacktestCostSummary | null | undefined =
        result?.cost_summary;
    const missingDataSummary: BacktestMissingDataSummary | undefined =
        result?.missing_data_summary;
    const walkForwardRequest: WalkForwardHandoff | null | undefined =
        result?.walk_forward_request;
    const regimeReferenceTicker = result?.regime_reference_ticker;
    const regimeSummary = result?.regime_summary ?? [];
    const regimePeriods = result?.regime_periods ?? [];
    const monthlyReturns = result?.monthly_returns ?? [];
    const annualReturns = result?.annual_returns ?? [];
    const walkForwardHref = buildWalkForwardHref(walkForwardRequest);
    const costBySymbolRows = Object.entries(
        costSummary?.costs_by_symbol ?? {},
    ).map(([tickerSymbol, total]) => ({
        ticker: tickerSymbol,
        total_cost: total,
    }));
    const inflationAdjustedSeries =
        realValueHistory.length > 0
            ? [
                  {
                      name: "Nominal",
                      dates:
                          result?.value_history?.map((r) => String(r.date)) ??
                          [],
                      values:
                          result?.value_history?.map(
                              (r) => r.Value as number,
                          ) ?? [],
                      color: "#2563eb",
                  },
                  {
                      name: "Real",
                      dates: realValueHistory.map((r) => String(r.date)),
                      values: realValueHistory.map((r) => r.Value as number),
                      color: "#f97316",
                  },
              ]
            : [];
    const rollingChartData =
        rollingMetrics?.dates.map((date, index) => ({
            date,
            sharpe: rollingMetrics.sharpe[index],
            volatility: rollingMetrics.volatility[index],
            beta: rollingMetrics.beta?.[index] ?? null,
        })) ?? [];
    const allocationSeriesKeys = Object.keys(allocationHistory[0] ?? {}).filter(
        (key) => key !== "date" && key !== "index",
    );
    const allocationChartData = allocationHistory.map((row) => {
        const chartRow: Record<string, unknown> = {
            date: String(row.date ?? row.index ?? ""),
        };
        allocationSeriesKeys.forEach((key) => {
            const value = row[key];
            chartRow[key] = typeof value === "number" ? value : null;
        });
        return chartRow;
    });
    let targetWeightMap: Record<string, number> = {};
    const noRebalanceWeights =
        lastRunRequest?.strategy_params["equity_proportions"];
    const rebalanceWeights =
        lastRunRequest?.strategy_params["rebal_proportions"];
    if (
        lastRunRequest?.strategy === "NoRebalance" &&
        Array.isArray(noRebalanceWeights)
    ) {
        targetWeightMap = Object.fromEntries(
            lastRunRequest.tickers.map((tickerSymbol, index) => [
                tickerSymbol,
                Number(noRebalanceWeights[index]),
            ]),
        );
    } else if (
        lastRunRequest?.strategy === "Rebalance" &&
        Array.isArray(rebalanceWeights)
    ) {
        targetWeightMap = Object.fromEntries(
            lastRunRequest.tickers.map((tickerSymbol, index) => [
                tickerSymbol,
                Number(rebalanceWeights[index]),
            ]),
        );
    }
    const latestAllocation = allocationHistory[allocationHistory.length - 1];
    const allocationDriftSummary = Object.keys(targetWeightMap).map(
        (tickerSymbol) => {
            const latestWeight = latestAllocation?.[tickerSymbol];
            let maxDrift = 0;
            allocationHistory.forEach((row) => {
                const rowValue = row[tickerSymbol];
                if (typeof rowValue === "number") {
                    maxDrift = Math.max(
                        maxDrift,
                        Math.abs(rowValue - targetWeightMap[tickerSymbol]),
                    );
                }
            });
            return {
                ticker: tickerSymbol,
                target_weight: targetWeightMap[tickerSymbol],
                latest_weight:
                    typeof latestWeight === "number" ? latestWeight : null,
                max_drift: maxDrift,
            };
        },
    );
    const comparisonChartSeries =
        result?.value_history && result.value_history.length > 0
            ? [
                  {
                      name: "Portfolio",
                      dates: result.value_history.map((r) => String(r.date)),
                      values: result.value_history.map(
                          (r) => r.Value as number,
                      ),
                      color: "#3b82f6",
                  },
                  ...(benchmarkStats && benchmarkValueHistory.length > 0
                      ? [
                            {
                                name: benchmarkStats.benchmark_name,
                                dates: benchmarkValueHistory.map((r) =>
                                    String(r.date),
                                ),
                                values: benchmarkValueHistory.map(
                                    (r) => r.Value as number,
                                ),
                                color: "#22c55e",
                            },
                        ]
                      : []),
              ]
            : [];

    return (
        <div className="space-y-8">
            <PageHeader
                title="Strategy Backtester"
                description="Run allocation backtests or trading strategies on historical data"
                actions={
                    result ? (
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
                                onClick={handleExportCsv}
                            >
                                Export CSV
                            </Button>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={handleExportJson}
                            >
                                Export JSON
                            </Button>
                            <Button
                                onClick={handleSaveExperiment}
                                disabled={
                                    saveExperimentMutation.isPending ||
                                    !lastRunRequest
                                }
                                className="bg-gradient-to-r from-emerald-600 to-emerald-500 font-medium text-white shadow-lg shadow-emerald-500/20"
                            >
                                {saveExperimentMutation.isPending
                                    ? "Saving..."
                                    : "Save Experiment"}
                            </Button>
                        </>
                    ) : undefined
                }
            />

            <ToolLayout
                configPanel={
                    <ConfigPanel title="Configuration">
                        <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">
                                Strategy
                            </Label>
                            <Select
                                value={strategy}
                                onValueChange={applyStrategy}
                            >
                                <SelectTrigger className="border-border/50 bg-background/50">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                                    {strategies?.map((s) => (
                                        <SelectItem key={s.name} value={s.name}>
                                            {s.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            {currentStrategy && (
                                <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                                    {currentStrategy.description}
                                </p>
                            )}
                        </div>

                        {isAllocationStrategy ? (
                            <>
                                <div className="space-y-2">
                                    <Label className="text-xs text-muted-foreground">
                                        Preset Portfolios
                                    </Label>
                                    <div className="flex flex-wrap gap-2">
                                        {PORTFOLIO_PRESETS.map((preset) => (
                                            <Button
                                                key={preset.label}
                                                type="button"
                                                variant="outline"
                                                size="xs"
                                                onClick={() =>
                                                    applyPortfolioPreset(preset)
                                                }
                                            >
                                                {preset.label}
                                            </Button>
                                        ))}
                                    </div>
                                    <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                                        Load a canonical allocation, then edit
                                        the tickers and target weights directly.
                                    </p>
                                </div>

                                <div className="space-y-3">
                                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                                        <div>
                                            <Label className="text-xs text-muted-foreground">
                                                Assets and Weights
                                            </Label>
                                            <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                                                Build the allocation on this
                                                page. Total target weight must
                                                equal 100%.
                                            </p>
                                        </div>
                                        <div className="flex flex-wrap items-center gap-2">
                                            <span
                                                className={cn(
                                                    "text-xs font-medium",
                                                    allocationIsBalanced
                                                        ? "text-emerald-600 dark:text-emerald-400"
                                                        : "text-amber-600 dark:text-amber-400",
                                                )}
                                            >
                                                Total{" "}
                                                {formatNumber(
                                                    allocationWeightTotal,
                                                    1,
                                                )}
                                                %
                                            </span>
                                            <Button
                                                type="button"
                                                variant="outline"
                                                size="xs"
                                                onClick={
                                                    equalizePortfolioWeights
                                                }
                                            >
                                                Equal Weight
                                            </Button>
                                            <Button
                                                type="button"
                                                variant="outline"
                                                size="xs"
                                                onClick={addPortfolioAsset}
                                            >
                                                <Plus />
                                                Add Asset
                                            </Button>
                                        </div>
                                    </div>

                                    <div className="space-y-2">
                                        {portfolioAssets.map((asset, index) => (
                                            <div
                                                key={`${asset.ticker}-${index}`}
                                                className="grid grid-cols-[minmax(0,1fr)_96px_auto] gap-2"
                                            >
                                                <Input
                                                    value={asset.ticker}
                                                    onChange={(e) =>
                                                        updatePortfolioTicker(
                                                            index,
                                                            e.target.value,
                                                        )
                                                    }
                                                    placeholder={`Ticker ${index + 1}`}
                                                    className="border-border/50 bg-background/50"
                                                />
                                                <Input
                                                    type="number"
                                                    min={0}
                                                    step={0.1}
                                                    value={asset.weight}
                                                    onChange={(e) =>
                                                        updatePortfolioWeight(
                                                            index,
                                                            e.target.value,
                                                        )
                                                    }
                                                    className="border-border/50 bg-background/50"
                                                    aria-label={`Weight for asset ${index + 1}`}
                                                />
                                                <Button
                                                    type="button"
                                                    variant="ghost"
                                                    size="icon-xs"
                                                    onClick={() =>
                                                        removePortfolioAsset(
                                                            index,
                                                        )
                                                    }
                                                    disabled={
                                                        portfolioAssets.length ===
                                                        1
                                                    }
                                                    aria-label={`Remove asset ${index + 1}`}
                                                >
                                                    <Trash2 />
                                                </Button>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </>
                        ) : (
                            <>
                                <div className="space-y-2">
                                    <Label className="text-xs text-muted-foreground">
                                        Asset
                                    </Label>
                                    <Input
                                        value={ticker}
                                        onChange={(e) =>
                                            setTicker(e.target.value)
                                        }
                                        className="border-border/50 bg-background/50"
                                    />
                                </div>

                                {needsMultiAsset && (
                                    <div className="space-y-2">
                                        <Label className="text-xs text-muted-foreground">
                                            Second Asset
                                        </Label>
                                        <Input
                                            value={altTicker}
                                            onChange={(e) =>
                                                setAltTicker(e.target.value)
                                            }
                                            className="border-border/50 bg-background/50"
                                        />
                                    </div>
                                )}
                            </>
                        )}

                        <div className="grid grid-cols-2 gap-3">
                            <div className="space-y-1.5">
                                <Label className="text-xs text-muted-foreground">
                                    Start
                                </Label>
                                <Input
                                    type="date"
                                    value={startDate}
                                    onChange={(e) =>
                                        setStartDate(e.target.value)
                                    }
                                    className="border-border/50 bg-background/50"
                                />
                            </div>
                            <div className="space-y-1.5">
                                <Label className="text-xs text-muted-foreground">
                                    End
                                </Label>
                                <Input
                                    type="date"
                                    value={endDate}
                                    onChange={(e) => setEndDate(e.target.value)}
                                    className="border-border/50 bg-background/50"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">
                                Initial Cash ($)
                            </Label>
                            <Input
                                type="number"
                                value={cash}
                                onChange={(e) =>
                                    setCash(Number(e.target.value))
                                }
                                className="border-border/50 bg-background/50"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">
                                Benchmark Ticker
                            </Label>
                            <Input
                                value={benchmarkTicker}
                                onChange={(e) =>
                                    setBenchmarkTicker(e.target.value)
                                }
                                placeholder="Leave blank to skip benchmark analysis"
                                className="border-border/50 bg-background/50"
                            />
                            <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                                Compare the backtest to a benchmark on the same
                                date range. Leave blank to keep the existing
                                no-benchmark workflow.
                            </p>
                        </div>

                        <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">
                                Risk-Free Rate
                            </Label>
                            <Input
                                type="number"
                                step={0.01}
                                min={0}
                                max={1}
                                value={riskFreeRate}
                                onChange={(e) =>
                                    setRiskFreeRate(Number(e.target.value))
                                }
                                className="border-border/50 bg-background/50"
                            />
                        </div>

                        <div className="space-y-3 rounded-xl border border-border/50 bg-background/30 p-3">
                            <div>
                                <Label className="text-xs text-muted-foreground">
                                    Data and Execution Assumptions
                                </Label>
                                <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                                    Surface the gap-handling policy and
                                    estimated trade frictions used to
                                    contextualize this run.
                                </p>
                            </div>

                            <div className="space-y-2">
                                <Label className="text-xs text-muted-foreground">
                                    Missing Data Policy
                                </Label>
                                <Select
                                    value={missingDataPolicy}
                                    onValueChange={(value) =>
                                        setMissingDataPolicy(
                                            value as MissingDataPolicy,
                                        )
                                    }
                                >
                                    <SelectTrigger className="border-border/50 bg-background/50">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                                        {MISSING_DATA_POLICY_OPTIONS.map(
                                            (option) => (
                                                <SelectItem
                                                    key={option.value}
                                                    value={option.value}
                                                >
                                                    {option.label}
                                                </SelectItem>
                                            ),
                                        )}
                                    </SelectContent>
                                </Select>
                                <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                                    {
                                        MISSING_DATA_POLICY_OPTIONS.find(
                                            (option) =>
                                                option.value ===
                                                missingDataPolicy,
                                        )?.description
                                    }
                                </p>
                            </div>

                            <div className="space-y-2">
                                <Label className="text-xs text-muted-foreground">
                                    Commission Model
                                </Label>
                                <Select
                                    value={costAssumptions.commission_mode}
                                    onValueChange={(value) =>
                                        updateCostAssumption(
                                            "commission_mode",
                                            value as BacktestCostAssumptions["commission_mode"],
                                        )
                                    }
                                >
                                    <SelectTrigger className="border-border/50 bg-background/50">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                                        {COMMISSION_MODE_OPTIONS.map(
                                            (option) => (
                                                <SelectItem
                                                    key={option.value}
                                                    value={option.value}
                                                >
                                                    {option.label}
                                                </SelectItem>
                                            ),
                                        )}
                                    </SelectContent>
                                </Select>
                            </div>

                            {costAssumptions.commission_mode ===
                                "per_share" && (
                                <div className="grid grid-cols-2 gap-3">
                                    <div className="space-y-1.5">
                                        <Label className="text-xs text-muted-foreground">
                                            Per Share ($)
                                        </Label>
                                        <Input
                                            type="number"
                                            min={0}
                                            step={0.0001}
                                            value={
                                                costAssumptions.commission_per_share
                                            }
                                            onChange={(e) =>
                                                updateCostAssumption(
                                                    "commission_per_share",
                                                    Number(e.target.value),
                                                )
                                            }
                                            className="border-border/50 bg-background/50"
                                        />
                                    </div>
                                    <div className="space-y-1.5">
                                        <Label className="text-xs text-muted-foreground">
                                            Minimum ($)
                                        </Label>
                                        <Input
                                            type="number"
                                            min={0}
                                            step={0.01}
                                            value={
                                                costAssumptions.commission_minimum
                                            }
                                            onChange={(e) =>
                                                updateCostAssumption(
                                                    "commission_minimum",
                                                    Number(e.target.value),
                                                )
                                            }
                                            className="border-border/50 bg-background/50"
                                        />
                                    </div>
                                </div>
                            )}

                            {costAssumptions.commission_mode ===
                                "percentage" && (
                                <div className="grid grid-cols-2 gap-3">
                                    <div className="space-y-1.5">
                                        <Label className="text-xs text-muted-foreground">
                                            Commission (bps)
                                        </Label>
                                        <Input
                                            type="number"
                                            min={0}
                                            step={0.1}
                                            value={
                                                costAssumptions.commission_bps
                                            }
                                            onChange={(e) =>
                                                updateCostAssumption(
                                                    "commission_bps",
                                                    Number(e.target.value),
                                                )
                                            }
                                            className="border-border/50 bg-background/50"
                                        />
                                    </div>
                                    <div className="space-y-1.5">
                                        <Label className="text-xs text-muted-foreground">
                                            Minimum ($)
                                        </Label>
                                        <Input
                                            type="number"
                                            min={0}
                                            step={0.01}
                                            value={
                                                costAssumptions.commission_minimum
                                            }
                                            onChange={(e) =>
                                                updateCostAssumption(
                                                    "commission_minimum",
                                                    Number(e.target.value),
                                                )
                                            }
                                            className="border-border/50 bg-background/50"
                                        />
                                    </div>
                                </div>
                            )}

                            <div className="grid grid-cols-2 gap-3">
                                <div className="space-y-1.5">
                                    <Label className="text-xs text-muted-foreground">
                                        Spread (bps)
                                    </Label>
                                    <Input
                                        type="number"
                                        min={0}
                                        step={0.1}
                                        value={costAssumptions.spread_bps}
                                        onChange={(e) =>
                                            updateCostAssumption(
                                                "spread_bps",
                                                Number(e.target.value),
                                            )
                                        }
                                        className="border-border/50 bg-background/50"
                                    />
                                </div>
                                <div className="space-y-1.5">
                                    <Label className="text-xs text-muted-foreground">
                                        Slippage (bps)
                                    </Label>
                                    <Input
                                        type="number"
                                        min={0}
                                        step={0.1}
                                        value={costAssumptions.slippage_bps}
                                        onChange={(e) =>
                                            updateCostAssumption(
                                                "slippage_bps",
                                                Number(e.target.value),
                                            )
                                        }
                                        className="border-border/50 bg-background/50"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="space-y-3 rounded-xl border border-border/50 bg-background/30 p-3">
                            <div>
                                <Label className="text-xs text-muted-foreground">
                                    Cashflow Planning
                                </Label>
                                <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                                    Model recurring savings, portfolio-funded
                                    withdrawals, and dated one-off events in the
                                    same backtest run.
                                </p>
                            </div>

                            <div className="grid grid-cols-[minmax(0,1fr)_132px] gap-2">
                                <Input
                                    type="number"
                                    value={recurringContribution}
                                    onChange={(e) =>
                                        setRecurringContribution(
                                            Number(e.target.value),
                                        )
                                    }
                                    placeholder="Recurring contribution"
                                    className="border-border/50 bg-background/50"
                                />
                                <Select
                                    value={contributionFrequency}
                                    onValueChange={(value) =>
                                        setContributionFrequency(
                                            value as RecurringCashflowRule["frequency"],
                                        )
                                    }
                                >
                                    <SelectTrigger className="border-border/50 bg-background/50">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                                        {CASHFLOW_FREQUENCY_OPTIONS.map(
                                            (option) => (
                                                <SelectItem
                                                    key={`contrib-${option.value}`}
                                                    value={option.value}
                                                >
                                                    {option.label}
                                                </SelectItem>
                                            ),
                                        )}
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="grid grid-cols-[minmax(0,1fr)_132px] gap-2">
                                <Input
                                    type="number"
                                    value={recurringWithdrawal}
                                    onChange={(e) =>
                                        setRecurringWithdrawal(
                                            Number(e.target.value),
                                        )
                                    }
                                    placeholder="Recurring withdrawal"
                                    className="border-border/50 bg-background/50"
                                />
                                <Select
                                    value={withdrawalFrequency}
                                    onValueChange={(value) =>
                                        setWithdrawalFrequency(
                                            value as RecurringCashflowRule["frequency"],
                                        )
                                    }
                                >
                                    <SelectTrigger className="border-border/50 bg-background/50">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                                        {CASHFLOW_FREQUENCY_OPTIONS.map(
                                            (option) => (
                                                <SelectItem
                                                    key={`withdraw-${option.value}`}
                                                    value={option.value}
                                                >
                                                    {option.label}
                                                </SelectItem>
                                            ),
                                        )}
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="space-y-2">
                                <Label className="text-xs text-muted-foreground">
                                    Inflation Rate
                                </Label>
                                <Input
                                    type="number"
                                    step={0.01}
                                    min={0}
                                    max={1}
                                    value={inflationRate}
                                    onChange={(e) =>
                                        setInflationRate(Number(e.target.value))
                                    }
                                    className="border-border/50 bg-background/50"
                                />
                            </div>

                            <div className="space-y-2">
                                <div className="flex items-center justify-between gap-2">
                                    <div>
                                        <Label className="text-xs text-muted-foreground">
                                            One-Time Events
                                        </Label>
                                        <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                                            Positive amounts add capital.
                                            Negative amounts withdraw it.
                                        </p>
                                    </div>
                                    <Button
                                        type="button"
                                        variant="outline"
                                        size="xs"
                                        onClick={addOneTimeCashflow}
                                    >
                                        <Plus />
                                        Add Event
                                    </Button>
                                </div>

                                {oneTimeCashflows.length > 0 && (
                                    <div className="space-y-2">
                                        {oneTimeCashflows.map(
                                            (event, index) => (
                                                <div
                                                    key={`${event.date}-${index}`}
                                                    className="grid grid-cols-[132px_minmax(0,1fr)_minmax(0,1fr)_auto] gap-2"
                                                >
                                                    <Input
                                                        type="date"
                                                        value={event.date}
                                                        onChange={(e) =>
                                                            updateOneTimeCashflow(
                                                                index,
                                                                {
                                                                    date: e
                                                                        .target
                                                                        .value,
                                                                },
                                                            )
                                                        }
                                                        className="border-border/50 bg-background/50"
                                                    />
                                                    <Input
                                                        type="number"
                                                        value={event.amount}
                                                        onChange={(e) =>
                                                            updateOneTimeCashflow(
                                                                index,
                                                                {
                                                                    amount: Number(
                                                                        e.target
                                                                            .value,
                                                                    ),
                                                                },
                                                            )
                                                        }
                                                        placeholder="Amount"
                                                        className="border-border/50 bg-background/50"
                                                    />
                                                    <Input
                                                        value={
                                                            event.label ?? ""
                                                        }
                                                        onChange={(e) =>
                                                            updateOneTimeCashflow(
                                                                index,
                                                                {
                                                                    label: e
                                                                        .target
                                                                        .value,
                                                                },
                                                            )
                                                        }
                                                        placeholder="Optional label"
                                                        className="border-border/50 bg-background/50"
                                                    />
                                                    <Button
                                                        type="button"
                                                        variant="ghost"
                                                        size="icon-xs"
                                                        onClick={() =>
                                                            removeOneTimeCashflow(
                                                                index,
                                                            )
                                                        }
                                                        aria-label={`Remove cashflow event ${index + 1}`}
                                                    >
                                                        <Trash2 />
                                                    </Button>
                                                </div>
                                            ),
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Dynamic strategy params */}
                        {currentStrategy?.params.map((p) => (
                            <div key={p.name} className="space-y-1.5">
                                <Label className="text-xs text-muted-foreground">
                                    {p.description || p.name}
                                </Label>
                                <Input
                                    type="number"
                                    step={p.type === "float" ? 0.01 : 1}
                                    value={params[p.name] ?? p.default}
                                    onChange={(e) =>
                                        setParams((prev) => ({
                                            ...prev,
                                            [p.name]: Number(e.target.value),
                                        }))
                                    }
                                    className="border-border/50 bg-background/50"
                                />
                            </div>
                        ))}

                        <Button
                            className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
                            onClick={handleRun}
                            disabled={mutation.isPending}
                        >
                            {mutation.isPending ? "Running..." : "Run Backtest"}
                        </Button>
                    </ConfigPanel>
                }
            >
                {mutation.isPending && (
                    <>
                        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                            <CardSkeleton />
                            <CardSkeleton />
                            <CardSkeleton />
                            <CardSkeleton />
                        </div>
                        <ChartSkeleton />
                    </>
                )}

                {stats && (
                    <>
                        {/* Metric cards */}
                        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                            <StatCard
                                label="CAGR"
                                value={formatPercent(stats["CAGR"] as number)}
                                trend={
                                    (stats["CAGR"] as number) > 0
                                        ? "up"
                                        : "down"
                                }
                            />
                            <StatCard
                                label="Sharpe Ratio"
                                value={formatNumber(
                                    stats["Sharpe"] as number,
                                    3,
                                )}
                                trend={
                                    (stats["Sharpe"] as number) > 0
                                        ? "up"
                                        : "down"
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
                                trend={
                                    (stats["ROI"] as number) > 0 ? "up" : "down"
                                }
                            />
                        </div>

                        {savedExperiment && (
                            <ChartCard title="Experiment Lineage">
                                <DataTable
                                    columns={[
                                        { key: "field", label: "Field" },
                                        { key: "value", label: "Value" },
                                    ]}
                                    data={[
                                        {
                                            field: "Run ID",
                                            value: savedExperiment.run_id,
                                        },
                                        {
                                            field: "Strategy",
                                            value: savedExperiment.strategy_name,
                                        },
                                        {
                                            field: "Created At",
                                            value: new Date(
                                                savedExperiment.created_at,
                                            ).toLocaleString(),
                                        },
                                        {
                                            field: "Config Hash",
                                            value: savedExperiment.config_hash,
                                        },
                                        {
                                            field: "Data Snapshot",
                                            value: savedExperiment.data_snapshot_id,
                                        },
                                    ]}
                                />
                            </ChartCard>
                        )}

                        {costSummary && appliedCostAssumptions && (
                            <>
                                <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                                    <StatCard
                                        label="Estimated Costs"
                                        value={formatCurrencyPrecise(
                                            costSummary.total_costs,
                                        )}
                                        trend="down"
                                    />
                                    <StatCard
                                        label="Commission"
                                        value={formatCurrencyPrecise(
                                            costSummary.total_commission,
                                        )}
                                        trend="down"
                                    />
                                    <StatCard
                                        label="Spread"
                                        value={formatCurrencyPrecise(
                                            costSummary.total_spread,
                                        )}
                                        trend="down"
                                    />
                                    <StatCard
                                        label="Slippage"
                                        value={formatCurrencyPrecise(
                                            costSummary.total_slippage,
                                        )}
                                        trend="down"
                                    />
                                </div>

                                <ChartCard title="Execution Frictions">
                                    <DataTable
                                        columns={[
                                            { key: "field", label: "Field" },
                                            { key: "value", label: "Value" },
                                        ]}
                                        data={[
                                            {
                                                field: "Commission Model",
                                                value: appliedCostAssumptions.commission_label,
                                            },
                                            {
                                                field: "Spread Model",
                                                value: appliedCostAssumptions.spread_label,
                                            },
                                            {
                                                field: "Slippage Model",
                                                value: appliedCostAssumptions.slippage_label,
                                            },
                                            {
                                                field: "Equity Curve Impact",
                                                value: appliedCostAssumptions.estimated_only
                                                    ? "Estimated separately from the equity curve"
                                                    : "Applied directly to the equity curve",
                                            },
                                        ]}
                                    />
                                </ChartCard>

                                {costBySymbolRows.length > 0 && (
                                    <ChartCard title="Estimated Costs by Symbol">
                                        <DataTable
                                            columns={[
                                                {
                                                    key: "ticker",
                                                    label: "Ticker",
                                                },
                                                {
                                                    key: "total_cost",
                                                    label: "Estimated Cost",
                                                    format: (value) =>
                                                        formatCurrencyPrecise(
                                                            value as
                                                                | number
                                                                | null,
                                                        ),
                                                },
                                            ]}
                                            data={costBySymbolRows}
                                        />
                                    </ChartCard>
                                )}
                            </>
                        )}

                        {missingDataSummary && (
                            <ChartCard title="Missing Data Handling">
                                <div className="mb-3 space-y-1 text-sm text-muted-foreground">
                                    <p>Policy: {missingDataSummary.policy}</p>
                                    {missingDataSummary.note && (
                                        <p>{missingDataSummary.note}</p>
                                    )}
                                </div>
                                <DataTable
                                    columns={[
                                        { key: "ticker", label: "Ticker" },
                                        {
                                            key: "had_missing_data",
                                            label: "Had Gaps",
                                            format: (value) =>
                                                value ? "Yes" : "No",
                                        },
                                        {
                                            key: "missing_rows",
                                            label: "Missing Rows",
                                        },
                                        {
                                            key: "missing_cells",
                                            label: "Missing Cells",
                                        },
                                        {
                                            key: "rows_dropped",
                                            label: "Rows Dropped",
                                        },
                                        {
                                            key: "remaining_missing_cells",
                                            label: "Remaining Gaps",
                                        },
                                    ]}
                                    data={missingDataSummary.tickers}
                                />
                            </ChartCard>
                        )}

                        {walkForwardRequest && (
                            <ChartCard title="Walk-Forward Follow-Up">
                                <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                                    <div className="space-y-1">
                                        <p className="text-sm text-muted-foreground">
                                            {walkForwardRequest.reason}
                                        </p>
                                        <p className="text-xs text-muted-foreground/70">
                                            Suggested windows: train{" "}
                                            {walkForwardRequest.train_window}{" "}
                                            days, test{" "}
                                            {walkForwardRequest.test_window}{" "}
                                            days, step{" "}
                                            {walkForwardRequest.step_size} days.
                                        </p>
                                    </div>
                                    <Button asChild>
                                        <Link href={walkForwardHref}>
                                            Open Walk-Forward Analysis
                                        </Link>
                                    </Button>
                                </div>
                            </ChartCard>
                        )}

                        {withdrawalDurability && (
                            <>
                                <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                                    <StatCard
                                        label="Withdrawal Plan"
                                        value={
                                            withdrawalDurability.survived_to_end
                                                ? "Survived"
                                                : "Depleted"
                                        }
                                        trend={
                                            withdrawalDurability.survived_to_end
                                                ? "up"
                                                : "down"
                                        }
                                    />
                                    <StatCard
                                        label="Real Ending Value"
                                        value={formatCurrencyPrecise(
                                            withdrawalDurability.ending_real_value,
                                        )}
                                        trend={getMetricTrend(
                                            withdrawalDurability.real_total_return,
                                        )}
                                    />
                                    <StatCard
                                        label="Total Withdrawals"
                                        value={formatCurrencyPrecise(
                                            withdrawalDurability.total_withdrawals,
                                        )}
                                        trend="neutral"
                                    />
                                    <StatCard
                                        label="Net Cashflow"
                                        value={formatCurrencyPrecise(
                                            withdrawalDurability.net_cashflow,
                                        )}
                                        trend={getMetricTrend(
                                            withdrawalDurability.net_cashflow,
                                        )}
                                    />
                                </div>

                                {inflationAdjustedSeries.length > 0 && (
                                    <ChartCard
                                        title={`Nominal vs Real Value (${formatPercent(withdrawalDurability.inflation_rate)} inflation)`}
                                    >
                                        <LightweightChart
                                            series={inflationAdjustedSeries}
                                            height={360}
                                            type="line"
                                        />
                                    </ChartCard>
                                )}

                                {cashflowEvents.length > 0 && (
                                    <ChartCard title="Cashflow Log">
                                        <DataTable
                                            columns={[
                                                {
                                                    key: "scheduled_date",
                                                    label: "Scheduled",
                                                    format: (value) =>
                                                        new Date(
                                                            String(value),
                                                        ).toLocaleDateString(),
                                                },
                                                {
                                                    key: "applied_date",
                                                    label: "Applied",
                                                    format: (value) =>
                                                        new Date(
                                                            String(value),
                                                        ).toLocaleDateString(),
                                                },
                                                {
                                                    key: "label",
                                                    label: "Label",
                                                },
                                                {
                                                    key: "source",
                                                    label: "Type",
                                                },
                                                {
                                                    key: "direction",
                                                    label: "Direction",
                                                },
                                                {
                                                    key: "amount",
                                                    label: "Amount",
                                                    format: (value) =>
                                                        formatCurrencyPrecise(
                                                            value as
                                                                | number
                                                                | null,
                                                        ),
                                                },
                                                {
                                                    key: "cash_after",
                                                    label: "Cash After",
                                                    format: (value) =>
                                                        formatCurrencyPrecise(
                                                            value as
                                                                | number
                                                                | null,
                                                        ),
                                                },
                                                {
                                                    key: "portfolio_value_after",
                                                    label: "Portfolio After",
                                                    format: (value) =>
                                                        formatCurrencyPrecise(
                                                            value as
                                                                | number
                                                                | null,
                                                        ),
                                                },
                                            ]}
                                            data={cashflowEvents}
                                        />
                                    </ChartCard>
                                )}
                            </>
                        )}

                        {benchmarkStats && (
                            <>
                                <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
                                    <StatCard
                                        label="Alpha"
                                        value={formatBenchmarkValue(
                                            benchmarkStats.alpha,
                                            formatPercent,
                                        )}
                                        trend={getMetricTrend(
                                            benchmarkStats.alpha,
                                        )}
                                    />
                                    <StatCard
                                        label="Beta"
                                        value={formatBenchmarkValue(
                                            benchmarkStats.beta,
                                            (value) =>
                                                formatNumber(value ?? null, 3),
                                        )}
                                        trend="neutral"
                                    />
                                    <StatCard
                                        label="R-Squared"
                                        value={formatBenchmarkValue(
                                            benchmarkStats.r_squared,
                                            (value) =>
                                                formatNumber(value ?? null, 3),
                                        )}
                                        trend="neutral"
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
                                    <StatCard
                                        label="Tracking Error"
                                        value={formatBenchmarkValue(
                                            benchmarkStats.tracking_error,
                                            formatPercent,
                                        )}
                                        trend="neutral"
                                    />
                                    <StatCard
                                        label="Information Ratio"
                                        value={formatBenchmarkValue(
                                            benchmarkStats.information_ratio,
                                            (value) =>
                                                formatNumber(value ?? null, 3),
                                        )}
                                        trend={getMetricTrend(
                                            benchmarkStats.information_ratio,
                                        )}
                                    />
                                    <StatCard
                                        label="Up/Down Capture"
                                        value={`${formatBenchmarkValue(benchmarkStats.up_capture, formatPercent)} / ${formatBenchmarkValue(benchmarkStats.down_capture, formatPercent)}`}
                                        trend="neutral"
                                    />
                                </div>
                            </>
                        )}

                        {benchmarkStats && comparisonChartSeries.length > 0 && (
                            <ChartCard
                                title={
                                    benchmarkStats
                                        ? `Portfolio vs ${benchmarkStats.benchmark_name}`
                                        : "Portfolio Value"
                                }
                            >
                                <LightweightChart
                                    series={comparisonChartSeries}
                                    height={400}
                                    type={benchmarkStats ? "line" : "area"}
                                />
                            </ChartCard>
                        )}

                        {/* Portfolio value chart */}
                        {result?.value_history &&
                            !benchmarkStats &&
                            result.value_history.length > 0 && (
                                <ChartCard title="Portfolio Value">
                                    <LightweightChart
                                        series={[
                                            {
                                                name: "Value",
                                                dates: result.value_history.map(
                                                    (r) => String(r.date),
                                                ),
                                                values: result.value_history.map(
                                                    (r) => r.Value as number,
                                                ),
                                            },
                                        ]}
                                        height={400}
                                        type="area"
                                    />
                                </ChartCard>
                            )}

                        {/* Drawdown chart */}
                        {result?.value_history &&
                            result.value_history.length > 0 && (
                                <ChartCard title="Drawdown">
                                    <DrawdownChart
                                        data={result.value_history.map((r) => ({
                                            date: String(r.date),
                                            value: r.Value as number,
                                        }))}
                                        height={200}
                                    />
                                </ChartCard>
                            )}
                        {benchmarkStats && (
                            <ChartCard title="Benchmark Comparison">
                                <DataTable
                                    columns={[
                                        { key: "metric", label: "Metric" },
                                        { key: "value", label: "Value" },
                                    ]}
                                    data={[
                                        {
                                            metric: "Benchmark",
                                            value: benchmarkStats.benchmark_name,
                                        },
                                        {
                                            metric: "Observations",
                                            value: String(
                                                benchmarkStats.n_observations,
                                            ),
                                        },
                                        {
                                            metric: "Alpha",
                                            value: formatBenchmarkValue(
                                                benchmarkStats.alpha,
                                                formatPercent,
                                            ),
                                        },
                                        {
                                            metric: "Beta",
                                            value: formatBenchmarkValue(
                                                benchmarkStats.beta,
                                                (value) =>
                                                    formatNumber(
                                                        value ?? null,
                                                        4,
                                                    ),
                                            ),
                                        },
                                        {
                                            metric: "R-Squared",
                                            value: formatBenchmarkValue(
                                                benchmarkStats.r_squared,
                                                (value) =>
                                                    formatNumber(
                                                        value ?? null,
                                                        4,
                                                    ),
                                            ),
                                        },
                                        {
                                            metric: "Tracking Error",
                                            value: formatBenchmarkValue(
                                                benchmarkStats.tracking_error,
                                                formatPercent,
                                            ),
                                        },
                                        {
                                            metric: "Information Ratio",
                                            value: formatBenchmarkValue(
                                                benchmarkStats.information_ratio,
                                                (value) =>
                                                    formatNumber(
                                                        value ?? null,
                                                        4,
                                                    ),
                                            ),
                                        },
                                        {
                                            metric: "Up Capture",
                                            value: formatBenchmarkValue(
                                                benchmarkStats.up_capture,
                                                formatPercent,
                                            ),
                                        },
                                        {
                                            metric: "Down Capture",
                                            value: formatBenchmarkValue(
                                                benchmarkStats.down_capture,
                                                formatPercent,
                                            ),
                                        },
                                    ]}
                                />
                            </ChartCard>
                        )}

                        {rollingMetrics && (
                            <>
                                <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
                                    <StatCard
                                        label="Mean Rolling Sharpe"
                                        value={formatBenchmarkValue(
                                            rollingMetrics.mean_sharpe,
                                            (value) =>
                                                formatNumber(value ?? null, 3),
                                        )}
                                        trend={getMetricTrend(
                                            rollingMetrics.mean_sharpe,
                                        )}
                                    />
                                    <StatCard
                                        label="Mean Rolling Vol"
                                        value={formatBenchmarkValue(
                                            rollingMetrics.mean_vol,
                                            formatPercent,
                                        )}
                                        trend="neutral"
                                    />
                                    {rollingMetrics.mean_beta != null && (
                                        <StatCard
                                            label="Mean Rolling Beta"
                                            value={formatNumber(
                                                rollingMetrics.mean_beta,
                                                3,
                                            )}
                                            trend="neutral"
                                        />
                                    )}
                                </div>

                                {rollingChartData.length > 0 && (
                                    <ChartCard
                                        title={`Rolling Diagnostics (${rollingMetrics.window}-day)`}
                                    >
                                        <LineChartWrapper
                                            data={
                                                rollingChartData as Record<
                                                    string,
                                                    unknown
                                                >[]
                                            }
                                            xKey="date"
                                            series={[
                                                {
                                                    key: "sharpe",
                                                    color: "#2563eb",
                                                },
                                                {
                                                    key: "volatility",
                                                    color: "#f97316",
                                                },
                                                ...(rollingMetrics.beta
                                                    ? [
                                                          {
                                                              key: "beta",
                                                              color: "#16a34a",
                                                          },
                                                      ]
                                                    : []),
                                            ]}
                                            height={360}
                                            referenceY={0}
                                            referenceLabel="Zero"
                                        />
                                    </ChartCard>
                                )}
                            </>
                        )}

                        {regimeSummary.length > 0 && (
                            <ChartCard
                                title={
                                    regimeReferenceTicker
                                        ? `Regime Summary (${regimeReferenceTicker})`
                                        : "Regime Summary"
                                }
                            >
                                <DataTable
                                    columns={[
                                        { key: "regime", label: "Regime" },
                                        {
                                            key: "count_periods",
                                            label: "Periods",
                                        },
                                        {
                                            key: "total_days",
                                            label: "Days",
                                        },
                                        {
                                            key: "cagr",
                                            label: "CAGR",
                                            format: (value) =>
                                                formatPercent(
                                                    value as number | null,
                                                ),
                                        },
                                        {
                                            key: "volatility",
                                            label: "Volatility",
                                            format: (value) =>
                                                formatPercent(
                                                    value as number | null,
                                                ),
                                        },
                                        {
                                            key: "sharpe",
                                            label: "Sharpe",
                                            format: (value) =>
                                                formatNumber(
                                                    value as number | null,
                                                    3,
                                                ),
                                        },
                                        {
                                            key: "total_return",
                                            label: "Total Return",
                                            format: (value) =>
                                                formatPercent(
                                                    value as number | null,
                                                ),
                                        },
                                    ]}
                                    data={
                                        regimeSummary as BacktestRegimeSummary[]
                                    }
                                />
                            </ChartCard>
                        )}

                        {regimePeriods.length > 0 && (
                            <ChartCard title="Regime Periods">
                                <DataTable
                                    columns={[
                                        { key: "regime", label: "Regime" },
                                        {
                                            key: "start",
                                            label: "Start",
                                            format: (value) =>
                                                new Date(
                                                    String(value),
                                                ).toLocaleDateString(),
                                        },
                                        {
                                            key: "end",
                                            label: "End",
                                            format: (value) =>
                                                new Date(
                                                    String(value),
                                                ).toLocaleDateString(),
                                        },
                                        { key: "days", label: "Days" },
                                        {
                                            key: "market_return",
                                            label: "Market Return",
                                            format: (value) =>
                                                formatPercent(
                                                    value as number | null,
                                                ),
                                        },
                                        {
                                            key: "market_volatility",
                                            label: "Market Vol",
                                            format: (value) =>
                                                formatPercent(
                                                    value as number | null,
                                                ),
                                        },
                                        {
                                            key: "portfolio_return",
                                            label: "Portfolio Return",
                                            format: (value) =>
                                                formatPercent(
                                                    value as number | null,
                                                ),
                                        },
                                        {
                                            key: "portfolio_volatility",
                                            label: "Portfolio Vol",
                                            format: (value) =>
                                                formatPercent(
                                                    value as number | null,
                                                ),
                                        },
                                    ]}
                                    data={
                                        regimePeriods as BacktestRegimePeriod[]
                                    }
                                />
                            </ChartCard>
                        )}

                        {allocationChartData.length > 0 && (
                            <>
                                <ChartCard title="Allocation Drift">
                                    <LineChartWrapper
                                        data={allocationChartData}
                                        xKey="date"
                                        series={allocationSeriesKeys.map(
                                            (key, index) => ({
                                                key,
                                                color:
                                                    index === 0
                                                        ? "#2563eb"
                                                        : index === 1
                                                          ? "#16a34a"
                                                          : index === 2
                                                            ? "#f97316"
                                                            : undefined,
                                            }),
                                        )}
                                        height={360}
                                    />
                                </ChartCard>

                                {allocationDriftSummary.length > 0 && (
                                    <ChartCard title="Allocation Drift Summary">
                                        <DataTable
                                            columns={[
                                                {
                                                    key: "ticker",
                                                    label: "Ticker",
                                                },
                                                {
                                                    key: "target_weight",
                                                    label: "Target",
                                                    format: (value) =>
                                                        formatPercent(
                                                            value as
                                                                | number
                                                                | null,
                                                        ),
                                                },
                                                {
                                                    key: "latest_weight",
                                                    label: "Latest",
                                                    format: (value) =>
                                                        formatPercent(
                                                            value as
                                                                | number
                                                                | null,
                                                        ),
                                                },
                                                {
                                                    key: "max_drift",
                                                    label: "Max Drift",
                                                    format: (value) =>
                                                        formatPercent(
                                                            value as
                                                                | number
                                                                | null,
                                                        ),
                                                },
                                            ]}
                                            data={allocationDriftSummary}
                                        />
                                    </ChartCard>
                                )}
                            </>
                        )}

                        {rebalanceEvents.length > 0 && (
                            <ChartCard title="Rebalance Log">
                                <DataTable
                                    columns={[
                                        {
                                            key: "date",
                                            label: "Date",
                                            format: (value) =>
                                                new Date(
                                                    String(value),
                                                ).toLocaleDateString(),
                                        },
                                        {
                                            key: "event_type",
                                            label: "Event",
                                        },
                                        {
                                            key: "trade_count",
                                            label: "Trades",
                                        },
                                        {
                                            key: "symbols",
                                            label: "Symbols",
                                            format: (value) =>
                                                Array.isArray(value)
                                                    ? value.join(", ")
                                                    : String(value ?? ""),
                                        },
                                        {
                                            key: "gross_trade_value",
                                            label: "Gross Value",
                                            format: (value) =>
                                                formatCurrencyPrecise(
                                                    value as number | null,
                                                ),
                                        },
                                        {
                                            key: "net_trade_value",
                                            label: "Net Flow",
                                            format: (value) =>
                                                formatCurrencyPrecise(
                                                    value as number | null,
                                                ),
                                        },
                                        {
                                            key: "portfolio_value",
                                            label: "Portfolio",
                                            format: (value) =>
                                                formatCurrencyPrecise(
                                                    value as number | null,
                                                ),
                                        },
                                        {
                                            key: "cash_after",
                                            label: "Cash After",
                                            format: (value) =>
                                                formatCurrencyPrecise(
                                                    value as number | null,
                                                ),
                                        },
                                    ]}
                                    data={rebalanceEvents}
                                />
                            </ChartCard>
                        )}

                        {monthlyReturns.length > 0 && (
                            <ChartCard title="Monthly Returns">
                                <DataTable
                                    columns={[
                                        { key: "period", label: "Period" },
                                        {
                                            key: "start_value",
                                            label: "Start Value",
                                            format: (value) =>
                                                formatCurrencyPrecise(
                                                    value as number | null,
                                                ),
                                        },
                                        {
                                            key: "end_value",
                                            label: "End Value",
                                            format: (value) =>
                                                formatCurrencyPrecise(
                                                    value as number | null,
                                                ),
                                        },
                                        {
                                            key: "return_pct",
                                            label: "Return",
                                            format: (value) =>
                                                formatPercent(
                                                    value as number | null,
                                                ),
                                        },
                                    ]}
                                    data={monthlyReturns as ReturnTableRow[]}
                                />
                            </ChartCard>
                        )}

                        {annualReturns.length > 0 && (
                            <ChartCard title="Annual Returns">
                                <DataTable
                                    columns={[
                                        { key: "period", label: "Year" },
                                        {
                                            key: "start_value",
                                            label: "Start Value",
                                            format: (value) =>
                                                formatCurrencyPrecise(
                                                    value as number | null,
                                                ),
                                        },
                                        {
                                            key: "end_value",
                                            label: "End Value",
                                            format: (value) =>
                                                formatCurrencyPrecise(
                                                    value as number | null,
                                                ),
                                        },
                                        {
                                            key: "return_pct",
                                            label: "Return",
                                            format: (value) =>
                                                formatPercent(
                                                    value as number | null,
                                                ),
                                        },
                                    ]}
                                    data={annualReturns as ReturnTableRow[]}
                                />
                            </ChartCard>
                        )}

                        {/* Trades table */}
                        {result?.trades && result.trades.length > 0 && (
                            <ChartCard
                                title={`Trades (${result.trades.length})`}
                            >
                                <DataTable
                                    columns={[
                                        { key: "date", label: "Date" },
                                        { key: "ticker", label: "Ticker" },
                                        { key: "action", label: "Action" },
                                        {
                                            key: "size",
                                            label: "Size",
                                            format: (v) =>
                                                formatNumber(v as number, 0),
                                        },
                                        {
                                            key: "price",
                                            label: "Price",
                                            format: (v) =>
                                                formatCurrencyPrecise(
                                                    v as number,
                                                ),
                                        },
                                        {
                                            key: "value",
                                            label: "Value",
                                            format: (v) =>
                                                formatCurrencyPrecise(
                                                    v as number,
                                                ),
                                        },
                                    ]}
                                    data={result.trades}
                                />
                            </ChartCard>
                        )}

                        {/* Full statistics */}
                        <ChartCard title="Full Statistics">
                            <DataTable
                                columns={[
                                    { key: "metric", label: "Metric" },
                                    { key: "value", label: "Value" },
                                ]}
                                data={Object.entries(stats).map(([k, v]) => ({
                                    metric: k,
                                    value:
                                        typeof v === "number"
                                            ? v < 1 &&
                                              v > -1 &&
                                              k !== "Sharpe" &&
                                              k !== "Smart Sharpe"
                                                ? formatPercent(v)
                                                : formatNumber(v, 4)
                                            : String(v ?? "N/A"),
                                }))}
                            />
                        </ChartCard>
                    </>
                )}

                {mutation.isError && (
                    <InlineError
                        message={mutation.error?.message ?? "Backtest failed"}
                        onRetry={handleRun}
                    />
                )}

                {!mutation.isPending && !mutation.isError && !result && (
                    <EmptyState
                        icon={Activity}
                        message="Configure parameters and click Run Backtest to see results."
                        presets={[
                            {
                                label: "SPY Buy & Hold",
                                onClick: () =>
                                    applyPortfolioPreset(PORTFOLIO_PRESETS[0]),
                            },
                            {
                                label: "60/40 Rebalance",
                                onClick: () =>
                                    applyPortfolioPreset(PORTFOLIO_PRESETS[1]),
                            },
                            {
                                label: "SPY SMA Crossover",
                                onClick: () => {
                                    setTicker("SPY");
                                    applyStrategy("SMACrossover");
                                },
                            },
                        ]}
                    />
                )}
            </ToolLayout>
        </div>
    );
}
