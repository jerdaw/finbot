"use client";

import { Button } from "@/components/ui/button";
import { ConfigPanel } from "@/components/common/config-panel";
import { AssumptionsSection } from "@/app/backtesting/components/assumptions-section";
import { CashflowPlanningSection } from "@/app/backtesting/components/cashflow-planning-section";
import { PortfolioBuilderSection } from "@/app/backtesting/components/portfolio-builder-section";
import { RunSetupSection } from "@/app/backtesting/components/run-setup-section";
import { StrategyAssetsSection } from "@/app/backtesting/components/strategy-assets-section";
import { StrategyParametersSection } from "@/app/backtesting/components/strategy-parameters-section";
import { StrategySelectorSection } from "@/app/backtesting/components/strategy-selector-section";
import type { PortfolioPreset } from "@/app/backtesting/backtesting-options";
import type {
    BacktestCostAssumptions,
    MissingDataPolicy,
    OneTimeCashflowEvent,
    RecurringCashflowRule,
    StrategyInfo,
} from "@/types/api";
import type {
    ComparisonPortfolio,
    PortfolioAsset,
    SavedPortfolio,
} from "@/stores/backtest-store";

interface BacktestingConfigurationPanelProps {
    strategy: string;
    strategies: StrategyInfo[] | undefined;
    currentStrategy: StrategyInfo | undefined;
    isAllocationStrategy: boolean;
    ticker: string;
    altTicker: string;
    needsMultiAsset: boolean;
    portfolioAssets: PortfolioAsset[];
    allocationIsBalanced: boolean;
    allocationWeightTotal: number;
    presetFilter: string;
    filteredPortfolioPresets: PortfolioPreset[];
    savedPortfolios: SavedPortfolio[];
    comparisonPortfolios: ComparisonPortfolio[];
    comparisonIsPending: boolean;
    startDate: string;
    endDate: string;
    cash: number;
    benchmarkTicker: string;
    riskFreeRate: number;
    missingDataPolicy: MissingDataPolicy;
    costAssumptions: BacktestCostAssumptions;
    recurringContribution: number;
    contributionFrequency: RecurringCashflowRule["frequency"];
    recurringWithdrawal: number;
    withdrawalFrequency: RecurringCashflowRule["frequency"];
    inflationRate: number;
    oneTimeCashflows: OneTimeCashflowEvent[];
    params: Record<string, number>;
    runIsPending: boolean;
    onStrategyChange: (value: string) => void;
    onTickerChange: (value: string) => void;
    onAltTickerChange: (value: string) => void;
    onPresetFilterChange: (value: string) => void;
    onApplyPreset: (preset: PortfolioPreset) => void;
    onAddPresetToComparison: (preset: PortfolioPreset) => void;
    onEqualizeWeights: () => void;
    onNormalizeWeights: () => void;
    onClearAssets: () => void;
    onSavePortfolio: () => void;
    onAddCurrentToComparison: () => void;
    onAddAsset: () => void;
    onUpdateTicker: (index: number, value: string) => void;
    onUpdateWeight: (index: number, value: string) => void;
    onRemoveAsset: (index: number) => void;
    onApplySavedPortfolio: (portfolio: SavedPortfolio) => void;
    onAddSavedToComparison: (portfolio: SavedPortfolio) => void;
    onRemoveSavedPortfolio: (id: string) => void;
    onRunComparison: () => void;
    onRemoveComparisonPortfolio: (id: string) => void;
    onStartDateChange: (value: string) => void;
    onEndDateChange: (value: string) => void;
    onCashChange: (value: number) => void;
    onBenchmarkTickerChange: (value: string) => void;
    onRiskFreeRateChange: (value: number) => void;
    onMissingDataPolicyChange: (value: MissingDataPolicy) => void;
    onCostAssumptionChange: <K extends keyof BacktestCostAssumptions>(
        key: K,
        value: BacktestCostAssumptions[K],
    ) => void;
    onRecurringContributionChange: (value: number) => void;
    onContributionFrequencyChange: (
        value: RecurringCashflowRule["frequency"],
    ) => void;
    onRecurringWithdrawalChange: (value: number) => void;
    onWithdrawalFrequencyChange: (
        value: RecurringCashflowRule["frequency"],
    ) => void;
    onInflationRateChange: (value: number) => void;
    onOneTimeCashflowChange: (
        index: number,
        patch: Partial<OneTimeCashflowEvent>,
    ) => void;
    onAddOneTimeCashflow: () => void;
    onRemoveOneTimeCashflow: (index: number) => void;
    onParamsChange: (
        params:
            | Record<string, number>
            | ((current: Record<string, number>) => Record<string, number>),
    ) => void;
    onRun: () => void;
}

