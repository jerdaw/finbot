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

const backtestResponse = {
    stats: {
        CAGR: 0.1245,
        Sharpe: 1.214,
        "Max Drawdown": -0.118,
        ROI: 0.422,
    },
    value_history: [
        { date: "2024-01-01", Value: 10000 },
        { date: "2024-02-01", Value: 10350 },
        { date: "2024-03-01", Value: 10422 },
    ],
    trades: [
        {
            date: "2024-01-02",
            ticker: "SPY",
            action: "BUY",
            size: 50,
            price: 200,
            value: 10000,
        },
    ],
    applied_cost_assumptions: {
        commission_mode: "percentage",
        commission_per_share: 0.001,
        commission_bps: 1,
        commission_minimum: 0,
        spread_bps: 2,
        slippage_bps: 1,
        commission_label: "1 bps percentage commission",
        spread_label: "2 bps spread",
        slippage_label: "1 bps slippage",
        estimated_only: true,
    },
    cost_summary: {
        total_commission: 4.25,
        total_spread: 2.1,
        total_slippage: 1.3,
        total_costs: 7.65,
        costs_by_symbol: { SPY: 7.65 },
        cost_events: [],
    },
    missing_data_summary: {
        policy: "forward_fill",
        total_missing_rows: 1,
        total_missing_cells: 1,
        remaining_missing_cells: 0,
        note: "Forward-filled a single missing observation in SPY.",
        tickers: [
            {
                ticker: "SPY",
                rows_before: 3,
                rows_after: 3,
                rows_dropped: 0,
                missing_rows: 1,
                missing_cells: 1,
                remaining_missing_cells: 0,
                had_missing_data: true,
            },
        ],
    },
    benchmark_stats: {
        alpha: 0.012,
        beta: 0.98,
        r_squared: 0.94,
        tracking_error: 0.031,
        information_ratio: 0.56,
        up_capture: 1.05,
        down_capture: 0.92,
        benchmark_name: "SPY",
        n_observations: 3,
    },
    benchmark_value_history: [
        { date: "2024-01-01", Value: 10000 },
        { date: "2024-02-01", Value: 10200 },
        { date: "2024-03-01", Value: 10310 },
    ],
    rolling_metrics: {
        window: 63,
        n_obs: 3,
        sharpe: [1.0, 1.1, 1.2],
        volatility: [0.11, 0.105, 0.102],
        beta: [0.95, 0.98, 1.0],
        dates: ["2024-01-01", "2024-02-01", "2024-03-01"],
        mean_sharpe: 1.1,
        mean_vol: 0.106,
        mean_beta: 0.977,
    },
    regime_reference_ticker: "SPY",
    regime_summary: [
        {
            regime: "Bull",
            count_periods: 1,
            total_days: 63,
            cagr: 0.1245,
            volatility: 0.13,
            sharpe: 1.21,
            total_return: 0.0422,
        },
    ],
    regime_periods: [
        {
            regime: "Bull",
            start: "2024-01-01",
            end: "2024-03-01",
            days: 63,
            market_return: 0.031,
            market_volatility: 0.14,
            portfolio_return: 0.0422,
            portfolio_volatility: 0.12,
        },
    ],
    cashflow_events: [
        {
            scheduled_date: "2024-02-01",
            applied_date: "2024-02-01",
            label: "Monthly contribution",
            source: "recurring",
            direction: "contribution",
            amount: 500,
            cash_after: 500,
            portfolio_value_after: 10850,
        },
    ],
    real_value_history: [
        { date: "2024-01-01", Value: 10000 },
        { date: "2024-02-01", Value: 10280 },
        { date: "2024-03-01", Value: 10310 },
    ],
    withdrawal_durability: {
        survived_to_end: true,
        depletion_date: null,
        ending_nominal_value: 10422,
        ending_real_value: 10310,
        min_nominal_value: 10000,
        min_real_value: 10000,
        total_contributions: 500,
        total_withdrawals: 0,
        net_cashflow: 500,
        real_total_return: 0.031,
        inflation_rate: 0.02,
    },
    allocation_history: [
        { date: "2024-01-01", SPY: 1 },
        { date: "2024-02-01", SPY: 1 },
        { date: "2024-03-01", SPY: 1 },
    ],
    rebalance_events: [
        {
            date: "2024-01-01",
            event_type: "initial_allocation",
            trade_count: 1,
            symbols: ["SPY"],
            gross_trade_value: 10000,
            net_trade_value: 0,
            portfolio_value: 10000,
            cash_after: 0,
        },
    ],
    monthly_returns: [
        {
            period: "2024-01",
            start_value: 10000,
            end_value: 10350,
            return_pct: 0.035,
        },
    ],
    annual_returns: [
        {
            period: "2024",
            start_value: 10000,
            end_value: 10422,
            return_pct: 0.0422,
        },
    ],
    walk_forward_request: {
        tickers: ["SPY"],
        strategy: "NoRebalance",
        strategy_params: { equity_proportions: [1] },
        start_date: "2010-01-01",
        end_date: "2024-12-31",
        initial_cash: 10000,
        train_window: 756,
        test_window: 126,
        step_size: 63,
        anchored: false,
        include_train: false,
        reason: "Carry this allocation into walk-forward validation.",
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

const experimentCompareResponse = {
    assumptions: [
        {
            run_id: "run-001",
            strategy: "NoRebalance",
            engine: "backtrader",
            created_at: "2024-01-01T12:00:00Z",
            config_hash: "abc123",
            data_snapshot_id: "snap-abc123",
            symbols: ["SPY"],
        },
        {
            run_id: "run-002",
            strategy: "DualMomentum",
            engine: "backtrader",
            created_at: "2024-01-02T12:00:00Z",
            config_hash: "def456",
            data_snapshot_id: "snap-def456",
            symbols: ["SPY", "TLT"],
        },
    ],
    metrics: [
        {
            run_id: "run-001",
            strategy: "NoRebalance",
            cagr: 0.12,
            sharpe: 1.05,
            max_drawdown: -0.11,
        },
        {
            run_id: "run-002",
            strategy: "DualMomentum",
            cagr: 0.1,
            sharpe: 0.96,
            max_drawdown: -0.08,
        },
    ],
};

const saveExperimentResponse = {
    run_id: "bt-001",
    strategy_name: "NoRebalance",
    created_at: "2024-03-02T14:30:00Z",
    config_hash: "cfg-001",
    data_snapshot_id: "snap-001",
};

const walkForwardResponse = {
    config: {
        strategy: "NoRebalance",
        tickers: ["SPY"],
    },
    windows: [
        {
            window_id: 1,
            train_start: "2021-01-01",
            train_end: "2023-12-31",
            test_start: "2024-01-01",
            test_end: "2024-06-30",
            metrics: {
                CAGR: 0.11,
                Sharpe: 0.88,
                "Max Drawdown": -0.09,
            },
        },
    ],
    summary_metrics: {
        avg_cagr: 0.11,
        avg_sharpe: 0.88,
        worst_drawdown: -0.09,
    },
    summary_table: [
        {
            window: "W1",
            cagr: 0.11,
            sharpe: 0.88,
            max_drawdown: -0.09,
        },
    ],
};

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
            request.method() === "POST" &&
            apiPath === "/api/backtesting/run"
        ) {
            await fulfillJson(route, backtestResponse);
            return;
        }

        if (
            request.method() === "POST" &&
            apiPath === "/api/experiments/save"
        ) {
            await fulfillJson(route, saveExperimentResponse);
            return;
        }

        if (
            request.method() === "POST" &&
            apiPath === "/api/experiments/compare"
        ) {
            await fulfillJson(route, experimentCompareResponse);
            return;
        }

        if (
            request.method() === "POST" &&
            apiPath === "/api/walk-forward/run"
        ) {
            await fulfillJson(route, walkForwardResponse);
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

async function gotoAndWaitForHeading(
    page: Page,
    path: string,
    heading: string | RegExp,
): Promise<void> {
    await page.goto(path);
    await expect(
        page.locator("main").getByRole("heading", { name: heading }),
    ).toBeVisible();
}

async function waitForApiRequest(
    page: Page,
    apiPath: string,
): Promise<void> {
    await page.waitForRequest((request) => {
        const url = new URL(request.url());
        return url.pathname === `/_playwright_api${apiPath}`;
    });
}

function visibleByTestId(page: Page, testId: string) {
    return page.locator(`[data-testid="${testId}"]:visible`);
}

function trackPageErrors(page: Page): string[] {
    const pageErrors: string[] = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));
    return pageErrors;
}

