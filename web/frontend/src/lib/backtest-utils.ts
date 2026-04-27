import type { BacktestResponse, WalkForwardHandoff } from "@/types/api";

export function getMetricTrend(value: number | null | undefined): "up" | "down" | "neutral" {
    if (value == null) {
        return "neutral";
    }
    return value > 0 ? "up" : value < 0 ? "down" : "neutral";
}

export function formatBenchmarkValue(
    value: number | null | undefined,
    formatter: (value: number | null | undefined) => string,
): string {
    return value == null ? "N/A" : formatter(value);
}

export function getNumericStat(
    stats: Record<string, unknown> | null | undefined,
    key: string,
): number | null {
    const value = stats?.[key];
    return typeof value === "number" && Number.isFinite(value) ? value : null;
}

export function getEndingValue(result: BacktestResponse | null | undefined): number | null {
    const history = result?.value_history ?? [];
    const last = history[history.length - 1];
    const value = last?.Value;
    return typeof value === "number" && Number.isFinite(value) ? value : null;
}

export function buildDrawdownValues(values: Array<number | null>): Array<number | null> {
    let peak: number | null = null;
    return values.map((value) => {
        if (value == null || !Number.isFinite(value) || value <= 0) {
            return null;
        }
        peak = peak == null ? value : Math.max(peak, value);
        return (value / peak - 1) * 100;
    });
}

export function buildWalkForwardHref(
    request: WalkForwardHandoff | null | undefined,
): string {
    if (!request) {
        return "/walk-forward";
    }
    const params = new URLSearchParams();
    params.set("tickers", request.tickers.join(","));
    params.set("strategy", request.strategy);
    params.set("start_date", request.start_date);
    params.set("end_date", request.end_date);
    params.set("initial_cash", String(request.initial_cash));
    params.set("train_window", String(request.train_window));
    params.set("test_window", String(request.test_window));
    params.set("step_size", String(request.step_size));
    params.set("anchored", String(request.anchored));
    params.set("include_train", String(request.include_train));
    if (Object.keys(request.strategy_params).length > 0) {
        params.set("strategy_params", JSON.stringify(request.strategy_params));
    }
    return `/walk-forward?${params.toString()}`;
}
