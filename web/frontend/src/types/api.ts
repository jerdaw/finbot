/* Shared TypeScript types mirroring backend Pydantic schemas */

// --- Common ---
export interface TimeSeries {
  name: string;
  dates: string[];
  values: (number | null)[];
}

// --- Simulations ---
export interface FundInfo {
  ticker: string;
  name: string;
  leverage: number;
  annual_er_pct: number;
}

export interface SimulationMetric {
  ticker: string;
  name: string;
  leverage: number;
  total_return: number | null;
  cagr: number | null;
  volatility: number | null;
  max_drawdown: number | null;
}

export interface SimulationResponse {
  series: TimeSeries[];
  metrics: SimulationMetric[];
}

// --- Backtesting ---
export interface StrategyParam {
  name: string;
  type: string;
  default: number | string;
  min: number | null;
  description: string;
}

export interface StrategyInfo {
  name: string;
  description: string;
  params: StrategyParam[];
  min_assets: number;
}

export interface BacktestRequest {
  tickers: string[];
  strategy: string;
  strategy_params: Record<string, unknown>;
  start_date?: string;
  end_date?: string;
  initial_cash: number;
  benchmark_ticker?: string;
  risk_free_rate?: number;
  recurring_cashflows?: RecurringCashflowRule[];
  one_time_cashflows?: OneTimeCashflowEvent[];
  inflation_rate?: number;
}

export interface RecurringCashflowRule {
  amount: number;
  frequency: "monthly" | "quarterly" | "yearly";
  start_date?: string;
  end_date?: string;
  label?: string;
}

export interface OneTimeCashflowEvent {
  date: string;
  amount: number;
  label?: string;
}

export interface TradeRecord {
  date: string;
  ticker: string;
  action: string;
  size: number;
  price: number;
  value: number;
}

export interface BacktestBenchmarkStats {
  alpha: number | null;
  beta: number | null;
  r_squared: number | null;
  tracking_error: number | null;
  information_ratio: number | null;
  up_capture: number | null;
  down_capture: number | null;
  benchmark_name: string;
  n_observations: number;
}

export interface ReturnTableRow {
  period: string;
  start_value: number | null;
  end_value: number | null;
  return_pct: number | null;
}

export interface BacktestRegimeSummary {
  regime: string;
  count_periods: number;
  total_days: number;
  cagr: number | null;
  volatility: number | null;
  sharpe: number | null;
  total_return: number | null;
}

export interface BacktestRegimePeriod {
  regime: string;
  start: string;
  end: string;
  days: number;
  market_return: number | null;
  market_volatility: number | null;
  portfolio_return: number | null;
  portfolio_volatility: number | null;
}

export interface CashflowEventRecord {
  scheduled_date: string;
  applied_date: string;
  label: string;
  source: "recurring" | "one_time";
  direction: "contribution" | "withdrawal";
  amount: number;
  cash_after: number | null;
  portfolio_value_after: number | null;
}

export interface WithdrawalDurabilitySummary {
  survived_to_end: boolean;
  depletion_date: string | null;
  ending_nominal_value: number | null;
  ending_real_value: number | null;
  min_nominal_value: number | null;
  min_real_value: number | null;
  total_contributions: number;
  total_withdrawals: number;
  net_cashflow: number;
  real_total_return: number | null;
  inflation_rate: number;
}

export interface RebalanceEventRecord {
  date: string;
  event_type: "initial_allocation" | "rebalance" | "trade";
  trade_count: number;
  symbols: string[];
  gross_trade_value: number | null;
  net_trade_value: number | null;
  portfolio_value: number | null;
  cash_after: number | null;
}

