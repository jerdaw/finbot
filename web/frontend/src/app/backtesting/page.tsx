"use client";

import { BacktestingWorkspace } from "@/app/backtesting/components/backtesting-workspace";
import { useBacktestingPageController } from "@/app/backtesting/use-backtesting-page-controller";

export default function BacktestingPage() {
    const controller = useBacktestingPageController();

    return <BacktestingWorkspace controller={controller} />;
}
