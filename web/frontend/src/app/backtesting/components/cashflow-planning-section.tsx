"use client";

import { Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
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
import { CASHFLOW_FREQUENCY_OPTIONS } from "@/app/backtesting/backtesting-options";
import type {
    OneTimeCashflowEvent,
    RecurringCashflowRule,
} from "@/types/api";

interface CashflowPlanningSectionProps {
    recurringContribution: number;
    contributionFrequency: RecurringCashflowRule["frequency"];
    recurringWithdrawal: number;
    withdrawalFrequency: RecurringCashflowRule["frequency"];
    inflationRate: number;
    oneTimeCashflows: OneTimeCashflowEvent[];
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
}

export function CashflowPlanningSection({
    recurringContribution,
    contributionFrequency,
    recurringWithdrawal,
    withdrawalFrequency,
    inflationRate,
    oneTimeCashflows,
    onRecurringContributionChange,
    onContributionFrequencyChange,
    onRecurringWithdrawalChange,
    onWithdrawalFrequencyChange,
    onInflationRateChange,
    onOneTimeCashflowChange,
    onAddOneTimeCashflow,
    onRemoveOneTimeCashflow,
}: CashflowPlanningSectionProps) {
    return (
        <ConfigSection
            title="Cashflow planning"
            description="Model recurring savings, portfolio-funded withdrawals, and dated one-off events in the same backtest run."
            summary={
                recurringContribution ||
                recurringWithdrawal ||
                oneTimeCashflows.length
                    ? `${oneTimeCashflows.length} one-time event${
                          oneTimeCashflows.length === 1 ? "" : "s"
                      }`
                    : "No cashflows"
            }
        >
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-[minmax(0,1fr)_132px] lg:col-span-2">
                <Input
                    type="number"
                    value={recurringContribution}
                    onChange={(event) =>
                        onRecurringContributionChange(
                            Number(event.target.value),
                        )
                    }
                    placeholder="Recurring contribution"
                    className="border-border/50 bg-background/50"
                />
                <Select
                    value={contributionFrequency}
                    onValueChange={(value) =>
                        onContributionFrequencyChange(
                            value as RecurringCashflowRule["frequency"],
                        )
                    }
                >
                    <SelectTrigger className="border-border/50 bg-background/50">
                        <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                        {CASHFLOW_FREQUENCY_OPTIONS.map((option) => (
                            <SelectItem
                                key={`contrib-${option.value}`}
                                value={option.value}
                            >
                                {option.label}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            <div className="grid grid-cols-1 gap-2 sm:grid-cols-[minmax(0,1fr)_132px] lg:col-span-2">
                <Input
                    type="number"
                    value={recurringWithdrawal}
                    onChange={(event) =>
                        onRecurringWithdrawalChange(Number(event.target.value))
                    }
                    placeholder="Recurring withdrawal"
                    className="border-border/50 bg-background/50"
                />
                <Select
                    value={withdrawalFrequency}
                    onValueChange={(value) =>
                        onWithdrawalFrequencyChange(
                            value as RecurringCashflowRule["frequency"],
                        )
                    }
                >
                    <SelectTrigger className="border-border/50 bg-background/50">
                        <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="border-border/50 bg-popover/95 backdrop-blur-xl">
                        {CASHFLOW_FREQUENCY_OPTIONS.map((option) => (
                            <SelectItem
                                key={`withdraw-${option.value}`}
                                value={option.value}
                            >
                                {option.label}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            <div className="space-y-2 lg:col-span-2">
                <Label className="text-xs text-muted-foreground">
                    Inflation Rate
                </Label>
                <Input
                    type="number"
                    step={0.01}
                    min={0}
                    max={1}
                    value={inflationRate}
                    onChange={(event) =>
                        onInflationRateChange(Number(event.target.value))
                    }
                    className="border-border/50 bg-background/50"
                />
            </div>

            <div className="space-y-2">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                        <Label className="text-xs text-muted-foreground">
                            One-Time Events
                        </Label>
                        <p className="text-[11px] leading-relaxed text-muted-foreground/70">
                            Positive amounts add capital. Negative amounts
                            withdraw it.
                        </p>
                    </div>
                    <Button
                        type="button"
                        variant="outline"
                        size="xs"
                        onClick={onAddOneTimeCashflow}
                    >
                        <Plus />
                        Add Event
                    </Button>
                </div>

                {oneTimeCashflows.length > 0 && (
                    <div className="space-y-2">
                        {oneTimeCashflows.map((event, index) => (
                            <div
                                key={`${event.date}-${index}`}
                                className="grid grid-cols-1 gap-2 sm:grid-cols-[132px_minmax(0,1fr)_minmax(0,1fr)_auto]"
                            >
                                <Input
                                    type="date"
                                    value={event.date}
                                    onChange={(inputEvent) =>
                                        onOneTimeCashflowChange(index, {
                                            date: inputEvent.target.value,
                                        })
                                    }
                                    className="border-border/50 bg-background/50"
                                    aria-label={`Date for cashflow event ${index + 1}`}
                                />
                                <Input
                                    type="number"
                                    value={event.amount}
                                    onChange={(inputEvent) =>
                                        onOneTimeCashflowChange(index, {
                                            amount: Number(
                                                inputEvent.target.value,
                                            ),
                                        })
                                    }
                                    placeholder="Amount"
                                    className="border-border/50 bg-background/50"
                                    aria-label={`Amount for cashflow event ${index + 1}`}
                                />
                                <Input
                                    value={event.label ?? ""}
                                    onChange={(inputEvent) =>
                                        onOneTimeCashflowChange(index, {
                                            label: inputEvent.target.value,
                                        })
                                    }
                                    placeholder="Optional label"
                                    className="border-border/50 bg-background/50"
                                    aria-label={`Label for cashflow event ${index + 1}`}
                                />
                                <Button
                                    type="button"
                                    variant="ghost"
                                    size="icon-xs"
                                    onClick={() =>
                                        onRemoveOneTimeCashflow(index)
                                    }
                                    aria-label={`Remove cashflow event ${index + 1}`}
                                >
                                    <Trash2 />
                                </Button>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </ConfigSection>
    );
}