export interface BacktestResponse {
  stats: Record<string, unknown>;
  value_history: Record<string, unknown>[];
  trades: TradeRecord[];
  benchmark_stats?: BacktestBenchmarkStats | null;
  benchmark_value_history?: Record<string, unknown>[];
  rolling_metrics?: RollingMetricsResponse | null;
  regime_reference_ticker?: string | null;
  regime_summary?: BacktestRegimeSummary[];
  regime_periods?: BacktestRegimePeriod[];
  cashflow_events?: CashflowEventRecord[];
  real_value_history?: Record<string, unknown>[];
  withdrawal_durability?: WithdrawalDurabilitySummary | null;
  allocation_history?: Record<string, unknown>[];
  rebalance_events?: RebalanceEventRecord[];
  monthly_returns?: ReturnTableRow[];
  annual_returns?: ReturnTableRow[];
}

// --- Monte Carlo ---
export interface MonteCarloRequest {
  ticker: string;
  sim_periods: number;
  n_sims: number;
  start_price?: number;
}

export interface PercentileBand {
  label: string;
  values: (number | null)[];
}

export interface MonteCarloResponse {
  periods: number[];
  bands: PercentileBand[];
  sample_paths: (number | null)[][];
  statistics: Record<string, number | null>;
}

// --- DCA Optimizer ---
export interface DCAOptimizerRequest {
  ticker: string;
  ratio_range?: number[];
  dca_durations?: number[];
  dca_steps?: number[];
  trial_durations?: number[];
  starting_cash?: number;
  start_step?: number;
}

export interface DCAOptimizerResponse {
  by_ratio: Record<string, unknown>[];
  by_duration: Record<string, unknown>[];
  raw_results: Record<string, unknown>[];
}

// --- Health Economics ---
export interface InterventionInput {
  name: string;
  cost_per_year: number;
  cost_std?: number;
  utility_gain: number;
  utility_gain_std?: number;
  mortality_reduction?: number;
  mortality_reduction_std?: number;
}

export interface QALYRequest {
  intervention: InterventionInput;
  baseline_utility?: number;
  baseline_mortality?: number;
  time_horizon?: number;
  n_sims?: number;
  discount_rate?: number;
  seed?: number;
}

export interface QALYResponse {
  mean_cost: number;
  mean_qaly: number;
  cost_percentiles: Record<string, number>;
  qaly_percentiles: Record<string, number>;
  survival_curve: number[];
  annual_cost_means: number[];
  annual_qaly_means: number[];
}

export interface CEARequest {
  interventions: QALYRequest[];
  comparator: string;
  wtp_thresholds?: number[];
}

export interface CEAResponse {
  icer_table: Record<string, unknown>[];
  ceac: Record<string, unknown>[];
  ce_plane: Record<string, Record<string, number | null>[]>;
  nmb: Record<string, unknown>[];
  summary: Record<string, unknown>[];
}

export interface TreatmentOptimizerRequest {
  cost_per_dose: number;
  cost_per_dose_std?: number;
  qaly_gain_per_dose?: number;
  qaly_gain_per_dose_std?: number;
  frequencies?: number[];
  durations?: number[];
  baseline_utility?: number;
  baseline_mortality?: number;
  mortality_reduction_per_dose?: number;
  discount_rate?: number;
  wtp_threshold?: number;
  n_sims?: number;
  seed?: number;
}

export interface TreatmentOptimizerResponse {
  results: Record<string, unknown>[];
  best_schedule: Record<string, unknown>;
}

export interface ScenarioRequest {
  scenario: string;
  n_sims?: number;
  seed?: number;
  wtp_threshold?: number;
}

export interface ScenarioResponse {
  scenario_name: string;
  description: string;
  intervention_name: string;
  comparator_name: string;
  icer: number | null;
  nmb: number;
  is_cost_effective: boolean;
  qaly_gain: number;
  cost_difference: number;
  n_simulations: number;
  summary_stats: Record<string, number>;
}

// --- Walk-Forward ---
export interface WalkForwardRequest {
  tickers: string[];
  strategy: string;
  strategy_params: Record<string, unknown>;
  start_date: string;
  end_date: string;
  initial_cash?: number;
  train_window?: number;
  test_window?: number;
  step_size?: number;
  anchored?: boolean;
  include_train?: boolean;
}

export interface WalkForwardWindowResult {
  window_id: number;
  train_start: string;
  train_end: string;
  test_start: string;
  test_end: string;
  metrics: Record<string, number | null>;
}

