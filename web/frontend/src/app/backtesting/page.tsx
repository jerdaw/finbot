"use client";

import { useEffect, useState } from "react";
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
import {
    Tabs,
    TabsList,
    TabsTrigger,
} from "@/components/ui/tabs";
import { StatCard } from "@/components/common/stat-card";
import { PageHeader } from "@/components/common/page-header";
import { ConfigPanel, ConfigSection } from "@/components/common/config-panel";
import { ChartCard } from "@/components/common/chart-card";
import { ToolLayout } from "@/components/common/tool-layout";
import { EmptyState } from "@/components/common/empty-state";
import { InlineError } from "@/components/common/inline-error";
import {
    ChartSkeleton,
    CardSkeleton,
} from "@/components/common/loading-skeleton";
import {
    Activity,
    BarChart3,
    Download,
    Eye,
    EyeOff,
    LineChart,
    Plus,
    Save,
    Share2,
    Trash2,
    X,
} from "lucide-react";
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
    id: string;
    label: string;
    description: string;
    category: "Core" | "Diversified" | "Defensive" | "Tactical";
    assumption: "live/local" | "simulated" | "proxy" | "unavailable";
    strategy: "NoRebalance" | "Rebalance";
    assets: PortfolioAsset[];
    rebalInterval?: number;
}

interface SavedPortfolio {
    id: string;
    label: string;
    strategy: "NoRebalance" | "Rebalance";
    assets: PortfolioAsset[];
    strategyParams?: Record<string, number>;
    createdAt: string;
}

interface ComparisonPortfolio {
    id: string;
    label: string;
    strategy: "NoRebalance" | "Rebalance";
    assets: PortfolioAsset[];
    strategyParams?: Record<string, number>;
    source: "current" | "preset" | "saved";
}

interface ComparisonRun {
    portfolio: ComparisonPortfolio;
    request: BacktestRequest | null;
    result: BacktestResponse | null;
    error?: string;
}

const DEFAULT_PORTFOLIO_ASSETS: PortfolioAsset[] = [
    { ticker: "SPY", weight: 100 },
];

const SAVED_PORTFOLIOS_KEY = "finbot-backtesting-saved-portfolios";
const MAX_COMPARISON_PORTFOLIOS = 5;

