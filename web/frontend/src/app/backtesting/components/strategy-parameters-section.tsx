"use client";

import { ConfigSection } from "@/components/common/config-panel";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { StrategyInfo } from "@/types/api";

interface StrategyParametersSectionProps {
    strategy: StrategyInfo | undefined;
    params: Record<string, number>;
    onParamsChange: (
        params:
            | Record<string, number>
            | ((current: Record<string, number>) => Record<string, number>),
    ) => void;
}

export function StrategyParametersSection({
    strategy,
    params,
    onParamsChange,
}: StrategyParametersSectionProps) {
    if (!strategy || strategy.params.length === 0) {
        return null;
    }

    return (
        <ConfigSection
            title="Strategy parameters"
            description="Fine-tune the selected strategy's numeric inputs."
            defaultOpen={false}
        >
            {strategy.params.map((parameter) => (
                <div key={parameter.name} className="space-y-1.5">
                    <Label className="text-xs text-muted-foreground">
                        {parameter.description || parameter.name}
                    </Label>
                    <Input
                        type="number"
                        step={parameter.type === "float" ? 0.01 : 1}
                        value={params[parameter.name] ?? parameter.default}
                        onChange={(event) =>
                            onParamsChange((current) => ({
                                ...current,
                                [parameter.name]: Number(event.target.value),
                            }))
                        }
                        className="border-border/50 bg-background/50"
                    />
                </div>
            ))}
        </ConfigSection>
    );
}