export interface WalkForwardResponse {
  config: Record<string, unknown>;
  windows: WalkForwardWindowResult[];
  summary_metrics: Record<string, number | null>;
  summary_table: Record<string, unknown>[];
}

// --- Experiments ---
export interface ExperimentSummary {
  run_id: string;
  engine_name: string;
  strategy_name: string;
  created_at: string;
  config_hash: string;
  data_snapshot_id: string;
}

export interface ExperimentCompareResponse {
  assumptions: Record<string, unknown>[];
  metrics: Record<string, unknown>[];
}

export interface SaveExperimentRequest {
  tickers: string[];
  strategy: string;
  strategy_params: Record<string, unknown>;
  start_date?: string;
  end_date?: string;
  initial_cash: number;
  benchmark_ticker?: string;
  risk_free_rate?: number;
  stats: Record<string, unknown>;
}

export interface SaveExperimentResponse {
  run_id: string;
  strategy_name: string;
  created_at: string;
  config_hash: string;
  data_snapshot_id: string;
}

// --- Risk Analytics ---
export interface VaRRequest {
  ticker: string;
  confidence?: number;
  horizon_days?: number;
  portfolio_value?: number | null;
  start_date?: string;
  end_date?: string;
}

export interface VaRResultSchema {
  var_: number | null;
  confidence: number;
  method: string;
  horizon_days: number;
  n_observations: number;
  var_dollars: number | null;
}

export interface CVaRResultSchema {
  cvar: number | null;
  var_: number | null;
  confidence: number;
  method: string;
  n_tail_obs: number;
  n_observations: number;
}

export interface VaRResponse {
  historical: VaRResultSchema;
  parametric: VaRResultSchema;
  montecarlo: VaRResultSchema;
  cvar: CVaRResultSchema;
}

export interface StressTestRequest {
  ticker: string;
  scenarios?: string[];
  initial_value?: number;
  start_date?: string;
  end_date?: string;
}

export interface StressTestResultSchema {
  scenario_name: string;
  initial_value: number;
  trough_value: number;
  trough_return: number | null;
  max_drawdown_pct: number | null;
  shock_duration_days: number;
  recovery_days: number;
  price_path: number[];
}

export interface StressTestResponse {
  results: StressTestResultSchema[];
}

export interface KellyRequest {
  ticker: string;
  start_date?: string;
  end_date?: string;
}

export interface KellyResponse {
  full_kelly: number | null;
  half_kelly: number | null;
  quarter_kelly: number | null;
  win_rate: number | null;
  win_loss_ratio: number | null;
  expected_value: number | null;
  is_positive_ev: boolean;
  n_observations: number;
}

export interface MultiKellyRequest {
  tickers: string[];
  start_date?: string;
  end_date?: string;
}

export interface MultiKellyResponse {
  weights: Record<string, number>;
  full_kelly_weights: Record<string, number>;
  half_kelly_weights: Record<string, number>;
  correlation_matrix: Record<string, Record<string, number>>;
  asset_results: Record<string, KellyResponse>;
  n_assets: number;
  n_observations: number;
}

export interface VaRBacktestRequest {
  ticker: string;
  confidence?: number;
  method?: string;
  start_date?: string;
  end_date?: string;
}

export interface VaRBacktestResponse {
  confidence: number;
  method: string;
  n_observations: number;
  n_violations: number;
  violation_rate: number | null;
  expected_violation_rate: number;
  is_calibrated: boolean;
}

// --- Portfolio Analytics ---
export interface RollingMetricsRequest {
  ticker: string;
  benchmark_ticker?: string;
  window?: number;
  risk_free_rate?: number;
  start_date?: string;
  end_date?: string;
}

export interface RollingMetricsResponse {
  window: number;
  n_obs: number;
  sharpe: (number | null)[];
  volatility: (number | null)[];
  beta: (number | null)[] | null;
  dates: string[];
  mean_sharpe: number | null;
  mean_vol: number | null;
  mean_beta: number | null;
}

