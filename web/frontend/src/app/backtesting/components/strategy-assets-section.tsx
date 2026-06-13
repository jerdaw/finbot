"use client";

import { ConfigSection } from "@/components/common/config-panel";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface StrategyAssetsSectionProps {
    ticker: string;
    altTicker: string;
    needsMultiAsset: boolean;
    onTickerChange: (value: string) => void;
    onAltTickerChange: (value: string) => void;
}

export function StrategyAssetsSection({
    ticker,
    altTicker,
    needsMultiAsset,
    onTickerChange,
    onAltTickerChange,
}: StrategyAssetsSectionProps) {
    return (
        <ConfigSection
            title="Assets"
            description="Choose the instruments used by this strategy."
            defaultOpen={false}
            summary={needsMultiAsset ? `${ticker}, ${altTicker}` : ticker}
        >
            <div className="space-y-2">
                <Label className="text-xs text-muted-foreground">Asset</Label>
                <Input
                    value={ticker}
                    onChange={(event) => onTickerChange(event.target.value)}
                    className="border-border/50 bg-background/50"
                />
            </div>

            {needsMultiAsset && (
                <div className="space-y-2">
                    <Label className="text-xs text-muted-foreground">
                        Second Asset
                    </Label>
                    <Input
                        value={altTicker}
                        onChange={(event) =>
                            onAltTickerChange(event.target.value)
                        }
                        className="border-border/50 bg-background/50"
                    />
                </div>
            )}
        </ConfigSection>
    );
}
