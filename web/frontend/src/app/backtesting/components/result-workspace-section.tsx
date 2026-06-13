"use client";

import { ResultWorkspaceSummary } from "@/app/backtesting/components/result-workspace-summary";
import { AuditTab } from "@/app/backtesting/components/audit-tab";
import { CashflowsTab } from "@/app/backtesting/components/cashflows-tab";
import {
    ComparisonResultsTab,
    type ComparisonMetricsRow,
} from "@/app/backtesting/components/comparison-results-tab";
import { DiagnosticsTab } from "@/app/backtesting/components/diagnostics-tab";
import { OverviewTab } from "@/app/backtesting/components/overview-tab";
import { ReturnsTab } from "@/app/backtesting/components/returns-tab";
import type { ComparisonRun } from "@/stores/backtest-store";
import type {
    AppliedBacktestCostAssumptions,
    BacktestBenchmarkStats,
    BacktestCostSummary,
    BacktestMissingDataSummary,
    BacktestRegimePeriod,
    BacktestRegimeSummary,
    CashflowEventRecord,
    RebalanceEventRecord,
    ReturnTableRow,
    RollingMetricsResponse,
    TimeSeries,
    TradeRecord,
    WithdrawalDurabilitySummary,
    WalkForwardHandoff,
    SaveExperimentResponse,
} from "@/types/api";

interface CostBySymbolRow extends Record<string, string | number> {
    ticker: string;
    total_cost: number;
}

interface AllocationDriftRow {
    ticker: string;
    target_weight: number;
    latest_weight: number | null;
    max_drift: number;
}

interface ResultWorkspaceSectionProps {
    stats: Record<string, unknown> | null | undefined;
    title: string;
    strategy?: string;
    detail: string;
    hasStaleResults: boolean;
    activeTab: string;
    savedExperiment: SaveExperimentResponse | null;
    costSummary: BacktestCostSummary | null | undefined;
    appliedCostAssumptions: AppliedBacktestCostAssumptions | undefined;
    costBySymbolRows: CostBySymbolRow[];
    missingDataSummary: BacktestMissingDataSummary | undefined;
    walkForwardRequest: WalkForwardHandoff | null | undefined;
    walkForwardHref: string;
    withdrawalDurability: WithdrawalDurabilitySummary | null | undefined;
    inflationAdjustedSeries: TimeSeries[];
    cashflowEvents: CashflowEventRecord[];
    benchmarkStats: BacktestBenchmarkStats | null | undefined;
    comparisonChartSeries: TimeSeries[];
    visiblePortfolioChartSeries: TimeSeries[];
    valueHistory: Record<string, unknown>[];
    portfolioChartLogScale: boolean;
    showPortfolioSeries: boolean;
    showBenchmarkSeries: boolean;
    overviewExportBaseName: string;
    rollingMetrics: RollingMetricsResponse | null | undefined;
    rollingChartData: Record<string, unknown>[];
    regimeSummary: BacktestRegimeSummary[];
    regimePeriods: BacktestRegimePeriod[];
    regimeReferenceTicker: string | null | undefined;
    allocationChartData: Record<string, unknown>[];
    allocationSeriesKeys: string[];
    allocationDriftSummary: AllocationDriftRow[];
    rebalanceEvents: RebalanceEventRecord[];
    comparisonRuns: ComparisonRun[];
    comparisonRows: ComparisonMetricsRow[];
    comparisonResultSeries: TimeSeries[];
    comparisonDrawdownSeries: TimeSeries[];
    comparisonExportBaseName: string;
    monthlyReturns: ReturnTableRow[];
    annualReturns: ReturnTableRow[];
    trades: TradeRecord[];
    onTabChange: (value: string) => void;
    onTogglePortfolioSeries: () => void;
    onToggleBenchmarkSeries: () => void;
    onToggleLogScale: () => void;
    onExportComparisonCsv: () => void;
}