export interface BenchmarkRequest {
  portfolio_ticker: string;
  benchmark_ticker: string;
  risk_free_rate?: number;
  start_date?: string;
  end_date?: string;
}

export interface BenchmarkResponse {
  alpha: number | null;
  beta: number | null;
  r_squared: number | null;
  tracking_error: number | null;
  information_ratio: number | null;
  up_capture: number | null;
  down_capture: number | null;
  benchmark_name: string;
  n_observations: number;
}

export interface DrawdownRequest {
  ticker: string;
  top_n?: number;
  start_date?: string;
  end_date?: string;
}

export interface DrawdownPeriodSchema {
  start_idx: number;
  trough_idx: number;
  end_idx: number | null;
  depth: number;
  duration_bars: number;
  recovery_bars: number | null;
}

export interface DrawdownResponse {
  periods: DrawdownPeriodSchema[];
  underwater_curve: (number | null)[];
  n_periods: number;
  max_depth: number | null;
  avg_depth: number | null;
  avg_duration_bars: number | null;
  avg_recovery_bars: number | null;
  current_drawdown: number | null;
  n_observations: number;
}

export interface CorrelationRequest {
  tickers: string[];
  weights?: Record<string, number>;
  start_date?: string;
  end_date?: string;
}

export interface CorrelationResponse {
  n_assets: number;
  weights: Record<string, number>;
  herfindahl_index: number | null;
  effective_n: number | null;
  diversification_ratio: number | null;
  avg_pairwise_correlation: number | null;
  correlation_matrix: Record<string, Record<string, number>>;
  individual_vols: Record<string, number>;
  portfolio_vol: number | null;
  n_observations: number;
}

// --- Real-Time Quotes ---
export interface QuotesRequest {
  symbols: string[];
}

export interface QuoteSchema {
  symbol: string;
  price: number;
  change: number | null;
  change_percent: number | null;
  volume: number | null;
  previous_close: number | null;
  open: number | null;
  high: number | null;
  low: number | null;
  bid: number | null;
  ask: number | null;
  provider: string;
  timestamp: string;
}

export interface QuotesResponse {
  quotes: QuoteSchema[];
  errors: Record<string, string>;
}

export interface ProviderStatusSchema {
  provider: string;
  is_available: boolean;
  last_success: string | null;
  last_error: string | null;
  total_requests: number;
  total_errors: number;
}

export interface ProviderStatusResponse {
  providers: ProviderStatusSchema[];
}

// --- Factor Analytics ---
export interface FactorRegressionRequest {
  ticker: string;
  factor_data: Record<string, number>[];
  factor_names: string[];
  model_type?: string;
  start_date?: string;
  end_date?: string;
}

export interface FactorRegressionResponse {
  loadings: Record<string, number | null>;
  alpha: number | null;
  r_squared: number | null;
  adj_r_squared: number | null;
  residual_std: number | null;
  t_stats: Record<string, number | null>;
  p_values: Record<string, number | null>;
  factor_names: string[];
  model_type: string;
  n_observations: number;
}

export interface FactorAttributionResponse {
  factor_contributions: Record<string, number | null>;
  alpha_contribution: number | null;
  total_return: number | null;
  explained_return: number | null;
  residual_return: number | null;
  factor_names: string[];
  n_observations: number;
}

export interface FactorRiskResponse {
  systematic_variance: number | null;
  idiosyncratic_variance: number | null;
  total_variance: number | null;
  pct_systematic: number | null;
  marginal_contributions: Record<string, number | null>;
  factor_names: string[];
  n_observations: number;
}

export interface RollingRSquaredResponse {
  values: (number | null)[];
  dates: string[];
}

// --- Data Status ---
export interface DataSourceInfo {
  name: string;
  description: string;
  file_count: number;
  is_stale: boolean;
  age_str: string;
  size_str: string;
  oldest_file: string | null;
  newest_file: string | null;
  total_size_bytes: number;
  max_age_days: number;
}

export interface DataStatusResponse {
  sources: DataSourceInfo[];
  total_files: number;
  total_size_bytes: number;
  fresh_count: number;
  stale_count: number;
}
