import { expect, test, type Page, type Route } from "@playwright/test";

const APP_ROUTES = [
    { path: "/", heading: /Welcome to Finbot/i },
    { path: "/simulations", heading: "Research Simulations" },
    { path: "/backtesting", heading: "Strategy Backtester" },
    { path: "/optimizer", heading: "Portfolio Optimizer" },
    { path: "/monte-carlo", heading: "Monte Carlo Lab" },
    { path: "/walk-forward", heading: "Walk-Forward Analysis" },
    { path: "/experiments", heading: "Experiments" },
    { path: "/risk-analytics", heading: "Risk Analytics" },
    { path: "/portfolio-analytics", heading: "Portfolio Analytics" },
    { path: "/factor-analytics", heading: "Factor Analytics" },
    { path: "/realtime-quotes", heading: "Real-Time Quotes" },
    { path: "/data-status", heading: "Data Status" },
    { path: "/health-economics", heading: "Health Economics" },
] as const;

const strategies = [
    {
        name: "NoRebalance",
        description: "Buy and hold a fixed allocation.",
        params: [],
        min_assets: 1,
    },
    {
        name: "DualMomentum",
        description: "Switch between two assets based on momentum.",
        params: [],
        min_assets: 2,
    },
];

const funds = [
    {
        ticker: "SPY",
        name: "SPDR S&P 500 ETF Trust",
        leverage: 1,
        annual_er_pct: 0.09,
    },
    {
        ticker: "UPRO",
        name: "ProShares UltraPro S&P500",
        leverage: 3,
        annual_er_pct: 0.92,
    },
];

const dataStatus = {
    sources: [
        {
            name: "price_histories",
            description: "Historical price parquet files",
            file_count: 12,
            is_stale: false,
            age_str: "2 hours",
            size_str: "12 MB",
            oldest_file: "2024-01-01T00:00:00",
            newest_file: "2024-01-02T00:00:00",
            total_size_bytes: 12_000_000,
            max_age_days: 1,
        },
    ],
    total_files: 12,
    total_size_bytes: 12_000_000,
    fresh_count: 1,
    stale_count: 0,
};

const simulationResponse = {
    series: [
        {
            name: "SPY",
            dates: ["2024-01-01", "2024-01-02", "2024-01-03"],
            values: [100, 101, 102],
        },
    ],
    metrics: [
        {
            ticker: "SPY",
            name: "SPDR S&P 500 ETF Trust",
            leverage: 1,
            total_return: 0.12,
            cagr: 0.08,
            volatility: 0.14,
            max_drawdown: -0.09,
        },
    ],
};

const bondLadderResponse = {
    series: [
        {
            name: "1Y-10Y Ladder",
            dates: ["2024-01-01", "2024-01-02", "2024-01-03"],
            values: [100, 100.4, 100.9],
        },
        {
            name: "SHY",
            dates: ["2024-01-01", "2024-01-02", "2024-01-03"],
            values: [100, 100.1, 100.2],
        },
    ],
    metrics: [
        {
            ticker: "BOND_LADDER",
            name: "1Y-10Y Ladder",
            start_value: 100,
            end_value: 100.9,
            total_return: 0.009,
            cagr: 0.031,
            volatility: 0.024,
            max_drawdown: -0.012,
        },
        {
            ticker: "SHY",
            name: "1-3 Year Treasury",
            start_value: 100,
            end_value: 100.2,
            total_return: 0.002,
            cagr: 0.011,
            volatility: 0.01,
            max_drawdown: -0.004,
        },
    ],
};

const monteCarloResponse = {
    periods: [0, 1, 2, 3],
    bands: [
        { label: "p5", values: [100, 96, 94, 92] },
        { label: "p25", values: [100, 99, 98, 97] },
        { label: "p50", values: [100, 101, 102, 103] },
        { label: "p75", values: [100, 103, 105, 107] },
        { label: "p95", values: [100, 106, 109, 112] },
    ],
    sample_paths: [
        [100, 101, 102, 104],
        [100, 99, 100, 101],
        [100, 104, 107, 111],
    ],
    statistics: {
        mean: 105.33,
        median: 104,
        std: 4.11,
        min: 101,
        max: 111,
        p5: 101.3,
        p25: 102,
        p75: 107.5,
        p95: 110.2,
        prob_loss: 0.05,
    },
};

