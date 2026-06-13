import type { MissingDataPolicy } from "@/types/api";
import type { PortfolioAsset } from "@/stores/backtest-store";

export const MAX_COMPARISON_PORTFOLIOS = 5;

export interface PortfolioPreset {
    id: string;
    label: string;
    description: string;
    category: "Core" | "Diversified" | "Defensive" | "Tactical";
    assumption: "live/local" | "simulated" | "proxy" | "unavailable";
    strategy: "NoRebalance" | "Rebalance";
    assets: PortfolioAsset[];
    rebalInterval?: number;
}

export const PORTFOLIO_PRESETS: PortfolioPreset[] = [
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

export const STRATEGY_FALLBACK_PARAMS: Record<string, Record<string, number>> = {
    Rebalance: { rebal_interval: 63 },
    SMACrossover: { fast_ma: 50, slow_ma: 200 },
};

export const CASHFLOW_FREQUENCY_OPTIONS = [
    { label: "Monthly", value: "monthly" },
    { label: "Quarterly", value: "quarterly" },
    { label: "Yearly", value: "yearly" },
] as const;

export const MISSING_DATA_POLICY_OPTIONS: Array<{
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

export const COMMISSION_MODE_OPTIONS = [
    { label: "None", value: "none" },
    { label: "Per Share", value: "per_share" },
    { label: "Percentage", value: "percentage" },
] as const;
