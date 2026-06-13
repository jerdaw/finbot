"use client";

import { ConfigSection } from "@/components/common/config-panel";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import type { StrategyInfo } from "@/types/api";

interface StrategySelectorSectionProps {
    strategy: string;
    strategies: StrategyInfo[] | undefined;
    currentStrategy: StrategyInfo | undefined;
    onStrategyChange: (value: string) => void;
}

export function StrategySelectorSection({
    strategy,
    strategies,
    currentStrategy,
    onStrategyChange,
}: StrategySelectorSectionProps) {
    return (
        <ConfigSection
            title="Strategy"
            description="Select the backtest template and review its default behavior."
            summary={strategy}
        >
            <div className="space-y-2 col-span-full md:col-span-2 lg:col-span-1">
                <Label className="text-xs text-muted-foreground">
                    Strategy
                </Label>
                <Select value={strategy} onValueChange={onStrategyChange}>
                    <SelectTrigger className="border-border/50 bg-background/50">
                        <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                        {strategies?.map((strategyOption) => (
                            <SelectItem
                                key={strategyOption.name}
                                value={strategyOption.name}
                            >
                                {strategyOption.name}
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
    );
}