const multiAssetMonteCarloResponse = {
    periods: [0, 1, 2, 3],
    portfolio_bands: [
        { label: "p5", values: [10000, 9800, 9700, 9600] },
        { label: "p25", values: [10000, 9950, 10020, 10080] },
        { label: "p50", values: [10000, 10080, 10190, 10310] },
        { label: "p75", values: [10000, 10220, 10410, 10600] },
        { label: "p95", values: [10000, 10380, 10620, 10890] },
    ],
    portfolio_sample_paths: [
        [10000, 10050, 10120, 10210],
        [10000, 10220, 10410, 10620],
        [10000, 9900, 10020, 10110],
    ],
    portfolio_statistics: {
        mean: 10480,
        median: 10310,
        std: 520,
        min: 9600,
        max: 10890,
        p5: 9640,
        p25: 10080,
        p75: 10600,
        p95: 10850,
        prob_loss: 0.08,
    },
    weights: [
        { ticker: "SPY", weight: 0.6 },
        { ticker: "TLT", weight: 0.3 },
        { ticker: "GLD", weight: 0.1 },
    ],
    asset_statistics: [
        {
            ticker: "SPY",
            weight: 0.6,
            annual_return: 0.09,
            annual_volatility: 0.18,
        },
        {
            ticker: "TLT",
            weight: 0.3,
            annual_return: 0.04,
            annual_volatility: 0.11,
        },
        {
            ticker: "GLD",
            weight: 0.1,
            annual_return: 0.05,
            annual_volatility: 0.14,
        },
    ],
    correlation_matrix: {
        SPY: { SPY: 1, TLT: -0.2, GLD: 0.15 },
        TLT: { SPY: -0.2, TLT: 1, GLD: 0.05 },
        GLD: { SPY: 0.15, TLT: 0.05, GLD: 1 },
    },
};

const dcaOptimizerResponse = {
    by_ratio: [
        { ratio: 0.1, cagr: 0.07 },
        { ratio: 0.5, cagr: 0.11 },
        { ratio: 1.0, cagr: 0.09 },
    ],
    by_duration: [
        { duration: 30, cagr: 0.08 },
        { duration: 90, cagr: 0.11 },
        { duration: 180, cagr: 0.1 },
    ],
    raw_results: [{ ratio: 0.5, duration: 90, cagr: 0.11, total_return: 0.18 }],
};

const paretoOptimizerResponse = {
    objective_a_name: "cagr",
    objective_b_name: "max_drawdown",
    n_evaluated: 3,
    all_points: [
        {
            strategy_name: "NoRebalance",
            tickers_used: ["SPY", "TLT"],
            params: {},
            metrics: { cagr: 0.1, max_drawdown: 0.12, sharpe: 0.8 },
            objective_a: 0.1,
            objective_b: 0.12,
            is_pareto_optimal: true,
        },
        {
            strategy_name: "DualMomentum",
            tickers_used: ["SPY", "TLT"],
            params: {},
            metrics: { cagr: 0.08, max_drawdown: 0.07, sharpe: 1.0 },
            objective_a: 0.08,
            objective_b: 0.07,
            is_pareto_optimal: true,
        },
        {
            strategy_name: "Rebalance",
            tickers_used: ["SPY", "TLT"],
            params: {},
            metrics: { cagr: 0.07, max_drawdown: 0.15, sharpe: 0.6 },
            objective_a: 0.07,
            objective_b: 0.15,
            is_pareto_optimal: false,
        },
    ],
    pareto_front: [
        {
            strategy_name: "NoRebalance",
            tickers_used: ["SPY", "TLT"],
            params: {},
            metrics: { cagr: 0.1, max_drawdown: 0.12, sharpe: 0.8 },
            objective_a: 0.1,
            objective_b: 0.12,
            is_pareto_optimal: true,
        },
        {
            strategy_name: "DualMomentum",
            tickers_used: ["SPY", "TLT"],
            params: {},
            metrics: { cagr: 0.08, max_drawdown: 0.07, sharpe: 1.0 },
            objective_a: 0.08,
            objective_b: 0.07,
            is_pareto_optimal: true,
        },
    ],
    dominated_points: [
        {
            strategy_name: "Rebalance",
            tickers_used: ["SPY", "TLT"],
            params: {},
            metrics: { cagr: 0.07, max_drawdown: 0.15, sharpe: 0.6 },
            objective_a: 0.07,
            objective_b: 0.15,
            is_pareto_optimal: false,
        },
    ],
    warnings: [],
};

