"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { Landmark, LineChart } from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LightweightChart } from "@/components/charts/lightweight-chart";
import { DataTable } from "@/components/common/data-table";
import { StatCard } from "@/components/common/stat-card";
import { PageHeader } from "@/components/common/page-header";
import { ChartCard } from "@/components/common/chart-card";
import { ConfigPanel } from "@/components/common/config-panel";
import { ToolLayout } from "@/components/common/tool-layout";
import { EmptyState } from "@/components/common/empty-state";
import { InlineError } from "@/components/common/inline-error";
import {
    ChartSkeleton,
    CardSkeleton,
} from "@/components/common/loading-skeleton";
import { apiGet, apiPost } from "@/lib/api";
import { formatPercent, formatNumber } from "@/lib/format";
import { cn } from "@/lib/utils";
import type {
    BondLadderRequest,
    BondLadderResponse,
    FundInfo,
    SimulationResponse,
} from "@/types/api";

const CHART_COLORS = [
    "#3b82f6",
    "#22c55e",
    "#f59e0b",
    "#a855f7",
    "#06b6d4",
    "#ef4444",
    "#ec4899",
    "#14b8a6",
    "#f97316",
    "#8b5cf6",
];

const FUND_GROUPS: { label: string; tickers: string[] }[] = [
    { label: "S&P 500", tickers: ["SPY", "SSO", "UPRO"] },
    { label: "Nasdaq", tickers: ["QQQ", "QLD", "TQQQ"] },
    { label: "Treasury Long", tickers: ["TLT", "UBT", "TMF"] },
    { label: "Treasury Mid", tickers: ["IEF", "UST", "TYD"] },
    { label: "Treasury Short", tickers: ["SHY"] },
    { label: "Multi-Asset", tickers: ["NTSX"] },
];

const FUND_PRESETS: { label: string; tickers: string[] }[] = [
    { label: "Leveraged S&P", tickers: ["SPY", "SSO", "UPRO"] },
    { label: "Bond Duration", tickers: ["SHY", "IEF", "TLT"] },
    { label: "60/40", tickers: ["SPY", "TLT"] },
];

function parseTickerList(input: string): string[] {
    return input
        .split(",")
        .map((value) => value.trim().toUpperCase())
        .filter((value) => value.length > 0);
}

