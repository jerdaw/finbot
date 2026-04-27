import type {
    BacktestRequest,
    BacktestResponse,
    SaveExperimentResponse,
    RollingMetricsResponse,
    BacktestBenchmarkStats
} from "@/types/api";

export function downloadFile(content: string, fileName: string, mimeType: string): void {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = fileName;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
}

export function escapeCsvValue(value: unknown): string {
    if (value == null) {
        return "";
    }
    const normalized = String(value).replace(/"/g, '""');
    return /[",\n]/.test(normalized) ? `"${normalized}"` : normalized;
}

export function buildCsv(rows: Array<Record<string, unknown>>, columns: string[]): string {
    const header = columns.join(",");
    const body = rows.map((row) =>
        columns.map((column) => escapeCsvValue(row[column])).join(","),
    );
    return [header, ...body].join("\n");
}

export function buildExportBaseName(request: BacktestRequest | null): string {
    if (!request) {
        return "finbot-backtest";
    }
    const slug = [request.strategy, ...request.tickers]
        .join("-")
        .toLowerCase()
        .replace(/[^a-z0-9-]+/g, "-")
        .replace(/-+/g, "-")
        .replace(/^-|-$/g, "");
    return slug ? `finbot-${slug}` : "finbot-backtest";
}