const efficientFrontierResponse = {
    portfolios: [
        {
            expected_return: 0.06,
            volatility: 0.08,
            sharpe_ratio: 0.5,
            weights: { SPY: 0.2, TLT: 0.6, GLD: 0.2 },
        },
        {
            expected_return: 0.09,
            volatility: 0.14,
            sharpe_ratio: 0.64,
            weights: { SPY: 0.6, TLT: 0.25, GLD: 0.15 },
        },
    ],
    frontier: [
        {
            expected_return: 0.06,
            volatility: 0.08,
            sharpe_ratio: 0.5,
            weights: { SPY: 0.2, TLT: 0.6, GLD: 0.2 },
        },
        {
            expected_return: 0.09,
            volatility: 0.14,
            sharpe_ratio: 0.64,
            weights: { SPY: 0.6, TLT: 0.25, GLD: 0.15 },
        },
    ],
    max_sharpe: {
        expected_return: 0.09,
        volatility: 0.14,
        sharpe_ratio: 0.64,
        weights: { SPY: 0.6, TLT: 0.25, GLD: 0.15 },
    },
    min_volatility: {
        expected_return: 0.06,
        volatility: 0.08,
        sharpe_ratio: 0.5,
        weights: { SPY: 0.2, TLT: 0.6, GLD: 0.2 },
    },
    asset_stats: [
        { ticker: "SPY", annual_return: 0.09, annual_volatility: 0.18 },
        { ticker: "TLT", annual_return: 0.04, annual_volatility: 0.1 },
        { ticker: "GLD", annual_return: 0.05, annual_volatility: 0.14 },
    ],
    correlation_matrix: {
        SPY: { SPY: 1, TLT: -0.2, GLD: 0.12 },
        TLT: { SPY: -0.2, TLT: 1, GLD: 0.05 },
        GLD: { SPY: 0.12, TLT: 0.05, GLD: 1 },
    },
};

const experiments = [
    {
        run_id: "run-001",
        engine_name: "backtrader",
        strategy_name: "NoRebalance",
        created_at: "2024-01-01T12:00:00Z",
        config_hash: "abc123",
        data_snapshot_id: "snap-abc123",
    },
    {
        run_id: "run-002",
        engine_name: "backtrader",
        strategy_name: "DualMomentum",
        created_at: "2024-01-02T12:00:00Z",
        config_hash: "def456",
        data_snapshot_id: "snap-def456",
    },
];

const providerStatus = {
    providers: [
        {
            provider: "alpaca",
            is_available: true,
            last_success: "2024-01-02T12:00:00Z",
            last_error: null,
            total_requests: 10,
            total_errors: 0,
        },
    ],
};

async function fulfillJson(route: Route, body: unknown): Promise<void> {
    await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(body),
    });
}

async function mockApi(page: Page): Promise<void> {
    await page.route("**/_playwright_api/**", async (route) => {
        const request = route.request();
        const url = new URL(request.url());
        const apiPath = url.pathname.replace("/_playwright_api", "");

        if (
            request.method() === "GET" &&
            apiPath === "/api/simulations/funds"
        ) {
            await fulfillJson(route, funds);
            return;
        }

        if (
            request.method() === "GET" &&
            apiPath === "/api/backtesting/strategies"
        ) {
            await fulfillJson(route, strategies);
            return;
        }

        if (request.method() === "GET" && apiPath === "/api/data-status/") {
            await fulfillJson(route, dataStatus);
            return;
        }

        if (request.method() === "GET" && apiPath === "/api/simulations/run") {
            await fulfillJson(route, simulationResponse);
            return;
        }

        if (
            request.method() === "POST" &&
            apiPath === "/api/simulations/bond-ladder/run"
        ) {
            await fulfillJson(route, bondLadderResponse);
            return;
        }

        if (request.method() === "POST" && apiPath === "/api/monte-carlo/run") {
            await fulfillJson(route, monteCarloResponse);
            return;
        }

        if (
            request.method() === "POST" &&
            apiPath === "/api/monte-carlo/multi-asset/run"
        ) {
            await fulfillJson(route, multiAssetMonteCarloResponse);
            return;
        }

        if (request.method() === "POST" && apiPath === "/api/optimizer/run") {
            await fulfillJson(route, dcaOptimizerResponse);
            return;
        }

        if (
            request.method() === "POST" &&
            apiPath === "/api/optimizer/pareto/run"
        ) {
            await fulfillJson(route, paretoOptimizerResponse);
            return;
        }

        if (
            request.method() === "POST" &&
            apiPath === "/api/optimizer/efficient-frontier/run"
        ) {
            await fulfillJson(route, efficientFrontierResponse);
            return;
        }

        if (request.method() === "GET" && apiPath === "/api/experiments/list") {
            await fulfillJson(route, experiments);
            return;
        }

        if (
            request.method() === "GET" &&
            apiPath === "/api/realtime-quotes/provider-status"
        ) {
            await fulfillJson(route, providerStatus);
            return;
        }

        await fulfillJson(route, {});
    });
}

