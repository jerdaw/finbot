import { expect, test, type Page, type Route } from "@playwright/test";

const APP_ROUTES = [
  { path: "/", heading: /Welcome to Finbot/i },
  { path: "/simulations", heading: "Fund Simulations" },
  { path: "/backtesting", heading: "Strategy Backtester" },
  { path: "/optimizer", heading: "DCA Optimizer" },
  { path: "/monte-carlo", heading: "Monte Carlo Simulation" },
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

    if (request.method() === "GET" && apiPath === "/api/simulations/funds") {
      await fulfillJson(route, funds);
      return;
    }

    if (request.method() === "GET" && apiPath === "/api/backtesting/strategies") {
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

    if (request.method() === "GET" && apiPath === "/api/experiments/list") {
      await fulfillJson(route, experiments);
      return;
    }

    if (request.method() === "GET" && apiPath === "/api/realtime-quotes/provider-status") {
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

for (const route of APP_ROUTES) {
  test(`smoke loads ${route.path}`, async ({ page }) => {
    const pageErrors: string[] = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));

    await page.goto(route.path);
    await page.waitForLoadState("networkidle");

    await expect(page.locator("main").getByRole("heading", { name: route.heading })).toBeVisible();
    await expect(pageErrors).toHaveLength(0);
  });
}

test.describe("mobile navigation", () => {
  test.use({ viewport: { width: 390, height: 844 } });

  test("opens the mobile menu and navigates to Health Economics", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "Open menu" }).click();
    await page.getByRole("link", { name: "Health Economics" }).click();

    await expect(page).toHaveURL(/\/health-economics$/);
    await expect(page.locator("main").getByRole("heading", { name: "Health Economics" })).toBeVisible();
  });
});
