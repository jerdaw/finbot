"use client";

import { StatCard } from "@/components/common/stat-card";
import { ChartCard } from "@/components/common/chart-card";
import { LightweightChart } from "@/components/charts/lightweight-chart";
import { DrawdownChart } from "@/components/charts/drawdown-chart";
import { DataTable } from "@/components/common/data-table";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { getMetricTrend } from "@/lib/backtest-utils";
import { formatPercent, formatNumber, formatCurrencyPrecise } from "@/lib/format";
import type { BacktestResponse, BacktestRequest } from "@/types/api";
import { useBacktestStore } from "@/stores/backtest-store";

interface ResultsDashboardProps {
    result: BacktestResponse;
    request: BacktestRequest;
}

export function ResultsDashboard({ result, request }: ResultsDashboardProps) {
    const { activeResultTab, setActiveResultTab } = useBacktestStore();

    const stats = result.stats;
    const valueHistory = result.value_history ?? [];

    const chartSeries = valueHistory.length > 0 ? [
        {
            name: "Portfolio",
            dates: valueHistory.map((r) => String(r.date)),
            values: valueHistory.map((r) => r.Value as number),
            color: "#3b82f6",
        }
    ] : [];

    return (
        <div className="space-y-6 mt-8 animate-in fade-in">
            <h2 className="text-2xl font-bold tracking-tight">Results Overview</h2>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                    label="CAGR"
                    value={formatPercent((stats?.CAGR as number) || 0)}
                    trend={getMetricTrend(stats?.CAGR as number)}
                />
                <StatCard
                    label="Max Drawdown"
                    value={formatPercent((stats?.["Max Drawdown"] as number) || 0)}
                    trend={getMetricTrend(-(stats?.["Max Drawdown"] as number))}
                />
                <StatCard
                    label="Sharpe Ratio"
                    value={formatNumber((stats?.Sharpe as number) || 0)}
                    trend={getMetricTrend((stats?.Sharpe as number) - 1)}
                />
                <StatCard
                    label="Final Value"
                    value={formatCurrencyPrecise((valueHistory[valueHistory.length - 1]?.Value as number) || 0)}
                    trend="up"
                />
            </div>

            <Tabs value={activeResultTab} onValueChange={setActiveResultTab} className="w-full">
                <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="drawdowns">Drawdowns</TabsTrigger>
                    <TabsTrigger value="trades">Trades</TabsTrigger>
                    <TabsTrigger value="metrics">Metrics</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="mt-4">
                    <ChartCard title="Portfolio Growth">
                        <LightweightChart
                            series={chartSeries}
                            height={400}
                        />
                    </ChartCard>
                </TabsContent>

                <TabsContent value="drawdowns" className="mt-4">
                    <ChartCard title="Portfolio Drawdown">
                        <DrawdownChart
                            data={valueHistory.map(r => ({ date: String(r.date), value: r.Drawdown as number || 0 }))}
                            height={300}
                        />
                    </ChartCard>
                </TabsContent>

                <TabsContent value="trades" className="mt-4">
                    <div className="border rounded-md p-4">
                        <h3 className="text-lg font-medium mb-4">Trade Log</h3>
                        <DataTable
                            data={result.trades as any[] || []}
                            columns={[
                                { label: "Date", key: "date" },
                                { label: "Ticker", key: "ticker" },
                                { label: "Action", key: "action" },
                                { label: "Size", key: "size" },
                                { label: "Price", key: "price" },
                                { label: "Value", key: "value" }
                            ]}
                        />
                    </div>
                </TabsContent>

                <TabsContent value="metrics" className="mt-4">
                    <div className="border rounded-md p-4 bg-muted/50">
                        <h3 className="text-lg font-medium mb-4">Detailed Metrics</h3>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-y-2 gap-x-8 text-sm">
                            {Object.entries(stats || {}).map(([key, value]) => (
                                <div key={key} className="flex justify-between py-1 border-b border-border/50">
                                    <span className="text-muted-foreground">{key}</span>
                                    <span className="font-medium">{String(value)}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}