test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
        localStorage.setItem("finbot-disclaimer-accepted", "true");
    });
    await mockApi(page);
});

function trackPageErrors(page: Page): string[] {
    const pageErrors: string[] = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));
    return pageErrors;
}

for (const route of APP_ROUTES) {
    test(`smoke loads ${route.path}`, async ({ page }) => {
        const pageErrors = trackPageErrors(page);

        await page.goto(route.path);
        await page.waitForLoadState("networkidle");

        await expect(
            page.locator("main").getByRole("heading", { name: route.heading }),
        ).toBeVisible();
        await expect(pageErrors).toHaveLength(0);
    });
}

test.describe("adjacent research workspaces", () => {
    test("simulations runs the bond ladder tab", async ({ page }) => {
        const pageErrors = trackPageErrors(page);

        await page.goto("/simulations");
        await page.waitForLoadState("networkidle");

        await page.getByRole("tab", { name: "Bond Ladder" }).click();
        await page.getByRole("button", { name: "Run Bond Ladder" }).click();

        await expect(page.getByText("Bond Ladder Metrics")).toBeVisible();
        await expect(page.getByText("1Y-10Y Ladder")).toBeVisible();
        await expect(page.getByText("BOND_LADDER")).toBeVisible();
        await expect(pageErrors).toHaveLength(0);
    });

    test("monte carlo runs single and multi-asset tabs", async ({ page }) => {
        const pageErrors = trackPageErrors(page);

        await page.goto("/monte-carlo");
        await page.waitForLoadState("networkidle");

        await page.getByRole("button", { name: "Run Simulation" }).click();
        await expect(page.getByText("Price Path Fan Chart")).toBeVisible();
        await expect(page.getByText("Simulation Statistics")).toBeVisible();

        await page.getByRole("tab", { name: "Multi-Asset" }).click();
        await page
            .getByRole("button", { name: "Run Multi-Asset Simulation" })
            .click();

        await expect(page.getByText("Portfolio Fan Chart")).toBeVisible();
        await expect(
            page.getByText("Historical Correlation Matrix"),
        ).toBeVisible();
        await expect(
            page.getByText("Asset Weights and Historical Stats"),
        ).toBeVisible();
        await expect(pageErrors).toHaveLength(0);
    });

    test("optimizer runs dca, pareto, and efficient frontier tabs", async ({
        page,
    }) => {
        const pageErrors = trackPageErrors(page);

        await page.goto("/optimizer");
        await page.waitForLoadState("networkidle");

        await page.getByRole("button", { name: "Run DCA Optimizer" }).click();
        await expect(page.getByText("Performance by DCA Ratio")).toBeVisible();

        await page.getByRole("tab", { name: "Pareto" }).click();
        await page.getByRole("button", { name: "Run Pareto Sweep" }).click();
        await expect(page.getByText("Pareto-Optimal Strategies")).toBeVisible();
        await expect(
            page.getByRole("cell", { name: "NoRebalance" }),
        ).toBeVisible();

        await page.getByRole("tab", { name: "Efficient Frontier" }).click();
        await page
            .getByRole("button", { name: "Run Efficient Frontier" })
            .click();
        await expect(page.getByText("Highlighted Portfolios")).toBeVisible();
        await expect(
            page.getByRole("cell", { name: "Max Sharpe" }),
        ).toBeVisible();
        await expect(
            page.getByText("Historical Correlation Matrix"),
        ).toBeVisible();
        await expect(pageErrors).toHaveLength(0);
    });
});

test.describe("mobile navigation", () => {
    test.use({ viewport: { width: 390, height: 844 } });

    test("opens the mobile menu and navigates to Health Economics", async ({
        page,
    }) => {
        await page.goto("/");
        await page.getByRole("button", { name: "Open menu" }).click();
        await page.getByRole("link", { name: "Health Economics" }).click();

        await expect(page).toHaveURL(/\/health-economics$/);
        await expect(
            page
                .locator("main")
                .getByRole("heading", { name: "Health Economics" }),
        ).toBeVisible();
    });
});