export function ResultWorkspaceSection({
    stats,
    title,
    strategy,
    detail,
    hasStaleResults,
    activeTab,
    savedExperiment,
    costSummary,
    appliedCostAssumptions,
    costBySymbolRows,
    missingDataSummary,
    walkForwardRequest,
    walkForwardHref,
    withdrawalDurability,
    inflationAdjustedSeries,
    cashflowEvents,
    benchmarkStats,
    comparisonChartSeries,
    visiblePortfolioChartSeries,
    valueHistory,
    portfolioChartLogScale,
    showPortfolioSeries,
    showBenchmarkSeries,
    overviewExportBaseName,
    rollingMetrics,
    rollingChartData,
    regimeSummary,
    regimePeriods,
    regimeReferenceTicker,
    allocationChartData,
    allocationSeriesKeys,
    allocationDriftSummary,
    rebalanceEvents,
    comparisonRuns,
    comparisonRows,
    comparisonResultSeries,
    comparisonDrawdownSeries,
    comparisonExportBaseName,
    monthlyReturns,
    annualReturns,
    trades,
    onTabChange,
    onTogglePortfolioSeries,
    onToggleBenchmarkSeries,
    onToggleLogScale,
    onExportComparisonCsv,
}: ResultWorkspaceSectionProps) {
    return (
        <>
            <ResultWorkspaceSummary
                stats={stats}
                title={title}
                strategy={strategy}
                detail={detail}
                hasStaleResults={hasStaleResults}
                activeTab={activeTab}
                onTabChange={onTabChange}
            />

            {activeTab === "audit" && (
                <AuditTab
                    savedExperiment={savedExperiment}
                    costSummary={costSummary}
                    appliedCostAssumptions={appliedCostAssumptions}
                    costBySymbolRows={costBySymbolRows}
                    missingDataSummary={missingDataSummary}
                    walkForwardRequest={walkForwardRequest}
                    walkForwardHref={walkForwardHref}
                    stats={stats}
                />
            )}

            {activeTab === "cashflows" && (
                <CashflowsTab
                    withdrawalDurability={withdrawalDurability}
                    inflationAdjustedSeries={inflationAdjustedSeries}
                    cashflowEvents={cashflowEvents}
                />
            )}

            {activeTab === "overview" && (
                <OverviewTab
                    benchmarkStats={benchmarkStats}
                    comparisonChartSeries={comparisonChartSeries}
                    visiblePortfolioChartSeries={visiblePortfolioChartSeries}
                    valueHistory={valueHistory}
                    portfolioChartLogScale={portfolioChartLogScale}
                    showPortfolioSeries={showPortfolioSeries}
                    showBenchmarkSeries={showBenchmarkSeries}
                    exportBaseName={overviewExportBaseName}
                    onTogglePortfolioSeries={onTogglePortfolioSeries}
                    onToggleBenchmarkSeries={onToggleBenchmarkSeries}
                    onToggleLogScale={onToggleLogScale}
                />
            )}

            {activeTab === "diagnostics" && (
                <DiagnosticsTab
                    rollingMetrics={rollingMetrics}
                    rollingChartData={rollingChartData}
                    regimeSummary={regimeSummary}
                    regimePeriods={regimePeriods}
                    regimeReferenceTicker={regimeReferenceTicker}
                    allocationChartData={allocationChartData}
                    allocationSeriesKeys={allocationSeriesKeys}
                    allocationDriftSummary={allocationDriftSummary}
                    rebalanceEvents={rebalanceEvents}
                />
            )}

            {activeTab === "comparison" && (
                <ComparisonResultsTab
                    comparisonRuns={comparisonRuns}
                    comparisonRows={comparisonRows}
                    comparisonResultSeries={comparisonResultSeries}
                    comparisonDrawdownSeries={comparisonDrawdownSeries}
                    exportBaseName={comparisonExportBaseName}
                    onExportCsv={onExportComparisonCsv}
                />
            )}

            {activeTab === "returns" && (
                <ReturnsTab
                    monthlyReturns={monthlyReturns}
                    annualReturns={annualReturns}
                    trades={trades}
                />
            )}
        </>
    );
}
