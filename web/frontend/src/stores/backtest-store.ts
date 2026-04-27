import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
    BacktestCostAssumptions,
    MissingDataPolicy,
    OneTimeCashflowEvent,
    RecurringCashflowRule,
    BacktestRequest,
    SaveExperimentResponse,
    BacktestResponse,
} from "@/types/api";

export interface PortfolioAsset {
    ticker: string;
    weight: number;
}

export interface SavedPortfolio {
    id: string;
    label: string;
    strategy: "NoRebalance" | "Rebalance";
    assets: PortfolioAsset[];
    strategyParams?: Record<string, number>;
    createdAt: string;
}

export interface ComparisonPortfolio {
    id: string;
    label: string;
    strategy: "NoRebalance" | "Rebalance";
    assets: PortfolioAsset[];
    strategyParams?: Record<string, number>;
    source: "current" | "preset" | "saved";
}

export interface ComparisonRun {
    portfolio: ComparisonPortfolio;
    request: BacktestRequest | null;
    result: BacktestResponse | null;
    error?: string;
}

export const DEFAULT_COST_ASSUMPTIONS: BacktestCostAssumptions = {
    commission_mode: "none",
    commission_per_share: 0.001,
    commission_bps: 1,
    commission_minimum: 0,
    spread_bps: 0,
    slippage_bps: 0,
};

export const DEFAULT_PORTFOLIO_ASSETS: PortfolioAsset[] = [
    { ticker: "SPY", weight: 100 },
];

export interface BacktestState {
    // Basic inputs
    ticker: string;
    altTicker: string;
    portfolioAssets: PortfolioAsset[];
    strategy: string;
    startDate: string;
    endDate: string;
    cash: number;
    benchmarkTicker: string;
    riskFreeRate: number;

    // Cashflows
    recurringContribution: number;
    contributionFrequency: RecurringCashflowRule["frequency"];
    recurringWithdrawal: number;
    withdrawalFrequency: RecurringCashflowRule["frequency"];
    inflationRate: number;
    oneTimeCashflows: OneTimeCashflowEvent[];

    // Advanced Settings
    missingDataPolicy: MissingDataPolicy;
    costAssumptions: BacktestCostAssumptions;
    params: Record<string, number>;

    // Runs and Results State (Not persisted)
    lastRunRequest: BacktestRequest | null;
    lastComparisonRequest: BacktestRequest | null;
    savedExperiment: SaveExperimentResponse | null;
    activeResultTab: string;
    portfolioChartLogScale: boolean;
    showPortfolioSeries: boolean;
    showBenchmarkSeries: boolean;

    // Comparisons and Presets
    comparisonPortfolios: ComparisonPortfolio[];
    comparisonRuns: ComparisonRun[];
    savedPortfolios: SavedPortfolio[];
    presetFilter: string;

    // Actions
    setTicker: (ticker: string) => void;
    setAltTicker: (altTicker: string) => void;
    setPortfolioAssets: (assets: PortfolioAsset[] | ((current: PortfolioAsset[]) => PortfolioAsset[])) => void;
    setStrategy: (strategy: string) => void;
    setStartDate: (date: string) => void;
    setEndDate: (date: string) => void;
    setCash: (cash: number) => void;
    setBenchmarkTicker: (ticker: string) => void;
    setRiskFreeRate: (rate: number) => void;

    setRecurringContribution: (amount: number) => void;
    setContributionFrequency: (freq: RecurringCashflowRule["frequency"]) => void;
    setRecurringWithdrawal: (amount: number) => void;
    setWithdrawalFrequency: (freq: RecurringCashflowRule["frequency"]) => void;
    setInflationRate: (rate: number) => void;
    setOneTimeCashflows: (cashflows: OneTimeCashflowEvent[] | ((current: OneTimeCashflowEvent[]) => OneTimeCashflowEvent[])) => void;

    setMissingDataPolicy: (policy: MissingDataPolicy) => void;
    setCostAssumptions: (assumptions: BacktestCostAssumptions | ((current: BacktestCostAssumptions) => BacktestCostAssumptions)) => void;
    setParams: (params: Record<string, number> | ((current: Record<string, number>) => Record<string, number>)) => void;

    setLastRunRequest: (req: BacktestRequest | null) => void;
    setLastComparisonRequest: (req: BacktestRequest | null) => void;
    setSavedExperiment: (exp: SaveExperimentResponse | null) => void;
    setActiveResultTab: (tab: string) => void;
    setPortfolioChartLogScale: (logScale: boolean | ((current: boolean) => boolean)) => void;
    setShowPortfolioSeries: (show: boolean | ((current: boolean) => boolean)) => void;
    setShowBenchmarkSeries: (show: boolean | ((current: boolean) => boolean)) => void;

    setComparisonPortfolios: (portfolios: ComparisonPortfolio[] | ((current: ComparisonPortfolio[]) => ComparisonPortfolio[])) => void;
    removeComparisonPortfolio: (id: string) => void;
    setComparisonRuns: (runs: ComparisonRun[]) => void;
    setSavedPortfolios: (portfolios: SavedPortfolio[] | ((current: SavedPortfolio[]) => SavedPortfolio[])) => void;
    setPresetFilter: (filter: string) => void;

    resetForm: () => void;
}