for (const route of APP_ROUTES) {
    test(`smoke loads ${route.path}`, async ({ page }) => {
        const pageErrors = trackPageErrors(page);

        await gotoAndWaitForHeading(page, route.path, route.heading);
        await expect(pageErrors).toHaveLength(0);
    });
}

test.describe("adjacent research workspaces", () => {
    test("simulations runs the bond ladder tab", async ({ page }) => {
        const pageErrors = trackPageErrors(page);

        await gotoAndWaitForHeading(page, "/simulations", "Research Simulations");

        await page.getByRole("tab", { name: "Bond Ladder" }).click();
        await expect(
            page.getByRole("heading", { name: "Bond Ladder" }),
        ).toBeVisible();
        await Promise.all([
            waitForApiRequest(page, "/api/simulations/bond-ladder/run"),
            page.getByRole("button", { name: "Run Bond Ladder" }).click(),
        ]);

        await expect(page.getByText("Bond Ladder Metrics")).toBeVisible();
        await expect(page.getByText("1Y-10Y Ladder")).toBeVisible();
        await expect(page.getByText("BOND_LADDER")).toBeVisible();
        await expect(pageErrors).toHaveLength(0);
    });

    test("monte carlo runs single and multi-asset tabs", async ({ page }) => {
        const pageErrors = trackPageErrors(page);

        await gotoAndWaitForHeading(page, "/monte-carlo", "Monte Carlo Lab");

        await Promise.all([
            waitForApiRequest(page, "/api/monte-carlo/run"),
            page.getByRole("button", { name: "Run Simulation" }).click(),
        ]);
        await expect(page.getByText("Price Path Fan Chart")).toBeVisible();
        await expect(page.getByText("Simulation Statistics")).toBeVisible();

        await page.getByRole("tab", { name: "Multi-Asset" }).click();
        await Promise.all([
            waitForApiRequest(page, "/api/monte-carlo/multi-asset/run"),
            page
                .getByRole("button", { name: "Run Multi-Asset Simulation" })
                .click(),
        ]);

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

        await gotoAndWaitForHeading(page, "/optimizer", "Portfolio Optimizer");

        await Promise.all([
            waitForApiRequest(page, "/api/optimizer/run"),
            page.getByRole("button", { name: "Run DCA Optimizer" }).click(),
        ]);
        await expect(page.getByText("Performance by DCA Ratio")).toBeVisible();

        await page.getByRole("tab", { name: "Pareto" }).click();
        await Promise.all([
            waitForApiRequest(page, "/api/optimizer/pareto/run"),
            page.getByRole("button", { name: "Run Pareto Sweep" }).click(),
        ]);
        await expect(page.getByText("Pareto-Optimal Strategies")).toBeVisible();
        await expect(
            page.getByRole("cell", { name: "NoRebalance" }),
        ).toBeVisible();

        await page.getByRole("tab", { name: "Efficient Frontier" }).click();
        await Promise.all([
            waitForApiRequest(page, "/api/optimizer/efficient-frontier/run"),
            page
                .getByRole("button", { name: "Run Efficient Frontier" })
                .click(),
        ]);
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

test.describe("backtesting workflows", () => {
    test("runs a backtest, saves an experiment, and hands off to walk-forward", async ({
        page,
    }) => {
        const pageErrors = trackPageErrors(page);

        await gotoAndWaitForHeading(page, "/backtesting", "Strategy Backtester");

        await expect(
            page.getByRole("button", { name: "Save Experiment" }),
        ).toHaveCount(0);
        await expect(
            page.getByRole("button", { name: "Export CSV" }),
        ).toHaveCount(0);
        await expect(
            page.getByRole("button", { name: "Export JSON" }),
        ).toHaveCount(0);

        await Promise.all([
            waitForApiRequest(page, "/api/backtesting/run"),
            page.getByRole("button", { name: "Run Backtest" }).click(),
        ]);

        await expect(page.getByText("Execution Frictions")).toBeVisible();
        await expect(page.getByText("Missing Data Handling")).toBeVisible();
        await expect(page.getByText("Walk-Forward Follow-Up")).toBeVisible();

        await Promise.all([
            waitForApiRequest(page, "/api/experiments/save"),
            page.getByRole("button", { name: "Save Experiment" }).click(),
        ]);
        await expect(page.getByText("Experiment Lineage")).toBeVisible();
        await expect(page.getByText("bt-001")).toBeVisible();

        await page
            .getByRole("link", { name: "Open Walk-Forward Analysis" })
            .click();

        await expect(page).toHaveURL(/\/walk-forward\?/);
        await expect(page.locator('input[value="SPY"]').first()).toBeVisible();
        await expect(page.locator('input[value="10000"]').first()).toBeVisible();
        await expect(page.locator('input[value="756"]').first()).toBeVisible();
        await expect(pageErrors).toHaveLength(0);
    });

    test("blocks runs when allocation weights do not sum to 100%", async ({
        page,
    }) => {
        await gotoAndWaitForHeading(page, "/backtesting", "Strategy Backtester");

        await page.getByRole("button", { name: "Add Asset" }).click();
        await page.getByPlaceholder("Ticker 2").fill("TLT");
        await page.getByLabel("Weight for asset 1").fill("60");
        await page.getByLabel("Weight for asset 2").fill("30");

        await page.getByRole("button", { name: "Run Backtest" }).click();

        await expect(
            page.getByText("Allocation weights must add up to 100%."),
        ).toBeVisible();
    });

    test("blocks runs when allocation tickers are duplicated", async ({
        page,
    }) => {
        await gotoAndWaitForHeading(page, "/backtesting", "Strategy Backtester");

        await page.getByRole("button", { name: "Add Asset" }).click();
        await page.getByPlaceholder("Ticker 2").fill("SPY");
        await page.getByLabel("Weight for asset 1").fill("50");
        await page.getByLabel("Weight for asset 2").fill("50");

        await page.getByRole("button", { name: "Run Backtest" }).click();

        await expect(
            page.getByText("Each asset ticker must be unique."),
        ).toBeVisible();
    });

    test("blocks runs when one-time cashflow entries are incomplete", async ({
        page,
    }) => {
        await gotoAndWaitForHeading(page, "/backtesting", "Strategy Backtester");

        await page.getByRole("button", { name: "Add Event" }).click();
        await page.getByRole("button", { name: "Run Backtest" }).click();

        await expect(
            page.getByText("Each one-time cashflow needs a non-zero amount."),
        ).toBeVisible();
    });
});

test.describe("experiment comparison", () => {
    test("compares selected experiment runs", async ({ page }) => {
        const pageErrors = trackPageErrors(page);

        await gotoAndWaitForHeading(page, "/experiments", "Experiments");

        const firstExperiment = visibleByTestId(page, "experiment-row-run-001")
            .or(visibleByTestId(page, "experiment-card-run-001"));
        const secondExperiment = visibleByTestId(page, "experiment-row-run-002")
            .or(visibleByTestId(page, "experiment-card-run-002"));

        await expect(firstExperiment).toBeVisible();
        await expect(secondExperiment).toBeVisible();
        await firstExperiment.click();
        await secondExperiment.click();
        await Promise.all([
            waitForApiRequest(page, "/api/experiments/compare"),
            page.getByRole("button", { name: "Compare (2)" }).click(),
        ]);

        await expect(page.getByText("Assumptions Comparison")).toBeVisible();
        await expect(page.getByText("Metrics Comparison")).toBeVisible();
        await expect(page.getByText("Metric Rankings")).toBeVisible();
        await expect(pageErrors).toHaveLength(0);
    });
});

test.describe("walk-forward handoff", () => {
    test("prefills the walk-forward form from URL parameters and can run", async ({
        page,
    }) => {
        const pageErrors = trackPageErrors(page);

        await gotoAndWaitForHeading(
            page,
            "/walk-forward?tickers=SPY%2CTLT&strategy=NoRebalance&start_date=2015-01-01&end_date=2024-12-31&initial_cash=15000&train_window=756&test_window=126&step_size=63&anchored=true&include_train=true&strategy_params=%7B%22equity_proportions%22%3A%5B0.6%2C0.4%5D%7D",
            "Walk-Forward Analysis",
        );

        await expect(page.locator('input[value="SPY,TLT"]').first()).toBeVisible();
        await expect(page.locator('input[value="15000"]').first()).toBeVisible();
        await expect(page.locator('input[value="756"]').first()).toBeVisible();

        await Promise.all([
            waitForApiRequest(page, "/api/walk-forward/run"),
            page.getByRole("button", { name: "Run Walk-Forward" }).click(),
        ]);

        await expect(page.getByText("Summary Table")).toBeVisible();
        await expect(page.getByText("Timeline")).toBeVisible();
        await expect(pageErrors).toHaveLength(0);
    });
});

test.describe("mobile navigation", () => {
    test.use({ viewport: { width: 390, height: 844 } });

    test("opens the mobile menu and navigates across core routes", async ({
        page,
    }) => {
        const pageErrors = trackPageErrors(page);

        await page.goto("/");
        await page.getByRole("button", { name: "Open menu" }).click();
        await page.getByRole("link", { name: "Backtesting" }).click();

        await expect(page).toHaveURL(/\/backtesting$/);
        await expect(
            page
                .locator("main")
                .getByRole("heading", { name: "Strategy Backtester" }),
        ).toBeVisible();

        await page.getByRole("button", { name: "Open menu" }).click();
        await page.getByRole("link", { name: "Health Economics" }).click();

        await expect(page).toHaveURL(/\/health-economics$/);
        await expect(
            page
                .locator("main")
                .getByRole("heading", { name: "Health Economics" }),
        ).toBeVisible();

        await page.getByRole("button", { name: "Open menu" }).click();
        await page.getByRole("link", { name: "Monte Carlo" }).click();

        await expect(page).toHaveURL(/\/monte-carlo$/);
        await expect(
            page.locator("main").getByRole("heading", { name: "Monte Carlo Lab" }),
        ).toBeVisible();
        await expect(pageErrors).toHaveLength(0);
    });
});
