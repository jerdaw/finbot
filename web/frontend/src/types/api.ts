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
}

export interface TradeRecord {
  date: string;
  ticker: string;
  action: string;
  size: number;
  price: number;
  value: number;
}

export interface BacktestResponse {
  stats: Record<string, unknown>;
  value_history: Record<string, unknown>[];
  trades: TradeRecord[];
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
}

export interface ExperimentCompareResponse {
  assumptions: Record<string, unknown>[];
  metrics: Record<string, unknown>[];
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
