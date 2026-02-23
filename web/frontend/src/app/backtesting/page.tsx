"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { LightweightChart } from "@/components/charts/lightweight-chart";
import { DrawdownChart } from "@/components/charts/drawdown-chart";
import { DataTable } from "@/components/common/data-table";
import { StatCard } from "@/components/common/stat-card";
import { PageHeader } from "@/components/common/page-header";
import { ConfigPanel } from "@/components/common/config-panel";
import { ChartCard } from "@/components/common/chart-card";
import { ToolLayout } from "@/components/common/tool-layout";
import { EmptyState } from "@/components/common/empty-state";
import { InlineError } from "@/components/common/inline-error";
import { ChartSkeleton, CardSkeleton } from "@/components/common/loading-skeleton";
import { Activity } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";
import { formatPercent, formatNumber, formatCurrencyPrecise } from "@/lib/format";
import type { StrategyInfo, BacktestRequest, BacktestResponse } from "@/types/api";

export default function BacktestingPage() {
  const [ticker, setTicker] = useState("SPY");
  const [altTicker, setAltTicker] = useState("TLT");
  const [strategy, setStrategy] = useState("NoRebalance");
  const [startDate, setStartDate] = useState("2015-01-01");
  const [endDate, setEndDate] = useState("2024-12-31");
  const [cash, setCash] = useState(10000);
  const [params, setParams] = useState<Record<string, number>>({});

  const { data: strategies } = useQuery({
    queryKey: ["strategies"],
    queryFn: () => apiGet<StrategyInfo[]>("/api/backtesting/strategies"),
  });

  const currentStrategy = strategies?.find((s) => s.name === strategy);
  const needsMultiAsset = currentStrategy && currentStrategy.min_assets > 1;

  const mutation = useMutation({
    mutationFn: (req: BacktestRequest) =>
      apiPost<BacktestResponse>("/api/backtesting/run", req, 120000),
    onSuccess: () => toast.success("Backtest complete"),
    onError: (e) => toast.error(`Backtest failed: ${e.message}`),
  });

  const handleRun = () => {
    const tickers = needsMultiAsset
      ? [ticker.toUpperCase(), altTicker.toUpperCase()]
      : [ticker.toUpperCase()];

    const strategyParams: Record<string, unknown> = { ...params };
    if (strategy === "NoRebalance") {
      strategyParams.equity_proportions = tickers.map(() => 1 / tickers.length);
    }
    if (strategy === "Rebalance") {
      strategyParams.rebal_proportions = tickers.map(() => 1 / tickers.length);
    }

    mutation.mutate({
      tickers,
      strategy,
      strategy_params: strategyParams,
      start_date: startDate,
      end_date: endDate,
      initial_cash: cash,
    });
  };

  const handleStrategyChange = (name: string) => {
    setStrategy(name);
    const s = strategies?.find((st) => st.name === name);
    if (s) {
      const defaults: Record<string, number> = {};
      s.params.forEach((p) => {
        defaults[p.name] = p.default as number;
      });
      setParams(defaults);
    } else {
      setParams({});
    }
  };

  const result = mutation.data;
  const stats = result?.stats;

  return (
    <div className="space-y-8">
      <PageHeader
        title="Strategy Backtester"
        description="Run backtests with different strategies and parameters on historical data"
      />

      <ToolLayout
        configPanel={
        <ConfigPanel title="Configuration">
          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Asset</Label>
            <Input
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              className="border-border/50 bg-background/50"
            />
          </div>

          {needsMultiAsset && (
            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">Second Asset</Label>
              <Input
                value={altTicker}
                onChange={(e) => setAltTicker(e.target.value)}
                className="border-border/50 bg-background/50"
              />
            </div>
          )}

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Strategy</Label>
            <Select value={strategy} onValueChange={handleStrategyChange}>
              <SelectTrigger className="border-border/50 bg-background/50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                {strategies?.map((s) => (
                  <SelectItem key={s.name} value={s.name}>{s.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            {currentStrategy && (
              <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                {currentStrategy.description}
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">Start</Label>
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="border-border/50 bg-background/50"
              />
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">End</Label>
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="border-border/50 bg-background/50"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Initial Cash ($)</Label>
            <Input
              type="number"
              value={cash}
              onChange={(e) => setCash(Number(e.target.value))}
              className="border-border/50 bg-background/50"
            />
          </div>

          {/* Dynamic strategy params */}
          {currentStrategy?.params.map((p) => (
            <div key={p.name} className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">{p.description || p.name}</Label>
              <Input
                type="number"
                step={p.type === "float" ? 0.01 : 1}
                value={params[p.name] ?? p.default}
                onChange={(e) =>
                  setParams((prev) => ({ ...prev, [p.name]: Number(e.target.value) }))
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
                <CardSkeleton /><CardSkeleton /><CardSkeleton /><CardSkeleton />
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
                  trend={(stats["CAGR"] as number) > 0 ? "up" : "down"}
                />
                <StatCard
                  label="Sharpe Ratio"
                  value={formatNumber(stats["Sharpe"] as number, 3)}
                  trend={(stats["Sharpe"] as number) > 0 ? "up" : "down"}
                />
                <StatCard
                  label="Max Drawdown"
                  value={formatPercent(stats["Max Drawdown"] as number)}
                  trend="down"
                />
                <StatCard
                  label="ROI"
                  value={formatPercent(stats["ROI"] as number)}
                  trend={(stats["ROI"] as number) > 0 ? "up" : "down"}
                />
              </div>

              {/* Portfolio value chart */}
              {result?.value_history && result.value_history.length > 0 && (
                <ChartCard title="Portfolio Value">
                  <LightweightChart
                    series={[{
                      name: "Value",
                      dates: result.value_history.map((r) => String(r.date)),
                      values: result.value_history.map((r) => r.Value as number),
                    }]}
                    height={400}
                    type="area"
                  />
                </ChartCard>
              )}

              {/* Drawdown chart */}
              {result?.value_history && result.value_history.length > 0 && (
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

              {/* Trades table */}
              {result?.trades && result.trades.length > 0 && (
                <ChartCard title={`Trades (${result.trades.length})`}>
                  <DataTable
                    columns={[
                      { key: "date", label: "Date" },
                      { key: "ticker", label: "Ticker" },
                      { key: "action", label: "Action" },
                      { key: "size", label: "Size", format: (v) => formatNumber(v as number, 0) },
                      { key: "price", label: "Price", format: (v) => formatCurrencyPrecise(v as number) },
                      { key: "value", label: "Value", format: (v) => formatCurrencyPrecise(v as number) },
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
                    value: typeof v === "number"
                      ? v < 1 && v > -1 && k !== "Sharpe" && k !== "Smart Sharpe"
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
                { label: "SPY Buy & Hold", onClick: () => { setTicker("SPY"); setStrategy("NoRebalance"); } },
                { label: "SPY SMA Crossover", onClick: () => { setTicker("SPY"); setStrategy("SMA_Crossover"); } },
                { label: "SPY + TLT Rebalance", onClick: () => { setTicker("SPY"); setAltTicker("TLT"); setStrategy("Rebalance"); } },
              ]}
            />
          )}
      </ToolLayout>
    </div>
  );
}
