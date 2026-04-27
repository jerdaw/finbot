"use client";

import { useBacktestStore } from "@/stores/backtest-store";
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
import { ConfigSection } from "@/components/common/config-panel";
import { Plus, Trash2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { StrategyInfo } from "@/types/api";

export function ConfigurationPanel() {
    const { data: strategies } = useQuery({
        queryKey: ["strategies"],
        queryFn: () => apiGet<StrategyInfo[]>("/api/backtesting/strategies"),
    });

    const {
        ticker, setTicker,
        altTicker, setAltTicker,
        portfolioAssets, setPortfolioAssets,
        strategy, setStrategy,
        startDate, setStartDate,
        endDate, setEndDate,
        cash, setCash,
        benchmarkTicker, setBenchmarkTicker,
        riskFreeRate, setRiskFreeRate,
    } = useBacktestStore();

    const isAllocationStrategy = strategy === "NoRebalance" || strategy === "Rebalance";
    const currentStrategy = strategies?.find((s) => s.name === strategy);
    const needsMultiAsset = !isAllocationStrategy && currentStrategy && currentStrategy.min_assets > 1;

    const addAsset = () => setPortfolioAssets((current) => [...current, { ticker: "", weight: 0 }]);
    const removeAsset = (index: number) => setPortfolioAssets((current) => current.length > 1 ? current.filter((_, i) => i !== index) : current);
    const updateAssetTicker = (index: number, ticker: string) => setPortfolioAssets((current) => current.map((a, i) => i === index ? { ...a, ticker } : a));
    const updateAssetWeight = (index: number, weight: number) => setPortfolioAssets((current) => current.map((a, i) => i === index ? { ...a, weight } : a));

    return (
        <div className="space-y-6">
            <ConfigSection title="Strategy & Assets">
                <div className="space-y-4">
                    <div className="grid gap-2">
                        <Label>Strategy</Label>
                        <Select value={strategy} onValueChange={setStrategy}>
                            <SelectTrigger>
                                <SelectValue placeholder="Select strategy" />
                            </SelectTrigger>
                            <SelectContent>
                                {strategies?.map((s) => (
                                    <SelectItem key={s.name} value={s.name}>
                                        {s.name}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    {!isAllocationStrategy ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="grid gap-2">
                                <Label>Ticker</Label>
                                <Input value={ticker} onChange={(e) => setTicker(e.target.value)} placeholder="SPY" />
                            </div>
                            {needsMultiAsset && (
                                <div className="grid gap-2">
                                    <Label>Alternate Ticker</Label>
                                    <Input value={altTicker} onChange={(e) => setAltTicker(e.target.value)} placeholder="TLT" />
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="space-y-4">
                            <Label>Portfolio Assets</Label>
                            {portfolioAssets.map((asset, index) => (
                                <div key={index} className="flex gap-2 items-center">
                                    <Input
                                        placeholder="Ticker"
                                        value={asset.ticker}
                                        onChange={(e) => updateAssetTicker(index, e.target.value)}
                                    />
                                    <Input
                                        type="number"
                                        placeholder="Weight %"
                                        value={asset.weight}
                                        onChange={(e) => updateAssetWeight(index, Number(e.target.value))}
                                    />
                                    <Button variant="ghost" size="icon" onClick={() => removeAsset(index)}>
                                        <Trash2 className="w-4 h-4 text-destructive" />
                                    </Button>
                                </div>
                            ))}
                            <Button variant="outline" size="sm" onClick={addAsset} className="w-full">
                                <Plus className="w-4 h-4 mr-2" /> Add Asset
                            </Button>
                        </div>
                    )}
                </div>
            </ConfigSection>

            <ConfigSection title="Timeframe & Capital">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="grid gap-2">
                        <Label>Start Date</Label>
                        <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
                    </div>
                    <div className="grid gap-2">
                        <Label>End Date</Label>
                        <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
                    </div>
                    <div className="grid gap-2">
                        <Label>Initial Cash ($)</Label>
                        <Input type="number" value={cash} onChange={(e) => setCash(Number(e.target.value))} />
                    </div>
                    <div className="grid gap-2">
                        <Label>Benchmark Ticker</Label>
                        <Input value={benchmarkTicker} onChange={(e) => setBenchmarkTicker(e.target.value)} placeholder="Optional" />
                    </div>
                </div>
            </ConfigSection>
        </div>
    );
}