function FundSimulationsWorkspace() {
    const [selected, setSelected] = useState<string[]>(["SPY"]);
    const [normalize, setNormalize] = useState(true);

    const { data: funds } = useQuery({
        queryKey: ["funds"],
        queryFn: () => apiGet<FundInfo[]>("/api/simulations/funds"),
    });

    const { data, isLoading, error } = useQuery({
        queryKey: ["simulations", selected, normalize],
        queryFn: () => {
            const params = new URLSearchParams();
            selected.forEach((ticker) => params.append("tickers", ticker));
            if (normalize) {
                params.set("normalize", "true");
            }
            return apiGet<SimulationResponse>(
                `/api/simulations/run?${params.toString()}`,
                60000,
            );
        },
        enabled: selected.length > 0,
    });

    if (error) {
        toast.error(`Simulation failed: ${(error as Error).message}`);
    }

    const toggleFund = (ticker: string) => {
        setSelected((current) =>
            current.includes(ticker)
                ? current.filter((value) => value !== ticker)
                : [...current, ticker],
        );
    };

    return (
        <ToolLayout
            configPanel={
                <ConfigPanel title="Leveraged Funds">
                    <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs font-medium text-muted-foreground/60">
                            Presets:
                        </span>
                        {FUND_PRESETS.map((preset) => (
                            <button
                                key={preset.label}
                                onClick={() => setSelected(preset.tickers)}
                                className="rounded-md border border-border/50 bg-card/50 px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-accent/50 hover:text-foreground"
                            >
                                {preset.label}
                            </button>
                        ))}
                    </div>

                    <div className="space-y-3">
                        {FUND_GROUPS.map((group) => {
                            const availableTickers = group.tickers.filter(
                                (ticker) =>
                                    funds?.some(
                                        (fund) => fund.ticker === ticker,
                                    ),
                            );
                            if (availableTickers.length === 0) return null;

                            return (
                                <div key={group.label}>
                                    <p className="mb-1.5 text-[10px] font-semibold tracking-widest text-muted-foreground/60 uppercase">
                                        {group.label}
                                    </p>
                                    <div className="flex flex-wrap gap-2">
                                        {availableTickers.map((ticker) => (
                                            <button
                                                key={ticker}
                                                onClick={() =>
                                                    toggleFund(ticker)
                                                }
                                                className={cn(
                                                    "rounded-lg border px-3 py-1.5 text-xs font-medium transition-all duration-200",
                                                    selected.includes(ticker)
                                                        ? "border-blue-500/50 bg-blue-500/10 text-blue-400 shadow-sm shadow-blue-500/10"
                                                        : "border-border/50 bg-card/30 text-muted-foreground hover:border-border hover:text-foreground",
                                                )}
                                            >
                                                {ticker}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    <div className="flex items-center gap-3">
                        <Switch
                            id="normalize-funds"
                            checked={normalize}
                            onCheckedChange={setNormalize}
                        />
                        <Label
                            htmlFor="normalize-funds"
                            className="text-sm text-muted-foreground"
                        >
                            Normalize to 100
                        </Label>
                    </div>
                </ConfigPanel>
            }
        >
            {isLoading ? (
                <>
                    <ChartSkeleton />
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                        <CardSkeleton />
                        <CardSkeleton />
                        <CardSkeleton />
                        <CardSkeleton />
                    </div>
                </>
            ) : data ? (
                <>
                    <ChartCard
                        title={`${normalize ? "Normalized" : "Absolute"} Performance`}
                    >
                        <LightweightChart
                            series={data.series.map((series, index) => ({
                                ...series,
                                color: CHART_COLORS[
                                    index % CHART_COLORS.length
                                ],
                            }))}
                            height={450}
                            type="line"
                        />
                    </ChartCard>

                    {data.metrics.length > 0 && (
                        <>
                            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                                {data.metrics.slice(0, 4).map((metric) => (
                                    <StatCard
                                        key={metric.ticker}
                                        label={`${metric.ticker} CAGR`}
                                        value={formatPercent(metric.cagr)}
                                        trend={
                                            metric.cagr != null &&
                                            metric.cagr > 0
                                                ? "up"
                                                : "down"
                                        }
                                    />
                                ))}
                            </div>

                            <ChartCard title="Summary Metrics">
                                <DataTable
                                    columns={[
                                        { key: "ticker", label: "Ticker" },
                                        { key: "name", label: "Name" },
                                        {
                                            key: "leverage",
                                            label: "Leverage",
                                            format: (value) =>
                                                formatNumber(
                                                    value as number | null,
                                                    2,
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
                                            key: "max_drawdown",
                                            label: "Max Drawdown",
                                            format: (value) =>
                                                formatPercent(
                                                    value as number | null,
                                                ),
                                        },
                                    ]}
                                    data={data.metrics}
                                />
                            </ChartCard>
                        </>
                    )}
                </>
            ) : (
                <EmptyState
                    icon={LineChart}
                    message="Select one or more simulated funds to compare their paths."
                />
            )}
        </ToolLayout>
    );
}

function BondLadderWorkspace() {
    const [minMaturityYears, setMinMaturityYears] = useState(1);
    const [maxMaturityYears, setMaxMaturityYears] = useState(10);
    const [compareTickers, setCompareTickers] = useState("SHY, IEF, TLT");
    const [normalize, setNormalize] = useState(true);

    const mutation = useMutation({
        mutationFn: (request: BondLadderRequest) =>
            apiPost<BondLadderResponse>(
                "/api/simulations/bond-ladder/run",
                request,
                120000,
            ),
        onSuccess: () => toast.success("Bond ladder research complete"),
        onError: (error) => toast.error(`Bond ladder failed: ${error.message}`),
    });

    const handleRun = () => {
        if (maxMaturityYears <= minMaturityYears) {
            toast.error("Max maturity must be greater than min maturity.");
            return;
        }

        mutation.mutate({
            min_maturity_years: minMaturityYears,
            max_maturity_years: maxMaturityYears,
            compare_tickers: parseTickerList(compareTickers),
            normalize,
        });
    };

    const result = mutation.data;
    const ladderMetric = result?.metrics.find(
        (metric) => metric.ticker === "BOND_LADDER",
    );

    return (
        <ToolLayout
            configPanel={
                <ConfigPanel title="Bond Ladder">
                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                        <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">
                                Min Maturity (Years)
                            </Label>
                            <Input
                                type="number"
                                min={1}
                                max={30}
                                value={minMaturityYears}
                                onChange={(event) =>
                                    setMinMaturityYears(
                                        Number(event.target.value),
                                    )
                                }
                                className="border-border/50 bg-background/50"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">
                                Max Maturity (Years)
                            </Label>
                            <Input
                                type="number"
                                min={2}
                                max={30}
                                value={maxMaturityYears}
                                onChange={(event) =>
                                    setMaxMaturityYears(
                                        Number(event.target.value),
                                    )
                                }
                                className="border-border/50 bg-background/50"
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">
                            Comparison Tickers
                        </Label>
                        <Input
                            value={compareTickers}
                            onChange={(event) =>
                                setCompareTickers(event.target.value)
                            }
                            placeholder="SHY, IEF, TLT"
                            className="border-border/50 bg-background/50"
                        />
                        <p className="text-xs text-muted-foreground">
                            Compare the simulated ladder against Treasury ETFs
                            on the same date range.
                        </p>
                    </div>

                    <div className="flex items-center gap-3">
                        <Switch
                            id="normalize-bond-ladder"
                            checked={normalize}
                            onCheckedChange={setNormalize}
                        />
                        <Label
                            htmlFor="normalize-bond-ladder"
                            className="text-sm text-muted-foreground"
                        >
                            Normalize all series to 100
                        </Label>
                    </div>

                    <Button
                        className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
                        onClick={handleRun}
                        disabled={mutation.isPending}
                    >
                        {mutation.isPending ? "Running..." : "Run Bond Ladder"}
                    </Button>
                </ConfigPanel>
            }
        >
            {mutation.isPending && (
                <>
                    <ChartSkeleton />
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                        <CardSkeleton />
                        <CardSkeleton />
                        <CardSkeleton />
                        <CardSkeleton />
                    </div>
                </>
            )}

            {result && (
                <>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                        <StatCard
                            label="Ladder CAGR"
                            value={formatPercent(ladderMetric?.cagr ?? null)}
                            trend={
                                ladderMetric?.cagr != null &&
                                ladderMetric.cagr > 0
                                    ? "up"
                                    : "down"
                            }
                        />
                        <StatCard
                            label="Ladder Total Return"
                            value={formatPercent(
                                ladderMetric?.total_return ?? null,
                            )}
                            trend={
                                ladderMetric?.total_return != null &&
                                ladderMetric.total_return > 0
                                    ? "up"
                                    : "down"
                            }
                        />
                        <StatCard
                            label="Ladder Volatility"
                            value={formatPercent(
                                ladderMetric?.volatility ?? null,
                            )}
                            trend="neutral"
                        />
                        <StatCard
                            label="Comparison Series"
                            value={formatNumber(result.series.length, 0)}
                            trend="neutral"
                        />
                    </div>

                    <ChartCard title="Bond Ladder vs Comparisons">
                        <LightweightChart
                            series={result.series.map((series, index) => ({
                                ...series,
                                color: CHART_COLORS[
                                    index % CHART_COLORS.length
                                ],
                            }))}
                            height={420}
                            type="line"
                        />
                    </ChartCard>

                    <ChartCard title="Bond Ladder Metrics">
                        <DataTable
                            columns={[
                                { key: "ticker", label: "Ticker" },
                                { key: "name", label: "Name" },
                                {
                                    key: "start_value",
                                    label: "Start",
                                    format: (value) =>
                                        formatNumber(value as number | null, 2),
                                },
                                {
                                    key: "end_value",
                                    label: "End",
                                    format: (value) =>
                                        formatNumber(value as number | null, 2),
                                },
                                {
                                    key: "total_return",
                                    label: "Total Return",
                                    format: (value) =>
                                        formatPercent(value as number | null),
                                },
                                {
                                    key: "cagr",
                                    label: "CAGR",
                                    format: (value) =>
                                        formatPercent(value as number | null),
                                },
                                {
                                    key: "volatility",
                                    label: "Volatility",
                                    format: (value) =>
                                        formatPercent(value as number | null),
                                },
                                {
                                    key: "max_drawdown",
                                    label: "Max Drawdown",
                                    format: (value) =>
                                        formatPercent(value as number | null),
                                },
                            ]}
                            data={result.metrics}
                        />
                    </ChartCard>
                </>
            )}

            {mutation.isError && (
                <InlineError
                    message={mutation.error?.message ?? "Bond ladder failed"}
                    onRetry={handleRun}
                />
            )}

            {!mutation.isPending && !mutation.isError && !result && (
                <EmptyState
                    icon={Landmark}
                    message="Run a bond ladder simulation to compare a staggered Treasury ladder against ETF proxies."
                    presets={[
                        {
                            label: "1Y-10Y Ladder",
                            onClick: () => {
                                setMinMaturityYears(1);
                                setMaxMaturityYears(10);
                                setCompareTickers("SHY, IEF, TLT");
                            },
                        },
                        {
                            label: "3Y-7Y Ladder",
                            onClick: () => {
                                setMinMaturityYears(3);
                                setMaxMaturityYears(7);
                                setCompareTickers("IEF, TLT");
                            },
                        },
                    ]}
                />
            )}
        </ToolLayout>
    );
}

export default function SimulationsPage() {
    return (
        <div className="space-y-8">
            <PageHeader
                title="Research Simulations"
                description="Compare leveraged fund simulations and fixed-income ladder research in one workspace"
            />

            <Tabs defaultValue="funds" className="space-y-6">
                <TabsList>
                    <TabsTrigger value="funds">Leveraged Funds</TabsTrigger>
                    <TabsTrigger value="bond-ladder">Bond Ladder</TabsTrigger>
                </TabsList>

                <TabsContent value="funds">
                    <FundSimulationsWorkspace />
                </TabsContent>

                <TabsContent value="bond-ladder">
                    <BondLadderWorkspace />
                </TabsContent>
            </Tabs>
        </div>
    );
}
