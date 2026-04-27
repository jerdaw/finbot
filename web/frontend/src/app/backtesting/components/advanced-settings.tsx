"use client";

import { useState } from "react";
import { useBacktestStore } from "@/stores/backtest-store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ConfigSection } from "@/components/common/config-panel";
import { Settings, ChevronDown, ChevronUp } from "lucide-react";
import type { MissingDataPolicy, RecurringCashflowRule } from "@/types/api";

const MISSING_DATA_POLICY_OPTIONS: Array<{ label: string; value: MissingDataPolicy }> = [
    { label: "Forward Fill", value: "forward_fill" },
    { label: "Drop Gaps", value: "drop" },
    { label: "Error", value: "error" },
    { label: "Interpolate", value: "interpolate" },
    { label: "Backfill", value: "backfill" },
];

const CASHFLOW_FREQUENCY_OPTIONS: Array<{ label: string; value: RecurringCashflowRule["frequency"] }> = [
    { label: "Monthly", value: "monthly" },
    { label: "Quarterly", value: "quarterly" },
    { label: "Yearly", value: "yearly" },
];

export function AdvancedSettings() {
    const [isOpen, setIsOpen] = useState(false);
    const {
        missingDataPolicy, setMissingDataPolicy,
        recurringContribution, setRecurringContribution,
        contributionFrequency, setContributionFrequency,
        recurringWithdrawal, setRecurringWithdrawal,
        withdrawalFrequency, setWithdrawalFrequency,
        inflationRate, setInflationRate,
        costAssumptions, setCostAssumptions,
    } = useBacktestStore();

    if (!isOpen) {
        return (
            <Button variant="outline" className="w-full mt-4" onClick={() => setIsOpen(true)}>
                <Settings className="w-4 h-4 mr-2" /> Show Advanced Settings <ChevronDown className="w-4 h-4 ml-auto" />
            </Button>
        );
    }

    return (
        <div className="space-y-6 mt-6 border-t pt-6 animate-in fade-in slide-in-from-top-4">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold flex items-center">
                    <Settings className="w-5 h-5 mr-2" /> Advanced Settings
                </h3>
                <Button variant="ghost" size="sm" onClick={() => setIsOpen(false)}>
                    Hide <ChevronUp className="w-4 h-4 ml-1" />
                </Button>
            </div>

            <ConfigSection title="Data & Rebalancing">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="grid gap-2">
                        <Label>Missing Data Policy</Label>
                        <Select value={missingDataPolicy} onValueChange={(v) => setMissingDataPolicy(v as MissingDataPolicy)}>
                            <SelectTrigger><SelectValue /></SelectTrigger>
                            <SelectContent>
                                {MISSING_DATA_POLICY_OPTIONS.map((opt) => (
                                    <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                </div>
            </ConfigSection>

            <ConfigSection title="Cashflows & Inflation">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="grid gap-2">
                        <Label>Recurring Contribution ($)</Label>
                        <Input type="number" value={recurringContribution} onChange={(e) => setRecurringContribution(Number(e.target.value))} />
                    </div>
                    <div className="grid gap-2">
                        <Label>Contribution Freq.</Label>
                        <Select value={contributionFrequency} onValueChange={(v) => setContributionFrequency(v as RecurringCashflowRule["frequency"])}>
                            <SelectTrigger><SelectValue /></SelectTrigger>
                            <SelectContent>
                                {CASHFLOW_FREQUENCY_OPTIONS.map((opt) => (
                                    <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                    <div className="grid gap-2">
                        <Label>Recurring Withdrawal ($)</Label>
                        <Input type="number" value={recurringWithdrawal} onChange={(e) => setRecurringWithdrawal(Number(e.target.value))} />
                    </div>
                    <div className="grid gap-2">
                        <Label>Withdrawal Freq.</Label>
                        <Select value={withdrawalFrequency} onValueChange={(v) => setWithdrawalFrequency(v as RecurringCashflowRule["frequency"])}>
                            <SelectTrigger><SelectValue /></SelectTrigger>
                            <SelectContent>
                                {CASHFLOW_FREQUENCY_OPTIONS.map((opt) => (
                                    <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                    <div className="grid gap-2">
                        <Label>Inflation Rate (Decimal)</Label>
                        <Input type="number" step="0.01" value={inflationRate} onChange={(e) => setInflationRate(Number(e.target.value))} />
                    </div>
                </div>
            </ConfigSection>

            <ConfigSection title="Cost Assumptions">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="grid gap-2">
                        <Label>Commission Mode</Label>
                        <Select value={costAssumptions.commission_mode} onValueChange={(v) => setCostAssumptions((c) => ({ ...c, commission_mode: v as "none" | "per_share" | "percentage" }))}>
                            <SelectTrigger><SelectValue /></SelectTrigger>
                            <SelectContent>
                                <SelectItem value="none">None</SelectItem>
                                <SelectItem value="per_share">Per Share</SelectItem>
                                <SelectItem value="percentage">Percentage</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                    <div className="grid gap-2">
                        <Label>Spread (bps)</Label>
                        <Input type="number" value={costAssumptions.spread_bps} onChange={(e) => setCostAssumptions((c) => ({ ...c, spread_bps: Number(e.target.value) }))} />
                    </div>
                </div>
            </ConfigSection>
        </div>
    );
}
