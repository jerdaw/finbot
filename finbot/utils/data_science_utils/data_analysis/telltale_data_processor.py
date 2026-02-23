"""Compare multiple time series against a reference to analyze tracking accuracy.

Provides utilities for normalizing multiple time series relative to a reference
series and analyzing their tracking error. Particularly useful for comparing
fund performance, index tracking, or simulation accuracy against benchmarks.

Typical usage:
    ```python
    # Compare ETFs against S&P 500 Total Return index
    processor = TelltaleDataProcessor(sp500tr, spy, voo, splg)

    # Get normalized telltale data (all start at 1.0, relative to reference)
    telltale_data = processor.tell_data

    # Analyze tracking accuracy
    analysis = processor.analyze_telltale_data()
    print(analysis)  # Shows MAD, RMSD, max deviation for each series

    # Visualize telltale comparison
    processor.plot_telltale_data()
    ```

What is "telltale data"?
    - Normalizes all series to start at 1.0
    - Each subsequent value shows performance relative to reference
    - Telltale ratio = series / reference (normalized)
    - Value of 1.0 = perfect tracking
    - Value > 1.0 = outperforming reference
    - Value < 1.0 = underperforming reference

How it works:
    1. Normalize reference to start at 1.0: `ref / ref.iloc[0]`
    2. Normalize each comparison series to start at 1.0
    3. Concatenate all series (dropna for common date range)
    4. Divide each series by the normalized reference
    5. Result shows tracking ratio over time

Features:
    - Automatic normalization to common starting point
    - Statistical tracking error analysis (MAD, RMSD, max deviation)
    - Built-in visualization via InteractivePlotter
    - Handles both DataFrames and Series
    - Column naming with "(Reference)" suffix

Use cases:
    - ETF vs index tracking analysis
    - Simulated vs actual fund performance
    - Multiple fund comparison against benchmark
    - Model validation (predicted vs actual)
    - Replication quality assessment

Tracking error metrics:

1. **Mean Absolute Deviation (MAD)**:
   - Average absolute difference from reference
   - Measures typical tracking error magnitude
   - Less sensitive to large deviations than RMSD

2. **Root Mean Squared Deviation (RMSD)**:
   - Square root of mean squared differences
   - Penalizes large deviations more heavily
   - Standard metric for tracking error

3. **Maximum Deviation**:
   - Largest absolute difference observed
   - Shows worst-case tracking error
   - Useful for understanding tail risk

Example interpretation:
    ```python
    processor = TelltaleDataProcessor(sp500tr, spy, voo)
    analysis = processor.analyze_telltale_data()

    # analysis for SPY column:
    # MAD: 0.002 → Average 0.2% tracking error
    # RMSD: 0.003 → RMS tracking error of 0.3%
    # Max Deviation: 0.008 → Worst deviation was 0.8%
    ```

Static methods:
    - norm(prices): Normalize series to start at 1.0
    - cat(*dfs, dropna=True): Concatenate DataFrames with optional dropna

Best practices:
    - Use long time period for reliable statistics
    - Check for column name uniqueness (warning issued if duplicates)
    - Visualize before analyzing (plot_telltale_data)
    - Consider transaction costs in real-world tracking error
    - Compare multiple tracking periods (bull/bear markets)

Limitations:
    - Requires aligned indices (automatic concat handles this)
    - Assumes proportional tracking (multiplicative errors)
    - Does not account for dividends, fees, or slippage separately
    - Single reference comparison (not multi-reference)

Example workflows:
    ```python
    # ETF tracking analysis
    sp500tr = get_history("^SP500TR")["Close"]
    spy = get_history("SPY")["Close"]
    voo = get_history("VOO")["Close"]
    splg = get_history("SPLG")["Close"]

    processor = TelltaleDataProcessor(sp500tr, spy, voo, splg)
    analysis = processor.analyze_telltale_data()
    processor.plot_telltale_data()

    # Identify best tracker
    best_tracker = analysis.loc["Mean Absolute Deviation"].idxmin()
    print(f"Best tracker: {best_tracker}")

    # Simulation validation
    simulated_upro = sim_upro()
    actual_upro = get_history("UPRO")["Close"]

    processor = TelltaleDataProcessor(simulated_upro, actual_upro)
    tracking_stats = processor.analyze_telltale_data()
    # Shows how well simulation matches reality
    ```

Related modules: get_correlation (correlation analysis), rebase_cumu_pct_change
(normalization), plotting_utils (visualization).
"""

import numpy as np
import pandas as pd

from finbot.utils.plotting_utils.interactive.interactive_plotter import InteractivePlotter


class TelltaleDataProcessor:
    def __init__(self, reference: pd.DataFrame | pd.Series, *dfs: pd.DataFrame | pd.Series) -> None:
        self.reference: pd.DataFrame | pd.Series = reference
        self.dfs: tuple[pd.DataFrame | pd.Series, ...] = dfs
        self.tell_data = self.get_telltale_data()

    @staticmethod
    def norm(prices: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
        return prices / prices.iloc[0]

    @staticmethod
    def cat(*dfs: pd.DataFrame | pd.Series, dropna: bool = True) -> pd.DataFrame:
        result = pd.concat(dfs, axis=1)
        if dropna:
            result.dropna(inplace=True)
        return result

    def get_telltale_data(self) -> pd.DataFrame:
        if isinstance(self.reference, pd.DataFrame):
            self.reference.columns = [f"{c} (Reference)" for c in self.reference.columns]
        else:
            self.reference.name = f"{self.reference.name} (Reference)"

        tell = self.norm(self.cat(self.reference, *self.dfs))
        if not isinstance(tell, pd.DataFrame):
            raise TypeError("Expected telltale data normalization output to be a DataFrame")
        # Check for unique column names
        if tell.columns.nunique() < len(tell.columns):
            print("Warning: Column names are not unique.")

        return tell.apply(lambda c: c / tell.iloc[:, 0])

    def analyze_telltale_data(self) -> pd.DataFrame:
        results = pd.DataFrame()
        reference = self.tell_data.iloc[:, 0]

        for column in self.tell_data.columns[1:]:
            serie = self.tell_data[column]
            mad = np.mean(np.abs(reference - serie))
            rmsd = np.sqrt(np.mean((reference - serie) ** 2))
            max_dev = np.max(np.abs(reference - serie))

            results[column] = [mad, rmsd, max_dev]

        results.index = ["Mean Absolute Deviation", "Root Mean Squared Deviation", "Maximum Deviation"]
        return results

    def plot_telltale_data(self, **layout_kws: object) -> None:
        plotter = InteractivePlotter()
        plotter.plot_time_series(self.tell_data)


# Example usage
if __name__ == "__main__":
    # Assuming get_history function as defined before
    from finbot.utils.data_collection_utils.yfinance.get_history import get_history

    sp500tr = get_history("^SP500TR")["Adj Close"]
    sp500tr.name = "SP500TR"
    splg = get_history("SPLG")["Adj Close"]
    splg.name = "SPLG"
    voo = get_history("VOO")["Adj Close"]
    voo.name = "VOO"
    spy = get_history("SPY")["Adj Close"]
    spy.name = "SPY"

    processor = TelltaleDataProcessor(sp500tr, splg, voo, spy)
    analysis_results = processor.analyze_telltale_data()
    print(analysis_results)
    processor.plot_telltale_data()