const initialState = {
    ticker: "SPY",
    altTicker: "TLT",
    portfolioAssets: DEFAULT_PORTFOLIO_ASSETS,
    strategy: "NoRebalance",
    startDate: "2015-01-01",
    endDate: "2024-12-31",
    cash: 10000,
    benchmarkTicker: "",
    riskFreeRate: 0.04,

    recurringContribution: 0,
    contributionFrequency: "monthly" as const,
    recurringWithdrawal: 0,
    withdrawalFrequency: "monthly" as const,
    inflationRate: 0.03,
    oneTimeCashflows: [],

    missingDataPolicy: "forward_fill" as const,
    costAssumptions: DEFAULT_COST_ASSUMPTIONS,
    params: {},

    lastRunRequest: null,
    lastComparisonRequest: null,
    savedExperiment: null,
    activeResultTab: "overview",
    portfolioChartLogScale: false,
    showPortfolioSeries: true,
    showBenchmarkSeries: true,

    comparisonPortfolios: [],
    comparisonRuns: [],
    savedPortfolios: [],
    presetFilter: "",
};

export const useBacktestStore = create<BacktestState>()(
    persist(
        (set) => ({
            ...initialState,

            setTicker: (ticker) => set({ ticker }),
            setAltTicker: (altTicker) => set({ altTicker }),
            setPortfolioAssets: (assets) => set((state) => ({
                portfolioAssets: typeof assets === 'function' ? assets(state.portfolioAssets) : assets
            })),
            setStrategy: (strategy) => set({ strategy }),
            setStartDate: (startDate) => set({ startDate }),
            setEndDate: (endDate) => set({ endDate }),
            setCash: (cash) => set({ cash }),
            setBenchmarkTicker: (benchmarkTicker) => set({ benchmarkTicker }),
            setRiskFreeRate: (riskFreeRate) => set({ riskFreeRate }),

            setRecurringContribution: (recurringContribution) => set({ recurringContribution }),
            setContributionFrequency: (contributionFrequency) => set({ contributionFrequency }),
            setRecurringWithdrawal: (recurringWithdrawal) => set({ recurringWithdrawal }),
            setWithdrawalFrequency: (withdrawalFrequency) => set({ withdrawalFrequency }),
            setInflationRate: (inflationRate) => set({ inflationRate }),
            setOneTimeCashflows: (cashflows) => set((state) => ({
                oneTimeCashflows: typeof cashflows === 'function' ? cashflows(state.oneTimeCashflows) : cashflows
            })),

            setMissingDataPolicy: (missingDataPolicy) => set({ missingDataPolicy }),
            setCostAssumptions: (assumptions) => set((state) => ({
                costAssumptions: typeof assumptions === 'function' ? assumptions(state.costAssumptions) : assumptions
            })),
            setParams: (params) => set((state) => ({
                params: typeof params === 'function' ? params(state.params) : params
            })),

            setLastRunRequest: (lastRunRequest) => set({ lastRunRequest }),
            setLastComparisonRequest: (lastComparisonRequest) => set({ lastComparisonRequest }),
            setSavedExperiment: (savedExperiment) => set({ savedExperiment }),
            setActiveResultTab: (activeResultTab) => set({ activeResultTab }),
            setPortfolioChartLogScale: (logScale) => set((state) => ({
                portfolioChartLogScale: typeof logScale === 'function' ? logScale(state.portfolioChartLogScale) : logScale
            })),
            setShowPortfolioSeries: (show) => set((state) => ({
                showPortfolioSeries: typeof show === 'function' ? show(state.showPortfolioSeries) : show
            })),
            setShowBenchmarkSeries: (show) => set((state) => ({
                showBenchmarkSeries: typeof show === 'function' ? show(state.showBenchmarkSeries) : show
            })),

            setComparisonPortfolios: (portfolios) => set((state) => ({
                comparisonPortfolios: typeof portfolios === 'function' ? portfolios(state.comparisonPortfolios) : portfolios
            })),
            removeComparisonPortfolio: (id) => set((state) => ({
                comparisonPortfolios: state.comparisonPortfolios.filter(p => p.id !== id)
            })),
            setComparisonRuns: (comparisonRuns) => set({ comparisonRuns }),
            setSavedPortfolios: (portfolios) => set((state) => ({
                savedPortfolios: typeof portfolios === 'function' ? portfolios(state.savedPortfolios) : portfolios
            })),
            setPresetFilter: (presetFilter) => set({ presetFilter }),

            resetForm: () => set((state) => ({
                ...initialState,
                // Keep saved portfolios and existing comparison runs if desired, but for now reset all form inputs
                savedPortfolios: state.savedPortfolios,
            })),
        }),
        {
            name: "finbot-backtest-store",
            partialize: (state) => ({
                ticker: state.ticker,
                altTicker: state.altTicker,
                portfolioAssets: state.portfolioAssets,
                strategy: state.strategy,
                startDate: state.startDate,
                endDate: state.endDate,
                cash: state.cash,
                benchmarkTicker: state.benchmarkTicker,
                riskFreeRate: state.riskFreeRate,
                recurringContribution: state.recurringContribution,
                contributionFrequency: state.contributionFrequency,
                recurringWithdrawal: state.recurringWithdrawal,
                withdrawalFrequency: state.withdrawalFrequency,
                inflationRate: state.inflationRate,
                oneTimeCashflows: state.oneTimeCashflows,
                missingDataPolicy: state.missingDataPolicy,
                costAssumptions: state.costAssumptions,
                params: state.params,
                savedPortfolios: state.savedPortfolios,
            }),
        }
    )
);
