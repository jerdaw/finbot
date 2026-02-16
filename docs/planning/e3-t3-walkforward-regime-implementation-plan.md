# E3-T3: Walk-Forward and Regime Evaluation Implementation Plan

**Created:** 2026-02-16
**Epic:** E3 - Backtesting Fidelity Improvements
**Task:** E3-T3
**Estimated Effort:** M (3-5 days)

## Overview

Add walk-forward testing and regime-based evaluation capabilities to enhance backtest validation and understand strategy performance across different market conditions.

## Goals

1. **Walk-Forward Testing**: Prevent overfitting by validating strategies across rolling windows
2. **Regime Evaluation**: Understand performance in bull/bear/sideways markets
3. **API Design**: Clean, composable API that works with existing adapter pattern
4. **Documentation**: Clear examples and use cases

## Non-Goals

- Full parameter optimization framework (future work)
- Machine learning-based regime detection (use simple heuristics)
- Real-time regime classification (offline analysis only)

## Architecture

### Walk-Forward Testing

**Components:**
1. `WalkForwardConfig` - Configuration for window sizes, anchoring
2. `WalkForwardResult` - Results from walk-forward analysis
3. `run_walk_forward()` - Main orchestration function
4. Helper utilities for window generation

**Design Decisions:**
- Support both expanding and rolling windows
- Allow optional optimization phase (for future)
- Return structured results with per-window metrics
- Reuse existing BacktestEngine interface

### Regime Evaluation

**Components:**
1. `MarketRegime` enum - BULL, BEAR, SIDEWAYS, VOLATILE
2. `RegimeDetector` protocol - Interface for regime detection
3. `SimpleRegimeDetector` - Returns-based regime classification
4. `segment_by_regime()` - Split backtest results by regime
5. `RegimeMetrics` - Per-regime performance breakdown

**Design Decisions:**
- Simple threshold-based detection (not ML)
- Use market returns as primary signal
- Allow user-defined thresholds
- Compute same metrics per regime as overall

## Implementation Steps

### Step 1: Walk-Forward Core (2-3 hours)

**Files to create:**
- `finbot/core/contracts/walkforward.py` - Models and protocols
- `finbot/services/backtesting/walkforward.py` - Implementation

**Models:**
```python
@dataclass(frozen=True)
class WalkForwardConfig:
    train_window: int  # Trading days
    test_window: int  # Trading days
    step_size: int  # Trading days to move forward
    anchored: bool = False  # Expanding vs rolling window

@dataclass(frozen=True)
class WalkForwardWindow:
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp
    window_id: int

@dataclass(frozen=True)
class WalkForwardResult:
    config: WalkForwardConfig
    windows: tuple[WalkForwardWindow, ...]
    train_results: tuple[BacktestRunResult, ...]
    test_results: tuple[BacktestRunResult, ...]
    summary_metrics: dict[str, float]
```

**Functions:**
```python
def generate_windows(
    start: pd.Timestamp,
    end: pd.Timestamp,
    config: WalkForwardConfig,
) -> list[WalkForwardWindow]:
    """Generate walk-forward windows."""

def run_walk_forward(
    engine: BacktestEngine,
    request: BacktestRunRequest,
    config: WalkForwardConfig,
) -> WalkForwardResult:
    """Run walk-forward analysis."""
```

### Step 2: Regime Detection (2-3 hours)

**Files to create:**
- `finbot/core/contracts/regime.py` - Models and protocols
- `finbot/services/backtesting/regime.py` - Implementation

**Models:**
```python
class MarketRegime(StrEnum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"

@dataclass(frozen=True)
class RegimeConfig:
    bull_threshold: float = 0.15  # 15% annual return
    bear_threshold: float = -0.10  # -10% annual return
    volatility_threshold: float = 0.25  # 25% annual vol
    lookback_days: int = 252  # 1 year

@dataclass(frozen=True)
class RegimePeriod:
    regime: MarketRegime
    start: pd.Timestamp
    end: pd.Timestamp
    market_return: float
    market_volatility: float

@dataclass(frozen=True)
class RegimeMetrics:
    regime: MarketRegime
    count_periods: int
    total_days: int
    metrics: dict[str, float]  # Same as BacktestRunResult.metrics
```

**Protocol:**
```python
class RegimeDetector(Protocol):
    def detect(
        self,
        market_data: pd.DataFrame,
        config: RegimeConfig,
    ) -> list[RegimePeriod]:
        """Detect market regimes."""
```

**Implementation:**
```python
class SimpleRegimeDetector:
    """Returns-based regime detection."""

    def detect(
        self,
        market_data: pd.DataFrame,
        config: RegimeConfig,
    ) -> list[RegimePeriod]:
        # Calculate rolling returns and volatility
        # Classify each period
        # Return regime periods
```

**Functions:**
```python
def segment_by_regime(
    result: BacktestRunResult,
    market_data: pd.DataFrame,
    detector: RegimeDetector | None = None,
    config: RegimeConfig | None = None,
) -> dict[MarketRegime, RegimeMetrics]:
    """Segment backtest results by market regime."""
```

### Step 3: Tests (2-3 hours)

**Files to create:**
- `tests/unit/test_walkforward.py`
- `tests/unit/test_regime.py`

**Test coverage:**
- Window generation (rolling, anchored, edge cases)
- Walk-forward execution (simple strategy)
- Regime detection (bull, bear, sideways classification)
- Regime segmentation (metrics per regime)
- Integration with BacktraderAdapter

### Step 4: Examples and Documentation (2-3 hours)

**Files to create:**
- `notebooks/walkforward_testing_demo.ipynb`
- `notebooks/regime_analysis_demo.ipynb`
- `docs/user-guides/advanced-backtesting.md`

**Content:**
- Walk-forward methodology explanation
- Regime analysis methodology
- Practical examples
- Interpretation guidance
- Limitations and caveats

### Step 5: Integration and Polish (1-2 hours)

- Update contracts `__init__.py` exports
- Update roadmap and backlog
- Run full test suite
- Ensure parity maintained

## Acceptance Criteria

- [ ] Walk-forward helper API added and tested
- [ ] Regime segmentation functionality added and tested
- [ ] Examples demonstrating both features
- [ ] Documentation explaining methodology
- [ ] All existing tests still pass (467+)
- [ ] Parity maintained (100% on all golden strategies)

## Design Considerations

### Walk-Forward

**Why useful:**
- Validates strategy isn't overfit to specific period
- More realistic performance expectations
- Industry standard validation technique

**Limitations:**
- Computationally expensive (multiple backtests)
- Not included in this phase: parameter optimization
- Results can vary significantly by window choice

### Regime Detection

**Why simple heuristics:**
- Interpretable and transparent
- No ML dependencies
- Sufficient for initial analysis
- Users can implement custom detectors via protocol

**Limitations:**
- Backward-looking only (no real-time)
- Threshold-based (subjective)
- Doesn't capture all market nuances

## Future Enhancements (Out of Scope)

- Parameter optimization in walk-forward
- ML-based regime detection
- Volatility regimes (VIX-based)
- Correlation regimes
- Economic cycle regimes
- Custom regime definitions
- Real-time regime classification

## References

- Pardo, R. (2008). *The Evaluation and Optimization of Trading Strategies*. Wiley.
- De Prado, M. L. (2018). *Advances in Financial Machine Learning*. Wiley.