const PORTFOLIO_PRESETS: PortfolioPreset[] = [
    {
        id: "spy-buy-hold",
        label: "SPY Buy & Hold",
        description: "Single-asset U.S. equity baseline.",
        category: "Core",
        assumption: "live/local",
        strategy: "NoRebalance",
        assets: [{ ticker: "SPY", weight: 100 }],
    },
    {
        id: "sixty-forty",
        label: "60/40",
        description: "U.S. equity and long Treasury allocation.",
        category: "Core",
        assumption: "live/local",
        strategy: "Rebalance",
        rebalInterval: 253,
        assets: [
            { ticker: "SPY", weight: 60 },
            { ticker: "TLT", weight: 40 },
        ],
    },
    {
        id: "three-fund",
        label: "Three-Fund",
        description: "U.S. equity, ex-U.S. equity, and aggregate bonds.",
        category: "Diversified",
        assumption: "live/local",
        strategy: "Rebalance",
        rebalInterval: 253,
        assets: [
            { ticker: "VTI", weight: 50 },
            { ticker: "VXUS", weight: 30 },
            { ticker: "BND", weight: 20 },
        ],
    },
    {
        id: "all-weather",
        label: "All Weather",
        description: "Risk-balanced macro mix using common ETF proxies.",
        category: "Defensive",
        assumption: "proxy",
        strategy: "Rebalance",
        rebalInterval: 253,
        assets: [
            { ticker: "SPY", weight: 30 },
            { ticker: "TLT", weight: 40 },
            { ticker: "IEF", weight: 15 },
            { ticker: "GLD", weight: 7.5 },
            { ticker: "DBC", weight: 7.5 },
        ],
    },
    {
        id: "permanent-portfolio",
        label: "Permanent",
        description: "Stocks, long bonds, cash-like Treasuries, and gold.",
        category: "Defensive",
        assumption: "proxy",
        strategy: "Rebalance",
        rebalInterval: 253,
        assets: [
            { ticker: "SPY", weight: 25 },
            { ticker: "TLT", weight: 25 },
            { ticker: "SHY", weight: 25 },
            { ticker: "GLD", weight: 25 },
        ],
    },
    {
        id: "golden-butterfly",
        label: "Golden Butterfly",
        description: "Permanent-portfolio inspired mix with small-value proxy.",
        category: "Defensive",
        assumption: "proxy",
        strategy: "Rebalance",
        rebalInterval: 253,
        assets: [
            { ticker: "SPY", weight: 20 },
            { ticker: "IJS", weight: 20 },
            { ticker: "TLT", weight: 20 },
            { ticker: "SHY", weight: 20 },
            { ticker: "GLD", weight: 20 },
        ],
    },
    {
        id: "hfea",
        label: "HFEA",
        description: "Leveraged equity/Treasury allocation; high path risk.",
        category: "Tactical",
        assumption: "live/local",
        strategy: "Rebalance",
        rebalInterval: 63,
        assets: [
            { ticker: "UPRO", weight: 55 },
            { ticker: "TMF", weight: 45 },
        ],
    },
    {
        id: "risk-parity-starter",
        label: "Risk Parity Starter",
        description: "Balanced ETF proxy mix for a risk-parity-style study.",
        category: "Diversified",
        assumption: "proxy",
        strategy: "Rebalance",
        rebalInterval: 63,
        assets: [
            { ticker: "SPY", weight: 25 },
            { ticker: "TLT", weight: 35 },
            { ticker: "GLD", weight: 20 },
            { ticker: "DBC", weight: 20 },
        ],
    },
    {
        id: "equal-weight-basket",
        label: "Equal Weight",
        description: "Simple equal-weight multi-asset starter basket.",
        category: "Core",
        assumption: "live/local",
        strategy: "Rebalance",
        rebalInterval: 253,
        assets: [
            { ticker: "SPY", weight: 25 },
            { ticker: "QQQ", weight: 25 },
            { ticker: "TLT", weight: 25 },
            { ticker: "GLD", weight: 25 },
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

function getNumericStat(
    stats: Record<string, unknown> | null | undefined,
    key: string,
): number | null {
    const value = stats?.[key];
    return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function getEndingValue(result: BacktestResponse | null | undefined): number | null {
    const history = result?.value_history ?? [];
    const last = history[history.length - 1];
    const value = last?.Value;
    return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function buildPortfolioLabel(assets: PortfolioAsset[]): string {
    const tickers = assets
        .filter((asset) => asset.ticker.trim().length > 0)
        .map((asset) => `${asset.ticker.trim().toUpperCase()} ${formatNumber(asset.weight, 0)}%`);
    return tickers.length > 0 ? tickers.join(" / ") : "Untitled Portfolio";
}

function cloneAssets(assets: PortfolioAsset[]): PortfolioAsset[] {
    return assets.map((asset) => ({
        ticker: asset.ticker.trim().toUpperCase(),
        weight: Number(asset.weight),
    }));
}

function buildPortfolioStrategyParams(
    portfolioStrategy: "NoRebalance" | "Rebalance",
    sourceParams: Record<string, number>,
): Record<string, number> | undefined {
    if (portfolioStrategy !== "Rebalance") {
        return undefined;
    }

    const rebalInterval =
        typeof sourceParams.rebal_interval === "number"
            ? sourceParams.rebal_interval
            : STRATEGY_FALLBACK_PARAMS.Rebalance.rebal_interval;

    return { rebal_interval: rebalInterval };
}

function buildDrawdownValues(values: Array<number | null>): Array<number | null> {
    let peak: number | null = null;

    return values.map((value) => {
        if (value == null || !Number.isFinite(value) || value <= 0) {
            return null;
        }

        peak = peak == null ? value : Math.max(peak, value);
        return (value / peak - 1) * 100;
    });
}

function encodeSharedConfig(request: BacktestRequest): string {
    return encodeURIComponent(JSON.stringify(request));
}

function decodeSharedConfig(value: string): BacktestRequest | null {
    try {
        const parsed = JSON.parse(decodeURIComponent(value));
        if (!parsed || !Array.isArray(parsed.tickers) || typeof parsed.strategy !== "string") {
            return null;
        }
        return parsed as BacktestRequest;
    } catch {
        return null;
    }
}

function normalizeRequestForSignature(request: BacktestRequest | null): string | null {
    if (!request) {
        return null;
    }

    return JSON.stringify({
        tickers: request.tickers,
        strategy: request.strategy,
        strategy_params: request.strategy_params,
        start_date: request.start_date,
        end_date: request.end_date,
        initial_cash: request.initial_cash,
        benchmark_ticker: request.benchmark_ticker ?? "",
        risk_free_rate: request.risk_free_rate,
        recurring_cashflows: request.recurring_cashflows ?? [],
        one_time_cashflows: request.one_time_cashflows ?? [],
        inflation_rate: request.inflation_rate,
        missing_data_policy: request.missing_data_policy,
        cost_assumptions: request.cost_assumptions,
    });
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
    const [lastComparisonRequest, setLastComparisonRequest] =
        useState<BacktestRequest | null>(null);
    const [savedExperiment, setSavedExperiment] =
        useState<SaveExperimentResponse | null>(null);
    const [activeResultTab, setActiveResultTab] = useState("overview");
    const [portfolioChartLogScale, setPortfolioChartLogScale] =
        useState(false);
    const [showPortfolioSeries, setShowPortfolioSeries] = useState(true);
    const [showBenchmarkSeries, setShowBenchmarkSeries] = useState(true);
    const [comparisonPortfolios, setComparisonPortfolios] = useState<
        ComparisonPortfolio[]
    >([]);
    const [comparisonRuns, setComparisonRuns] = useState<ComparisonRun[]>([]);
    const [savedPortfolios, setSavedPortfolios] = useState<SavedPortfolio[]>(
        [],
    );
    const [presetFilter, setPresetFilter] = useState("");

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
    const filteredPortfolioPresets = PORTFOLIO_PRESETS.filter((preset) => {
        const query = presetFilter.trim().toLowerCase();
        if (!query) {
            return true;
        }
        return [
            preset.label,
            preset.description,
            preset.category,
            preset.assumption,
            ...preset.assets.map((asset) => asset.ticker),
        ]
            .join(" ")
            .toLowerCase()
            .includes(query);
    });

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
                throw new Error("Fix the current run configuration before comparing portfolios.");
            }

            const runs = await Promise.all(
                portfolios.map(async (portfolio): Promise<ComparisonRun> => {
                    const request = buildComparisonRequest(portfolio, baseRequest);
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
                toast.error(`${failed} comparison run${failed === 1 ? "" : "s"} failed`);
            } else {
                toast.success("Comparison complete");
            }
            setActiveResultTab("comparison");
        },
        onError: (e) => toast.error(`Comparison failed: ${e.message}`),
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
        if (preset.strategy === "Rebalance" && preset.rebalInterval) {
            const rebalInterval = preset.rebalInterval;
            setParams((current) => ({
                ...current,
                rebal_interval: rebalInterval,
            }));
        }
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

    const normalizePortfolioWeights = () => {
        setPortfolioAssets((current) => {
            const totalWeight = current.reduce(
                (total, asset) => total + Number(asset.weight),
                0,
            );
            if (totalWeight <= 0) {
                toast.error("Enter positive weights before normalizing.");
                return current;
            }

            const normalized = current.map((asset) => ({
                ...asset,
                weight: Number(((asset.weight / totalWeight) * 100).toFixed(2)),
            }));
            const roundedTotal = normalized.reduce(
                (total, asset) => total + asset.weight,
                0,
            );
            const delta = Number((100 - roundedTotal).toFixed(2));
            return normalized.map((asset, index) =>
                index === normalized.length - 1
                    ? { ...asset, weight: Number((asset.weight + delta).toFixed(2)) }
                    : asset,
            );
        });
    };

    const clearPortfolioAssets = () => {
        setPortfolioAssets([{ ticker: "", weight: 0 }]);
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

    const buildComparisonRequest = (
        portfolio: ComparisonPortfolio,
        baseRequest: BacktestRequest,
    ): BacktestRequest => {
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
        setRecurringContribution(
            contributionRule?.amount ?? 0,
        );
        if (contributionRule?.frequency) {
            setContributionFrequency(contributionRule.frequency);
        }
        setRecurringWithdrawal(
            Math.abs(withdrawalRule?.amount ?? 0),
        );
        if (withdrawalRule?.frequency) {
            setWithdrawalFrequency(withdrawalRule.frequency);
        }
        setOneTimeCashflows(request.one_time_cashflows ?? []);
        setInflationRate(request.inflation_rate ?? 0.03);

        if (request.strategy === "NoRebalance" || request.strategy === "Rebalance") {
            const proportions =
                request.strategy === "NoRebalance"
                    ? request.strategy_params.equity_proportions
                    : request.strategy_params.rebal_proportions;
            const weights = Array.isArray(proportions)
                ? proportions.map((value) => Number(value) * 100)
                : request.tickers.map(() => Number((100 / request.tickers.length).toFixed(2)));
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

    const handleRun = () => {
        const request = buildBacktestRequest();
        if (!request) {
            return;
        }
        mutation.mutate(request);
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

    const handleSavePortfolio = () => {
        if (!isAllocationStrategy || !allocationIsBalanced) {
            toast.error("Save a balanced allocation portfolio first.");
            return;
        }

        const saved: SavedPortfolio = {
            id: `portfolio-${Date.now()}`,
            label: buildPortfolioLabel(portfolioAssets),
            strategy: strategy as "NoRebalance" | "Rebalance",
            assets: cloneAssets(portfolioAssets),
            strategyParams: buildPortfolioStrategyParams(
                strategy as "NoRebalance" | "Rebalance",
                params,
            ),
            createdAt: new Date().toISOString(),
        };
        setSavedPortfolios((current) => [saved, ...current].slice(0, 12));
        toast.success("Portfolio saved");
    };

    const applySavedPortfolio = (portfolio: SavedPortfolio) => {
        applyStrategy(portfolio.strategy);
        setPortfolioAssets(cloneAssets(portfolio.assets));
        if (portfolio.strategyParams) {
            setParams((current) => ({
                ...current,
                ...portfolio.strategyParams,
            }));
        }
    };

    const removeSavedPortfolio = (id: string) => {
        setSavedPortfolios((current) => current.filter((portfolio) => portfolio.id !== id));
    };

    const addComparisonPortfolio = (
        portfolio: Omit<ComparisonPortfolio, "id">,
    ) => {
        setComparisonPortfolios((current) => {
            if (current.length >= MAX_COMPARISON_PORTFOLIOS) {
                toast.error(`Compare up to ${MAX_COMPARISON_PORTFOLIOS} portfolios at a time.`);
                return current;
            }
            return [
                ...current,
                {
                    ...portfolio,
                    id: `comparison-${Date.now()}-${current.length}`,
                    assets: cloneAssets(portfolio.assets),
                    strategyParams: portfolio.strategyParams
                        ? { ...portfolio.strategyParams }
                        : undefined,
                },
            ];
        });
    };

    const handleAddCurrentPortfolioToComparison = () => {
        if (!isAllocationStrategy || !allocationIsBalanced) {
            toast.error("Add a balanced allocation portfolio before comparing.");
            return;
        }

        addComparisonPortfolio({
            label: buildPortfolioLabel(portfolioAssets),
            strategy: strategy as "NoRebalance" | "Rebalance",
            assets: portfolioAssets,
            strategyParams: buildPortfolioStrategyParams(
                strategy as "NoRebalance" | "Rebalance",
                params,
            ),
            source: "current",
        });
    };

    const handleAddPresetToComparison = (preset: PortfolioPreset) => {
        addComparisonPortfolio({
            label: preset.label,
            strategy: preset.strategy,
            assets: preset.assets,
            strategyParams: buildPortfolioStrategyParams(preset.strategy, {
                rebal_interval:
                    preset.rebalInterval ??
                    STRATEGY_FALLBACK_PARAMS.Rebalance.rebal_interval,
            }),
            source: "preset",
        });
    };

    const handleAddSavedToComparison = (portfolio: SavedPortfolio) => {
        addComparisonPortfolio({
            label: portfolio.label,
            strategy: portfolio.strategy,
            assets: portfolio.assets,
            strategyParams: portfolio.strategyParams,
            source: "saved",
        });
    };

    const removeComparisonPortfolio = (id: string) => {
        setComparisonPortfolios((current) => current.filter((portfolio) => portfolio.id !== id));
    };

    const handleRunComparison = () => {
        if (comparisonPortfolios.length < 2) {
            toast.error("Add at least two portfolios to compare.");
            return;
        }
        comparisonMutation.mutate(comparisonPortfolios);
    };

    useEffect(() => {
        try {
            const raw = localStorage.getItem(SAVED_PORTFOLIOS_KEY);
            if (raw) {
                setSavedPortfolios(JSON.parse(raw) as SavedPortfolio[]);
            }
        } catch {
            setSavedPortfolios([]);
        }

        const encodedConfig = new URLSearchParams(window.location.search).get("config");
        if (encodedConfig) {
            const sharedRequest = decodeSharedConfig(encodedConfig);
            if (sharedRequest) {
                applyBacktestRequestToForm(sharedRequest);
                toast.success("Shared backtest configuration loaded");
            }
        }
        // Shared links and local portfolios should hydrate only once.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    useEffect(() => {
        localStorage.setItem(SAVED_PORTFOLIOS_KEY, JSON.stringify(savedPortfolios));
    }, [savedPortfolios]);

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

    const handleExportReturnsCsv = () => {
        const rows = [...monthlyReturns, ...annualReturns];
        if (rows.length === 0) {
            toast.error("No return tables are available for this run.");
            return;
        }

        downloadFile(
            buildCsv(
                rows.map((row) => ({
                    period: row.period,
                    start_value: row.start_value,
                    end_value: row.end_value,
                    return_pct: row.return_pct,
                })),
                ["period", "start_value", "end_value", "return_pct"],
            ),
            `${buildExportBaseName(lastRunRequest)}-returns.csv`,
            "text/csv;charset=utf-8",
        );
        toast.success("Returns CSV exported");
    };

    const handleExportTradesCsv = () => {
        if (!result?.trades || result.trades.length === 0) {
            toast.error("No trades are available for this run.");
            return;
        }

        downloadFile(
            buildCsv(result.trades as unknown as Array<Record<string, unknown>>, [
                "date",
                "ticker",
                "action",
                "size",
                "price",
                "value",
            ]),
            `${buildExportBaseName(lastRunRequest)}-trades.csv`,
            "text/csv;charset=utf-8",
        );
        toast.success("Trades CSV exported");
    };

    const handleExportComparisonCsv = () => {
        const rows = comparisonRuns.map((run) => ({
            portfolio: run.portfolio.label,
            status: run.error ? "error" : "complete",
            ending_value: getEndingValue(run.result ?? undefined),
            cagr: getNumericStat(run.result?.stats, "CAGR"),
            roi: getNumericStat(run.result?.stats, "ROI"),
            sharpe: getNumericStat(run.result?.stats, "Sharpe"),
            max_drawdown: getNumericStat(run.result?.stats, "Max Drawdown"),
            error: run.error ?? "",
        }));

        if (rows.length === 0) {
            toast.error("Run a portfolio comparison before exporting.");
            return;
        }

        downloadFile(
            buildCsv(rows, [
                "portfolio",
                "status",
                "ending_value",
                "cagr",
                "roi",
                "sharpe",
                "max_drawdown",
                "error",
            ]),
            `${buildExportBaseName(lastComparisonRequest ?? lastRunRequest)}-comparison.csv`,
            "text/csv;charset=utf-8",
        );
        toast.success("Comparison CSV exported");
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
    const resultSummaryRequest = result ? lastRunRequest : lastComparisonRequest;
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
    const visiblePortfolioChartSeries = comparisonChartSeries.filter((series) => {
        if (series.name === "Portfolio") {
            return showPortfolioSeries;
        }
        return showBenchmarkSeries;
    });
    const normalizedCurrentCostAssumptions: BacktestCostAssumptions = {
        ...costAssumptions,
        commission_per_share: Number(costAssumptions.commission_per_share),
        commission_bps: Number(costAssumptions.commission_bps),
        commission_minimum: Number(costAssumptions.commission_minimum),
        spread_bps: Number(costAssumptions.spread_bps),
        slippage_bps: Number(costAssumptions.slippage_bps),
    };
    const currentInputSignature = normalizeRequestForSignature(
        (() => {
            const strategyParams: Record<string, unknown> = { ...params };
            let currentTickers = [ticker.trim().toUpperCase()];
            const currentRecurringCashflows: RecurringCashflowRule[] = [];
            const currentOneTimeCashflows = oneTimeCashflows
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

            if (isAllocationStrategy) {
                const cleanedAssets = cloneAssets(portfolioAssets).filter(
                    (asset) => asset.ticker.length > 0,
                );
                currentTickers = cleanedAssets.map((asset) => asset.ticker);
                const currentWeights = cleanedAssets.map((asset) => asset.weight / 100);
                if (strategy === "NoRebalance") {
                    strategyParams.equity_proportions = currentWeights;
                }
                if (strategy === "Rebalance") {
                    strategyParams.rebal_proportions = currentWeights;
                }
            } else if (needsMultiAsset) {
                currentTickers = [ticker.trim().toUpperCase(), altTicker.trim().toUpperCase()];
            }

            if (recurringContribution > 0) {
                currentRecurringCashflows.push({
                    amount: recurringContribution,
                    frequency: contributionFrequency,
                    start_date: startDate,
                    end_date: endDate,
                    label: `Recurring contribution (${contributionFrequency})`,
                });
            }
            if (recurringWithdrawal > 0) {
                currentRecurringCashflows.push({
                    amount: -recurringWithdrawal,
                    frequency: withdrawalFrequency,
                    start_date: startDate,
                    end_date: endDate,
                    label: `Recurring withdrawal (${withdrawalFrequency})`,
                });
            }

            return {
                tickers: currentTickers,
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
                    currentRecurringCashflows.length > 0
                        ? currentRecurringCashflows
                        : undefined,
                one_time_cashflows:
                    currentOneTimeCashflows.length > 0
                        ? currentOneTimeCashflows
                        : undefined,
                inflation_rate: inflationRate,
                missing_data_policy: missingDataPolicy,
                cost_assumptions: normalizedCurrentCostAssumptions,
            };
        })(),
    );
    const lastRunInputSignature = normalizeRequestForSignature(lastRunRequest);
    const hasStaleResults =
        Boolean(result && lastRunInputSignature && currentInputSignature !== lastRunInputSignature);
    const comparisonRows = comparisonRuns.map((run) => ({
        portfolio: run.portfolio.label,
        status: run.error ? "Error" : "Complete",
        ending_value: getEndingValue(run.result ?? undefined),
        cagr: getNumericStat(run.result?.stats, "CAGR"),
        roi: getNumericStat(run.result?.stats, "ROI"),
        sharpe: getNumericStat(run.result?.stats, "Sharpe"),
        max_drawdown: getNumericStat(run.result?.stats, "Max Drawdown"),
        error: run.error ?? "",
    }));
    const comparisonResultSeries = comparisonRuns
        .filter((run) => run.result?.value_history?.length)
        .map((run, index) => ({
            name: run.portfolio.label,
            dates: run.result?.value_history.map((row) => String(row.date)) ?? [],
            values:
                run.result?.value_history.map((row) => {
                    const firstValue = run.result?.value_history[0]?.Value;
                    const currentValue = row.Value;
                    if (
                        typeof firstValue === "number" &&
                        firstValue !== 0 &&
                        typeof currentValue === "number"
                    ) {
                        return (currentValue / firstValue) * 100;
                    }
                    return null;
                }) ?? [],
            color:
                index === 0
                    ? "#3b82f6"
                    : index === 1
                      ? "#22c55e"
                      : index === 2
                        ? "#f97316"
                        : index === 3
                          ? "#a855f7"
                          : "#06b6d4",
        }));
    const comparisonDrawdownSeries = comparisonResultSeries.map((series) => ({
        ...series,
        values: buildDrawdownValues(series.values),
    }));
    const hasResultWorkspace = Boolean(stats || comparisonRuns.length > 0);

    return (
        <div className="space-y-8">
            <PageHeader
                title="Strategy Backtester"
                description="Run allocation backtests or trading strategies on historical data"
                actions={
                    <>
                        <Button
                            type="button"
                            variant="outline"
                            onClick={handleShareConfig}
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
                                onClick={handleExportCsv}
                            >
                                <Download className="h-3.5 w-3.5" />
                                Export CSV
                            </Button>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={handleExportReturnsCsv}
                            >
                                <Download className="h-3.5 w-3.5" />
                                Returns
                            </Button>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={handleExportTradesCsv}
                            >
                                <Download className="h-3.5 w-3.5" />
                                Trades
                            </Button>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={handleExportJson}
                            >
                                <Download className="h-3.5 w-3.5" />
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
                        ) : null}
                    </>
                }
            />

            <ToolLayout
                configPanel={
                    <ConfigPanel title="Configuration">
                        <ConfigSection
                            title="Strategy"
                            description="Select the backtest template and review its default behavior."
                            summary={strategy}
                        >
                            <div className="space-y-2 lg:col-span-2">
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
                                            <SelectItem
                                                key={s.name}
                                                value={s.name}
                                            >
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
                        </ConfigSection>

                        {isAllocationStrategy ? (
                            <ConfigSection
                                title="Portfolio"
                                description="Build or load the allocation that will be tested."
                                summary={
                                    <>
                                        <span>
                                            {portfolioAssets
                                                .map((asset) => asset.ticker)
                                                .join(", ")}
                                        </span>
                                        <span
                                            className={cn(
                                                allocationIsBalanced
                                                    ? "text-emerald-600 dark:text-emerald-400"
                                                    : "text-amber-600 dark:text-amber-400",
                                            )}
                                        >
                                            {formatNumber(
                                                allocationWeightTotal,
                                                1,
                                            )}
                                            %
                                        </span>
                                    </>
                                }
                            >
                                <div className="space-y-3 lg:col-span-5">
                                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                                        <Label className="text-xs text-muted-foreground">
                                            Preset Portfolios
                                        </Label>
                                        <Input
                                            value={presetFilter}
                                            onChange={(event) =>
                                                setPresetFilter(
                                                    event.target.value,
                                                )
                                            }
                                            placeholder="Search presets or tickers"
                                            className="h-8 border-border/50 bg-background/50 text-xs sm:max-w-64"
                                        />
                                    </div>
                                    <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-5">
                                        {filteredPortfolioPresets.map((preset) => (
                                            <div
                                                key={preset.label}
                                                data-testid={`portfolio-preset-${preset.id}`}
                                                className="rounded-lg border border-border/50 bg-card/40 p-3"
                                            >
                                                <div className="flex items-start justify-between gap-2">
                                                    <div className="min-w-0">
                                                        <p className="truncate text-sm font-semibold text-foreground">
                                                            {preset.label}
                                                        </p>
                                                        <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-muted-foreground">
                                                            {preset.description}
                                                        </p>
                                                    </div>
                                                    <span className="shrink-0 rounded-md border border-border/50 px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
                                                        {preset.assumption}
                                                    </span>
                                                </div>
                                                <p className="mt-2 text-[11px] text-muted-foreground/80">
                                                    {preset.assets
                                                        .map(
                                                            (asset) =>
                                                                `${asset.ticker} ${formatNumber(asset.weight, 0)}%`,
                                                        )
                                                        .join(" / ")}
                                                </p>
                                                <div className="mt-3 flex flex-wrap gap-2">
                                                    <Button
                                                        type="button"
                                                        variant="outline"
                                                        size="xs"
                                                        onClick={() =>
                                                            applyPortfolioPreset(
                                                                preset,
                                                            )
                                                        }
                                                    >
                                                        Load
                                                    </Button>
                                                    <Button
                                                        type="button"
                                                        variant="ghost"
                                                        size="xs"
                                                        onClick={() =>
                                                            handleAddPresetToComparison(
                                                                preset,
                                                            )
                                                        }
                                                    >
                                                        <Plus />
                                                        Compare
                                                    </Button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div className="space-y-3 lg:col-span-3 xl:col-span-4">
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
                                                onClick={
                                                    normalizePortfolioWeights
                                                }
                                            >
                                                Normalize
                                            </Button>
                                            <Button
                                                type="button"
                                                variant="ghost"
                                                size="xs"
                                                onClick={clearPortfolioAssets}
                                            >
                                                Clear
                                            </Button>
                                            <Button
                                                type="button"
                                                variant="outline"
                                                size="xs"
                                                onClick={handleSavePortfolio}
                                            >
                                                <Save />
                                                Save
                                            </Button>
                                            <Button
                                                type="button"
                                                variant="outline"
                                                size="xs"
                                                onClick={
                                                    handleAddCurrentPortfolioToComparison
                                                }
                                            >
                                                <Plus />
                                                Compare
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
                                                className="grid grid-cols-1 gap-2 sm:grid-cols-[minmax(0,1fr)_96px_auto]"
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

                                {(savedPortfolios.length > 0 ||
                                    comparisonPortfolios.length > 0) && (
                                    <div className="grid grid-cols-1 gap-4 lg:col-span-5 xl:grid-cols-2">
                                        {savedPortfolios.length > 0 && (
                                            <div className="rounded-lg border border-border/50 bg-background/30 p-3">
                                                <div className="mb-3 flex items-center justify-between gap-3">
                                                    <Label className="text-xs text-muted-foreground">
                                                        Saved Portfolios
                                                    </Label>
                                                    <span className="text-[11px] text-muted-foreground/70">
                                                        {savedPortfolios.length}
                                                    </span>
                                                </div>
                                                <div className="space-y-2">
                                                    {savedPortfolios.map(
                                                        (saved) => (
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
                                                                        onClick={() =>
                                                                            applySavedPortfolio(
                                                                                saved,
                                                                            )
                                                                        }
                                                                    >
                                                                        Load
                                                                    </Button>
                                                                    <Button
                                                                        type="button"
                                                                        variant="ghost"
                                                                        size="xs"
                                                                        onClick={() =>
                                                                            handleAddSavedToComparison(
                                                                                saved,
                                                                            )
                                                                        }
                                                                    >
                                                                        Compare
                                                                    </Button>
                                                                    <Button
                                                                        type="button"
                                                                        variant="ghost"
                                                                        size="icon-xs"
                                                                        onClick={() =>
                                                                            removeSavedPortfolio(
                                                                                saved.id,
                                                                            )
                                                                        }
                                                                        aria-label={`Remove ${saved.label}`}
                                                                    >
                                                                        <X />
                                                                    </Button>
                                                                </div>
                                                            </div>
                                                        ),
                                                    )}
                                                </div>
                                            </div>
                                        )}

                                        {comparisonPortfolios.length > 0 && (
                                            <div className="rounded-lg border border-border/50 bg-background/30 p-3">
                                                <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                                                    <div>
                                                        <Label className="text-xs text-muted-foreground">
                                                            Comparison Queue
                                                        </Label>
                                                        <p className="text-[11px] text-muted-foreground/70">
                                                            Shared dates,
                                                            cashflows,
                                                            costs, and data
                                                            policy.
                                                        </p>
                                                    </div>
                                                    <Button
                                                        type="button"
                                                        variant="outline"
                                                        size="xs"
                                                        onClick={
                                                            handleRunComparison
                                                        }
                                                        disabled={
                                                            comparisonMutation.isPending ||
                                                            comparisonPortfolios.length <
                                                                2
                                                        }
                                                    >
                                                        <BarChart3 />
                                                        {comparisonMutation.isPending
                                                            ? "Comparing..."
                                                            : "Run Comparison"}
                                                    </Button>
                                                </div>
                                                <div className="space-y-2">
                                                    {comparisonPortfolios.map(
                                                        (portfolio) => (
                                                            <div
                                                                key={
                                                                    portfolio.id
                                                                }
                                                                className="flex items-center justify-between gap-3 rounded-md border border-border/40 bg-card/30 p-2"
                                                            >
                                                                <div className="min-w-0">
                                                                    <p className="truncate text-xs font-medium text-foreground">
                                                                        {
                                                                            portfolio.label
                                                                        }
                                                                    </p>
                                                                    <p className="text-[11px] text-muted-foreground/70">
                                                                        {
                                                                            portfolio.strategy
                                                                        }{" "}
                                                                        /{" "}
                                                                        {
                                                                            portfolio.source
                                                                        }
                                                                    </p>
                                                                </div>
                                                                <Button
                                                                    type="button"
                                                                    variant="ghost"
                                                                    size="icon-xs"
                                                                    onClick={() =>
                                                                        removeComparisonPortfolio(
                                                                            portfolio.id,
                                                                        )
                                                                    }
                                                                    aria-label={`Remove ${portfolio.label}`}
                                                                >
                                                                    <X />
                                                                </Button>
                                                            </div>
                                                        ),
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </ConfigSection>
                        ) : (
                            <ConfigSection
                                title="Assets"
                                description="Choose the instruments used by this strategy."
                                defaultOpen={false}
                                summary={
                                    needsMultiAsset
                                        ? `${ticker}, ${altTicker}`
                                        : ticker
                                }
                            >
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
                            </ConfigSection>
                        )}

                        <ConfigSection
                            title="Run setup"
                            description="Set the date window, capital base, benchmark, and risk-free rate."
                            defaultOpen={false}
                            summary={`${startDate} to ${endDate} / $${formatNumber(cash, 0)}`}
                        >
                        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:col-span-2">
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
                        </ConfigSection>

                        <ConfigSection
                            title="Data and execution assumptions"
                            description="Surface the gap-handling policy and estimated trade frictions used to contextualize this run."
                            defaultOpen={false}
                            summary={`${
                                MISSING_DATA_POLICY_OPTIONS.find(
                                    (option) =>
                                        option.value === missingDataPolicy,
                                )?.label ?? missingDataPolicy
                            } / ${costAssumptions.commission_mode}`}
                        >
                            <div className="space-y-2 lg:col-span-2">
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
                                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
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
                                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
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

                            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:col-span-2">
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
                        </ConfigSection>

                        <ConfigSection
                            title="Cashflow planning"
                            description="Model recurring savings, portfolio-funded withdrawals, and dated one-off events in the same backtest run."
                            summary={
                                recurringContribution ||
                                recurringWithdrawal ||
                                oneTimeCashflows.length
                                    ? `${oneTimeCashflows.length} one-time event${
                                          oneTimeCashflows.length === 1
                                              ? ""
                                              : "s"
                                      }`
                                    : "No cashflows"
                            }
                        >
                            <div className="grid grid-cols-1 gap-2 sm:grid-cols-[minmax(0,1fr)_132px] lg:col-span-2">
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

                            <div className="grid grid-cols-1 gap-2 sm:grid-cols-[minmax(0,1fr)_132px] lg:col-span-2">
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

                            <div className="space-y-2 lg:col-span-2">
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
                                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
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
                                                    className="grid grid-cols-1 gap-2 sm:grid-cols-[132px_minmax(0,1fr)_minmax(0,1fr)_auto]"
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
                                                        aria-label={`Date for cashflow event ${index + 1}`}
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
                                                        aria-label={`Amount for cashflow event ${index + 1}`}
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
                                                        aria-label={`Label for cashflow event ${index + 1}`}
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
                        </ConfigSection>

                        {/* Dynamic strategy params */}
                        {currentStrategy && currentStrategy.params.length > 0 ? (
                            <ConfigSection
                                title="Strategy parameters"
                                description="Fine-tune the selected strategy's numeric inputs."
                                defaultOpen={false}
                            >
                                {currentStrategy.params.map((p) => (
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
                                                    [p.name]: Number(
                                                        e.target.value,
                                                    ),
                                                }))
                                            }
                                            className="border-border/50 bg-background/50"
                                        />
                                    </div>
                                ))}
                            </ConfigSection>
                        ) : null}

                        <div className="col-span-full flex justify-end border-t border-border/40 pt-4">
                            <div className="w-full sm:w-auto sm:min-w-48">
                                <Button
                                    className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
                                    onClick={handleRun}
                                    disabled={mutation.isPending}
                                >
                                    {mutation.isPending
                                        ? "Running..."
                                        : "Run Backtest"}
                                </Button>
                            </div>
                        </div>
                    </ConfigPanel>
                }
            >
                {mutation.isPending && (
                    <>
                        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                            <CardSkeleton />
                            <CardSkeleton />
                            <CardSkeleton />
                            <CardSkeleton />
                        </div>
                        <ChartSkeleton />
                    </>
                )}

                {hasResultWorkspace && (
                    <>
                        {/* Metric cards */}
                        {stats && (
                            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
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
                        )}

                        <div className="sticky top-16 z-20 rounded-lg border border-border/60 bg-background/90 p-3 shadow-sm backdrop-blur-xl">
                            <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                                <div className="min-w-0">
                                    <div className="flex flex-wrap items-center gap-2">
                                        <p className="truncate text-sm font-semibold text-foreground">
                                            <span data-testid="backtest-result-summary-title">
                                            {resultSummaryRequest?.tickers.join(" / ") ??
                                                "Portfolio comparison"}
                                            </span>
                                        </p>
                                        {resultSummaryRequest?.strategy && (
                                            <span className="rounded-md border border-border/60 bg-muted/30 px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
                                                {resultSummaryRequest.strategy}
                                            </span>
                                        )}
                                        {hasStaleResults && (
                                            <span className="rounded-md border border-amber-500/40 bg-amber-500/10 px-2 py-0.5 text-[11px] font-medium text-amber-600 dark:text-amber-300">
                                                Inputs changed
                                            </span>
                                        )}
                                    </div>
                                    <p className="mt-1 text-xs text-muted-foreground">
                                        {result
                                            ? `${lastRunRequest?.start_date} to ${lastRunRequest?.end_date} / ${formatCurrencyPrecise(getEndingValue(result))} ending value`
                                            : `${comparisonRuns.length} portfolio${comparisonRuns.length === 1 ? "" : "s"} compared with shared dates, cashflows, costs, and data policy`}
                                    </p>
                                </div>
                                <Tabs
                                    value={activeResultTab}
                                    onValueChange={setActiveResultTab}
                                    className="min-w-0"
                                >
                                    <TabsList>
                                        <TabsTrigger value="overview">
                                            Overview
                                        </TabsTrigger>
                                        <TabsTrigger value="comparison">
                                            Compare
                                        </TabsTrigger>
                                        <TabsTrigger value="audit">
                                            Audit
                                        </TabsTrigger>
                                        <TabsTrigger value="cashflows">
                                            Cashflows
                                        </TabsTrigger>
                                        <TabsTrigger value="diagnostics">
                                            Diagnostics
                                        </TabsTrigger>
                                        <TabsTrigger value="returns">
                                            Returns
                                        </TabsTrigger>
                                    </TabsList>
                                </Tabs>
                            </div>
                        </div>

                        {activeResultTab === "audit" && savedExperiment && (
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

                        {activeResultTab === "audit" &&
                            costSummary &&
                            appliedCostAssumptions && (
                            <>
                                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
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

                        {activeResultTab === "audit" && missingDataSummary && (
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
                                    initialRows={8}
                                />
                            </ChartCard>
                        )}

                        {activeResultTab === "audit" && walkForwardRequest && (
                            <ChartCard title="Walk-Forward Follow-Up">
                                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
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

                        {activeResultTab === "audit" && (
                            <ChartCard title="Metric Methodology">
                                <DataTable
                                    columns={[
                                        { key: "metric", label: "Metric" },
                                        { key: "basis", label: "Calculation Basis" },
                                    ]}
                                    data={[
                                        {
                                            metric: "Max Drawdown",
                                            basis: "Peak-to-trough decline computed directly from the portfolio value path. This matches the drawdown chart.",
                                        },
                                        {
                                            metric: "CAGR",
                                            basis: "Annualized compound growth from starting value, ending value, and elapsed trading history.",
                                        },
                                        {
                                            metric: "Sharpe",
                                            basis: "QuantStats daily-return ratio derived from the same portfolio value history.",
                                        },
                                        {
                                            metric: "ROI",
                                            basis: "Ending value divided by starting value minus one.",
                                        },
                                    ]}
                                />
                            </ChartCard>
                        )}

                        {activeResultTab === "cashflows" && withdrawalDurability && (
                            <>
                                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
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
                                            initialRows={12}
                                        />
                                    </ChartCard>
                                )}
                            </>
                        )}

                        {activeResultTab === "overview" && benchmarkStats && (
                            <>
                                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
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

                                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
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

                        {activeResultTab === "overview" &&
                            benchmarkStats &&
                            comparisonChartSeries.length > 0 && (
                            <ChartCard
                                title={
                                    benchmarkStats
                                        ? `Portfolio vs ${benchmarkStats.benchmark_name}`
                                        : "Portfolio Value"
                                }
                                action={
                                    <>
                                        <Button
                                            type="button"
                                            variant="outline"
                                            size="xs"
                                            onClick={() =>
                                                setShowPortfolioSeries(
                                                    (value) => !value,
                                                )
                                            }
                                        >
                                            {showPortfolioSeries ? (
                                                <Eye className="h-3.5 w-3.5" />
                                            ) : (
                                                <EyeOff className="h-3.5 w-3.5" />
                                            )}
                                            Portfolio
                                        </Button>
                                        <Button
                                            type="button"
                                            variant="outline"
                                            size="xs"
                                            onClick={() =>
                                                setShowBenchmarkSeries(
                                                    (value) => !value,
                                                )
                                            }
                                        >
                                            {showBenchmarkSeries ? (
                                                <Eye className="h-3.5 w-3.5" />
                                            ) : (
                                                <EyeOff className="h-3.5 w-3.5" />
                                            )}
                                            Benchmark
                                        </Button>
                                        <Button
                                            type="button"
                                            variant="outline"
                                            size="xs"
                                            onClick={() =>
                                                setPortfolioChartLogScale(
                                                    (value) => !value,
                                                )
                                            }
                                        >
                                            <LineChart className="h-3.5 w-3.5" />
                                            {portfolioChartLogScale
                                                ? "Linear"
                                                : "Log"}
                                        </Button>
                                    </>
                                }
                            >
                                <LightweightChart
                                    series={visiblePortfolioChartSeries}
                                    height={400}
                                    type={benchmarkStats ? "line" : "area"}
                                    logScale={portfolioChartLogScale}
                                    downloadImageName={`${buildExportBaseName(lastRunRequest)}-portfolio`}
                                />
                            </ChartCard>
                        )}

                        {/* Portfolio value chart */}
                        {activeResultTab === "overview" &&
                            result?.value_history &&
                            !benchmarkStats &&
                            result.value_history.length > 0 && (
                                <ChartCard
                                    title="Portfolio Value"
                                    action={
                                        <Button
                                            type="button"
                                            variant="outline"
                                            size="xs"
                                            onClick={() =>
                                                setPortfolioChartLogScale(
                                                    (value) => !value,
                                                )
                                            }
                                        >
                                            <LineChart className="h-3.5 w-3.5" />
                                            {portfolioChartLogScale
                                                ? "Linear"
                                                : "Log"}
                                        </Button>
                                    }
                                >
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
                                        logScale={portfolioChartLogScale}
                                        downloadImageName={`${buildExportBaseName(lastRunRequest)}-portfolio`}
                                    />
                                </ChartCard>
                            )}

                        {/* Drawdown chart */}
                        {activeResultTab === "overview" &&
                            result?.value_history &&
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
                        {activeResultTab === "overview" && benchmarkStats && (
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

                        {activeResultTab === "diagnostics" && rollingMetrics && (
                            <>
                                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
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

                        {activeResultTab === "diagnostics" &&
                            regimeSummary.length > 0 && (
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

                        {activeResultTab === "diagnostics" &&
                            regimePeriods.length > 0 && (
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
                                    initialRows={10}
                                />
                            </ChartCard>
                        )}

                        {activeResultTab === "diagnostics" &&
                            allocationChartData.length > 0 && (
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

                        {activeResultTab === "diagnostics" &&
                            rebalanceEvents.length > 0 && (
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
                                    initialRows={12}
                                />
                            </ChartCard>
                        )}

                        {activeResultTab === "comparison" && (
                            <>
                                {comparisonRuns.length > 0 ? (
                                    <>
                                        <ChartCard
                                            title="Portfolio Comparison"
                                            action={
                                                <Button
                                                    type="button"
                                                    variant="outline"
                                                    size="xs"
                                                    onClick={
                                                        handleExportComparisonCsv
                                                    }
                                                >
                                                    <Download className="h-3.5 w-3.5" />
                                                    CSV
                                                </Button>
                                            }
                                        >
                                            {comparisonResultSeries.length >
                                            0 ? (
                                                <LightweightChart
                                                    series={
                                                        comparisonResultSeries
                                                    }
                                                    height={400}
                                                    type="line"
                                                    downloadImageName={`${buildExportBaseName(lastComparisonRequest ?? lastRunRequest)}-comparison`}
                                                />
                                            ) : (
                                                <p className="text-sm text-muted-foreground">
                                                    No successful comparison
                                                    series are available.
                                                </p>
                                            )}
                                        </ChartCard>

                                        <ChartCard title="Comparison Drawdown">
                                            {comparisonDrawdownSeries.length >
                                            0 ? (
                                                <LightweightChart
                                                    series={
                                                        comparisonDrawdownSeries
                                                    }
                                                    height={300}
                                                    type="line"
                                                    downloadImageName={`${buildExportBaseName(lastComparisonRequest ?? lastRunRequest)}-comparison-drawdown`}
                                                />
                                            ) : (
                                                <p className="text-sm text-muted-foreground">
                                                    No successful comparison
                                                    drawdown series are
                                                    available.
                                                </p>
                                            )}
                                        </ChartCard>

                                        <ChartCard title="Comparison Metrics">
                                            <DataTable
                                                columns={[
                                                    {
                                                        key: "portfolio",
                                                        label: "Portfolio",
                                                    },
                                                    {
                                                        key: "status",
                                                        label: "Status",
                                                    },
                                                    {
                                                        key: "ending_value",
                                                        label: "Ending Value",
                                                        format: (value) =>
                                                            formatCurrencyPrecise(
                                                                value as
                                                                    | number
                                                                    | null,
                                                            ),
                                                    },
                                                    {
                                                        key: "cagr",
                                                        label: "CAGR",
                                                        format: (value) =>
                                                            formatPercent(
                                                                value as
                                                                    | number
                                                                    | null,
                                                            ),
                                                    },
                                                    {
                                                        key: "roi",
                                                        label: "ROI",
                                                        format: (value) =>
                                                            formatPercent(
                                                                value as
                                                                    | number
                                                                    | null,
                                                            ),
                                                    },
                                                    {
                                                        key: "sharpe",
                                                        label: "Sharpe",
                                                        format: (value) =>
                                                            formatNumber(
                                                                value as
                                                                    | number
                                                                    | null,
                                                                3,
                                                            ),
                                                    },
                                                    {
                                                        key: "max_drawdown",
                                                        label: "Max Drawdown",
                                                        format: (value) =>
                                                            formatPercent(
                                                                value as
                                                                    | number
                                                                    | null,
                                                            ),
                                                    },
                                                    {
                                                        key: "error",
                                                        label: "Error",
                                                    },
                                                ]}
                                                data={comparisonRows}
                                            />
                                        </ChartCard>

                                        <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
                                            {comparisonRuns.map((run) => (
                                                <ChartCard
                                                    key={run.portfolio.id}
                                                    title={`${run.portfolio.label} Details`}
                                                >
                                                    {run.error ? (
                                                        <InlineError
                                                            message={run.error}
                                                        />
                                                    ) : (
                                                        <DataTable
                                                            columns={[
                                                                {
                                                                    key: "field",
                                                                    label: "Field",
                                                                },
                                                                {
                                                                    key: "value",
                                                                    label: "Value",
                                                                },
                                                            ]}
                                                            data={[
                                                                {
                                                                    field: "Tickers",
                                                                    value:
                                                                        run.request?.tickers.join(
                                                                            ", ",
                                                                        ) ??
                                                                        "",
                                                                },
                                                                {
                                                                    field: "Strategy",
                                                                    value:
                                                                        run.request
                                                                            ?.strategy ??
                                                                        "",
                                                                },
                                                                {
                                                                    field: "Ending Value",
                                                                    value: formatCurrencyPrecise(
                                                                        getEndingValue(
                                                                            run.result ??
                                                                                undefined,
                                                                        ),
                                                                    ),
                                                                },
                                                                ...Object.entries(
                                                                    run.result
                                                                        ?.stats ??
                                                                        {},
                                                                ).map(
                                                                    ([
                                                                        key,
                                                                        value,
                                                                    ]) => ({
                                                                        field: key,
                                                                        value:
                                                                            typeof value ===
                                                                            "number"
                                                                                ? key ===
                                                                                      "Sharpe" ||
                                                                                  key ===
                                                                                      "Smart Sharpe"
                                                                                    ? formatNumber(
                                                                                          value,
                                                                                          4,
                                                                                      )
                                                                                    : value <
                                                                                            1 &&
                                                                                        value >
                                                                                            -1
                                                                                      ? formatPercent(
                                                                                            value,
                                                                                        )
                                                                                      : formatNumber(
                                                                                            value,
                                                                                            4,
                                                                                        )
                                                                                : String(
                                                                                      value ??
                                                                                          "N/A",
                                                                                  ),
                                                                    }),
                                                                ),
                                                            ]}
                                                            initialRows={8}
                                                        />
                                                    )}
                                                </ChartCard>
                                            ))}
                                        </div>
                                    </>
                                ) : (
                                    <EmptyState
                                        icon={BarChart3}
                                        message="Add two or more portfolios in the portfolio builder, then run a comparison."
                                    />
                                )}
                            </>
                        )}

                        {activeResultTab === "returns" && monthlyReturns.length > 0 && (
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
                                    initialRows={12}
                                />
                            </ChartCard>
                        )}

                        {activeResultTab === "returns" && annualReturns.length > 0 && (
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
                                    initialRows={12}
                                />
                            </ChartCard>
                        )}

                        {/* Trades table */}
                        {activeResultTab === "returns" &&
                            result?.trades &&
                            result.trades.length > 0 && (
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
                                    initialRows={15}
                                />
                            </ChartCard>
                        )}

                        {/* Full statistics */}
                        {activeResultTab === "audit" && stats && (
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
                                initialRows={18}
                            />
                        </ChartCard>
                        )}
                    </>
                )}

                {mutation.isError && (
                    <InlineError
                        message={mutation.error?.message ?? "Backtest failed"}
                        onRetry={handleRun}
                    />
                )}

                {!mutation.isPending &&
                    !mutation.isError &&
                    !result &&
                    comparisonRuns.length === 0 && (
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