export function BacktestingConfigurationPanel({
    strategy,
    strategies,
    currentStrategy,
    isAllocationStrategy,
    ticker,
    altTicker,
    needsMultiAsset,
    portfolioAssets,
    allocationIsBalanced,
    allocationWeightTotal,
    presetFilter,
    filteredPortfolioPresets,
    savedPortfolios,
    comparisonPortfolios,
    comparisonIsPending,
    startDate,
    endDate,
    cash,
    benchmarkTicker,
    riskFreeRate,
    missingDataPolicy,
    costAssumptions,
    recurringContribution,
    contributionFrequency,
    recurringWithdrawal,
    withdrawalFrequency,
    inflationRate,
    oneTimeCashflows,
    params,
    runIsPending,
    onStrategyChange,
    onTickerChange,
    onAltTickerChange,
    onPresetFilterChange,
    onApplyPreset,
    onAddPresetToComparison,
    onEqualizeWeights,
    onNormalizeWeights,
    onClearAssets,
    onSavePortfolio,
    onAddCurrentToComparison,
    onAddAsset,
    onUpdateTicker,
    onUpdateWeight,
    onRemoveAsset,
    onApplySavedPortfolio,
    onAddSavedToComparison,
    onRemoveSavedPortfolio,
    onRunComparison,
    onRemoveComparisonPortfolio,
    onStartDateChange,
    onEndDateChange,
    onCashChange,
    onBenchmarkTickerChange,
    onRiskFreeRateChange,
    onMissingDataPolicyChange,
    onCostAssumptionChange,
    onRecurringContributionChange,
    onContributionFrequencyChange,
    onRecurringWithdrawalChange,
    onWithdrawalFrequencyChange,
    onInflationRateChange,
    onOneTimeCashflowChange,
    onAddOneTimeCashflow,
    onRemoveOneTimeCashflow,
    onParamsChange,
    onRun,
}: BacktestingConfigurationPanelProps) {
    return (
        <ConfigPanel title="Configuration">
            <StrategySelectorSection
                strategy={strategy}
                strategies={strategies}
                currentStrategy={currentStrategy}
                onStrategyChange={onStrategyChange}
            />

            {isAllocationStrategy ? (
                <PortfolioBuilderSection
                    portfolioAssets={portfolioAssets}
                    allocationIsBalanced={allocationIsBalanced}
                    allocationWeightTotal={allocationWeightTotal}
                    presetFilter={presetFilter}
                    filteredPortfolioPresets={filteredPortfolioPresets}
                    savedPortfolios={savedPortfolios}
                    comparisonPortfolios={comparisonPortfolios}
                    comparisonIsPending={comparisonIsPending}
                    onPresetFilterChange={onPresetFilterChange}
                    onApplyPreset={onApplyPreset}
                    onAddPresetToComparison={onAddPresetToComparison}
                    onEqualizeWeights={onEqualizeWeights}
                    onNormalizeWeights={onNormalizeWeights}
                    onClearAssets={onClearAssets}
                    onSavePortfolio={onSavePortfolio}
                    onAddCurrentToComparison={onAddCurrentToComparison}
                    onAddAsset={onAddAsset}
                    onUpdateTicker={onUpdateTicker}
                    onUpdateWeight={onUpdateWeight}
                    onRemoveAsset={onRemoveAsset}
                    onApplySavedPortfolio={onApplySavedPortfolio}
                    onAddSavedToComparison={onAddSavedToComparison}
                    onRemoveSavedPortfolio={onRemoveSavedPortfolio}
                    onRunComparison={onRunComparison}
                    onRemoveComparisonPortfolio={onRemoveComparisonPortfolio}
                />
            ) : (
                <StrategyAssetsSection
                    ticker={ticker}
                    altTicker={altTicker}
                    needsMultiAsset={needsMultiAsset}
                    onTickerChange={onTickerChange}
                    onAltTickerChange={onAltTickerChange}
                />
            )}

            <RunSetupSection
                startDate={startDate}
                endDate={endDate}
                cash={cash}
                benchmarkTicker={benchmarkTicker}
                riskFreeRate={riskFreeRate}
                onStartDateChange={onStartDateChange}
                onEndDateChange={onEndDateChange}
                onCashChange={onCashChange}
                onBenchmarkTickerChange={onBenchmarkTickerChange}
                onRiskFreeRateChange={onRiskFreeRateChange}
            />

            <AssumptionsSection
                missingDataPolicy={missingDataPolicy}
                costAssumptions={costAssumptions}
                onMissingDataPolicyChange={onMissingDataPolicyChange}
                onCostAssumptionChange={onCostAssumptionChange}
            />

            <CashflowPlanningSection
                recurringContribution={recurringContribution}
                contributionFrequency={contributionFrequency}
                recurringWithdrawal={recurringWithdrawal}
                withdrawalFrequency={withdrawalFrequency}
                inflationRate={inflationRate}
                oneTimeCashflows={oneTimeCashflows}
                onRecurringContributionChange={onRecurringContributionChange}
                onContributionFrequencyChange={onContributionFrequencyChange}
                onRecurringWithdrawalChange={onRecurringWithdrawalChange}
                onWithdrawalFrequencyChange={onWithdrawalFrequencyChange}
                onInflationRateChange={onInflationRateChange}
                onOneTimeCashflowChange={onOneTimeCashflowChange}
                onAddOneTimeCashflow={onAddOneTimeCashflow}
                onRemoveOneTimeCashflow={onRemoveOneTimeCashflow}
            />

            <StrategyParametersSection
                strategy={currentStrategy}
                params={params}
                onParamsChange={onParamsChange}
            />

            <div className="col-span-full flex justify-end border-t border-border/40 pt-4">
                <div className="w-full sm:w-auto sm:min-w-48">
                    <Button
                        className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
                        onClick={onRun}
                        disabled={runIsPending}
                    >
                        {runIsPending ? "Running..." : "Run Backtest"}
                    </Button>
                </div>
            </div>
        </ConfigPanel>
    );
}
