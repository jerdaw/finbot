"use client";

import { ConfigSection } from "@/components/common/config-panel";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    COMMISSION_MODE_OPTIONS,
    MISSING_DATA_POLICY_OPTIONS,
} from "@/app/backtesting/backtesting-options";
import type {
    BacktestCostAssumptions,
    MissingDataPolicy,
} from "@/types/api";

interface AssumptionsSectionProps {
    missingDataPolicy: MissingDataPolicy;
    costAssumptions: BacktestCostAssumptions;
    onMissingDataPolicyChange: (value: MissingDataPolicy) => void;
    onCostAssumptionChange: <K extends keyof BacktestCostAssumptions>(
        key: K,
        value: BacktestCostAssumptions[K],
    ) => void;
}

export function AssumptionsSection({
    missingDataPolicy,
    costAssumptions,
    onMissingDataPolicyChange,
    onCostAssumptionChange,
}: AssumptionsSectionProps) {
    const missingDataPolicyOption = MISSING_DATA_POLICY_OPTIONS.find(
        (option) => option.value === missingDataPolicy,
    );

    return (
        <ConfigSection
            title="Data and execution assumptions"
            description="Surface the gap-handling policy and estimated trade frictions used to contextualize this run."
            defaultOpen={false}
            summary={`${missingDataPolicyOption?.label ?? missingDataPolicy} / ${costAssumptions.commission_mode}`}
        >
            <div className="space-y-2 lg:col-span-2">
                <Label className="text-xs text-muted-foreground">
                    Missing Data Policy
                </Label>
                <Select
                    value={missingDataPolicy}
                    onValueChange={(value) =>
                        onMissingDataPolicyChange(value as MissingDataPolicy)
                    }
                >
                    <SelectTrigger className="border-border/50 bg-background/50">
                        <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                        {MISSING_DATA_POLICY_OPTIONS.map((option) => (
                            <SelectItem key={option.value} value={option.value}>
                                {option.label}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
                <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                    {missingDataPolicyOption?.description}
                </p>
            </div>

            <div className="space-y-2">
                <Label className="text-xs text-muted-foreground">
                    Commission Model
                </Label>
                <Select
                    value={costAssumptions.commission_mode}
                    onValueChange={(value) =>
                        onCostAssumptionChange(
                            "commission_mode",
                            value as BacktestCostAssumptions["commission_mode"],
                        )
                    }
                >
                    <SelectTrigger className="border-border/50 bg-background/50">
                        <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                        {COMMISSION_MODE_OPTIONS.map((option) => (
                            <SelectItem key={option.value} value={option.value}>
                                {option.label}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            {costAssumptions.commission_mode === "per_share" && (
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                    <div className="space-y-1.5">
                        <Label className="text-xs text-muted-foreground">
                            Per Share ($)
                        </Label>
                        <Input
                            type="number"
                            min={0}
                            step={0.0001}
                            value={costAssumptions.commission_per_share}
                            onChange={(event) =>
                                onCostAssumptionChange(
                                    "commission_per_share",
                                    Number(event.target.value),
                                )
                            }
                            className="border-border/50 bg-background/50"
                        />
                    </div>
                    <div className="space-y-1.5">
                        <Label className="text-xs text-muted-foreground">
                            Minimum ($)
                        </Label>
                        <Input
                            type="number"
                            min={0}
                            step={0.01}
                            value={costAssumptions.commission_minimum}
                            onChange={(event) =>
                                onCostAssumptionChange(
                                    "commission_minimum",
                                    Number(event.target.value),
                                )
                            }
                            className="border-border/50 bg-background/50"
                        />
                    </div>
                </div>
            )}

            {costAssumptions.commission_mode === "percentage" && (
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                    <div className="space-y-1.5">
                        <Label className="text-xs text-muted-foreground">
                            Commission (bps)
                        </Label>
                        <Input
                            type="number"
                            min={0}
                            step={0.1}
                            value={costAssumptions.commission_bps}
                            onChange={(event) =>
                                onCostAssumptionChange(
                                    "commission_bps",
                                    Number(event.target.value),
                                )
                            }
                            className="border-border/50 bg-background/50"
                        />
                    </div>
                    <div className="space-y-1.5">
                        <Label className="text-xs text-muted-foreground">
                            Minimum ($)
                        </Label>
                        <Input
                            type="number"
                            min={0}
                            step={0.01}
                            value={costAssumptions.commission_minimum}
                            onChange={(event) =>
                                onCostAssumptionChange(
                                    "commission_minimum",
                                    Number(event.target.value),
                                )
                            }
                            className="border-border/50 bg-background/50"
                        />
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:col-span-2">
                <div className="space-y-1.5">
                    <Label className="text-xs text-muted-foreground">
                        Spread (bps)
                    </Label>
                    <Input
                        type="number"
                        min={0}
                        step={0.1}
                        value={costAssumptions.spread_bps}
                        onChange={(event) =>
                            onCostAssumptionChange(
                                "spread_bps",
                                Number(event.target.value),
                            )
                        }
                        className="border-border/50 bg-background/50"
                    />
                </div>
                <div className="space-y-1.5">
                    <Label className="text-xs text-muted-foreground">
                        Slippage (bps)
                    </Label>
                    <Input
                        type="number"
                        min={0}
                        step={0.1}
                        value={costAssumptions.slippage_bps}
                        onChange={(event) =>
                            onCostAssumptionChange(
                                "slippage_bps",
                                Number(event.target.value),
                            )
                        }
                        className="border-border/50 bg-background/50"
                    />
                </div>
            </div>
        </ConfigSection>
    );
}
