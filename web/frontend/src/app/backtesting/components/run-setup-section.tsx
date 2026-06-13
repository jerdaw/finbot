"use client";

import { ConfigSection } from "@/components/common/config-panel";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { formatNumber } from "@/lib/format";

interface RunSetupSectionProps {
    startDate: string;
    endDate: string;
    cash: number;
    benchmarkTicker: string;
    riskFreeRate: number;
    onStartDateChange: (value: string) => void;
    onEndDateChange: (value: string) => void;
    onCashChange: (value: number) => void;
    onBenchmarkTickerChange: (value: string) => void;
    onRiskFreeRateChange: (value: number) => void;
}

export function RunSetupSection({
    startDate,
    endDate,
    cash,
    benchmarkTicker,
    riskFreeRate,
    onStartDateChange,
    onEndDateChange,
    onCashChange,
    onBenchmarkTickerChange,
    onRiskFreeRateChange,
}: RunSetupSectionProps) {
    return (
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
                        onChange={(event) =>
                            onStartDateChange(event.target.value)
                        }
                        className="border-border/50 bg-background/50"
                    />
                </div>
                <div className="space-y-1.5">
                    <Label className="text-xs text-muted-foreground">End</Label>
                    <Input
                        type="date"
                        value={endDate}
                        onChange={(event) =>
                            onEndDateChange(event.target.value)
                        }
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
                    onChange={(event) => onCashChange(Number(event.target.value))}
                    className="border-border/50 bg-background/50"
                />
            </div>
            <div className="space-y-2">
                <Label className="text-xs text-muted-foreground">
                    Benchmark Ticker
                </Label>
                <Input
                    value={benchmarkTicker}
                    onChange={(event) =>
                        onBenchmarkTickerChange(event.target.value)
                    }
                    placeholder="Leave blank to skip benchmark analysis"
                    className="border-border/50 bg-background/50"
                />
                <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                    Compare the backtest to a benchmark on the same date range.
                    Leave blank to keep the existing no-benchmark workflow.
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
                    onChange={(event) =>
                        onRiskFreeRateChange(Number(event.target.value))
                    }
                    className="border-border/50 bg-background/50"
                />
            </div>
        </ConfigSection>
    );
}
