import numpy as np
import pandas as pd

from finbot.utils.plotting_utils.interactive.interactive_plotter import InteractivePlotter


class TelltaleDataProcessor:
    def __init__(self, reference, *dfs):
        self.reference = reference
        self.dfs = dfs
        self.tell_data = self.get_telltale_data()

    @staticmethod
    def norm(prices):
        return prices / prices.iloc[0]

    @staticmethod
    def cat(*dfs, dropna=True):
        result = pd.concat(dfs, axis=1)
        if dropna:
            result.dropna(inplace=True)
        return result

    def get_telltale_data(self):
        if isinstance(self.reference, pd.DataFrame):
            self.reference.columns = [f"{c} (Reference)" for c in self.reference.columns]
        else:
            self.reference.name = f"{self.reference.name} (Reference)"

        tell = self.norm(self.cat(self.reference, *self.dfs))
        # Check for unique column names
        if tell.columns.nunique() < len(tell.columns):
            print("Warning: Column names are not unique.")

        return tell.apply(lambda c: c / tell.iloc[:, 0])

    def analyze_telltale_data(self):
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

    def plot_telltale_data(self, **layout_kws):
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
