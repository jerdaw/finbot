from pathlib import Path
from typing import Any

import pandas as pd


class CollectionTrackerBase:
    """Base class for CSV-backed collection trackers.

    Provides CRUD operations (add, update, delete) and query helpers
    for tracked-symbol manifests stored as CSV files.

    Args:
        csv_path: Path to the CSV manifest file.
    """

    def __init__(self, csv_path: Path) -> None:
        """Initialise the tracker and load the CSV from disk.

        Args:
            csv_path: Path to the CSV manifest file.
        """
        self.csv_path = Path(csv_path)
        self.df = self.load_csv()

    def load_csv(self) -> pd.DataFrame:
        """Load the CSV manifest from disk, normalising sentinel strings.

        Converts ``"None"``, ``"nan"``, ``"True"``, and ``"False"`` strings
        to their Python equivalents. Returns an empty DataFrame if the file
        does not exist.

        Returns:
            DataFrame sorted by the ``symbol`` column.
        """

        # Function to convert "None" strings to None
        def convert_none(value: object) -> object:
            value = str(value)
            return {
                "None": None,
                "nan": None,
                "True": True,
                "False": False,
            }.get(value, value)

        try:
            # Apply the converter to all columns
            converters = dict.fromkeys(pd.read_csv(self.csv_path, nrows=0).columns, convert_none)
            df = pd.read_csv(self.csv_path, converters=converters)
            df = df.sort_values(by="symbol")
            df = df.reset_index(drop=True)
            return df
        except FileNotFoundError:
            return pd.DataFrame()

    def save_csv(self) -> None:
        """Save the DataFrame to the CSV file."""
        self.df = self.df.sort_values(by="symbol")
        self.df = self.df.reset_index(drop=True)
        self.df.to_csv(self.csv_path, index=False)

    def add_entries(self, entry_data: Any | list[Any]) -> None:
        """Add one or more entries to the tracker, raising on conflicting duplicates.

        Args:
            entry_data: A single entry dataclass or a list of them. Each must
                expose a ``symbol`` attribute and a ``to_dict()`` method.

        Raises:
            ValueError: If a symbol already exists with different field values.
        """
        entry_data_list = [entry_data] if not isinstance(entry_data, list) else entry_data
        for entry_data in entry_data_list:
            # Check if the symbol already exists in the DataFrame
            if not self.df.empty and entry_data.symbol in self.df["symbol"].values:
                # Retrieve the existing row for the symbol
                existing_row = self.df[self.df["symbol"] == entry_data.symbol]

                # Compare the data; raise error only if they differ
                existing_data_dict = existing_row.to_dict(orient="records")[0]
                new_data_dict = entry_data.to_dict()
                for key in existing_data_dict:
                    print(new_data_dict)
                    new_val = new_data_dict[key]
                    old_val = existing_data_dict[key]
                    # If one value is nan and the other is None, they are considered equal
                    if (pd.isna(new_val) and old_val is None) or (pd.isna(old_val) and new_val is None):
                        continue

                    # Compare the values
                    if new_val != old_val:
                        print(key)
                        print(existing_data_dict[key], new_data_dict[key])
                        raise ValueError(
                            f"Data for symbol {entry_data.symbol} already exists and differs from new data.",
                        )

                # If the data is the same, no action is needed
                continue

            # If the symbol does not exist, add the new data
            new_row = pd.DataFrame([entry_data.to_dict()])
            self.df = pd.concat([self.df, new_row], ignore_index=True)
            self.save_csv()

    def update_entry(self, symbol: str, updated_data: Any) -> None:
        """Replace an existing entry with updated data.

        Args:
            symbol: Symbol identifier to replace.
            updated_data: New entry dataclass with a ``to_dict()`` method.

        Raises:
            ValueError: If the symbol does not exist in the tracker.
        """
        if not self.df.empty and symbol.upper() not in self.df["symbol"].values:
            raise ValueError(f"Symbol {symbol} does not exist.")
        self.df = self.df[self.df["symbol"] != symbol]
        new_row = pd.DataFrame([updated_data.to_dict()])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.save_csv()

    def delete_entry(self, symbol: str | list[str]) -> None:
        """Delete one or more entries from the tracker by symbol.

        Args:
            symbol: A single symbol string or a list of symbol strings.
        """
        symbols = [symbol] if isinstance(symbol, str) else symbol
        for symbol in symbols:
            self.df = self.df[self.df["symbol"] != symbol]
            self.save_csv()

    def get_symbols(self, symbol: str | list[str]) -> pd.Series | pd.DataFrame:
        """Return rows matching the given symbol(s).

        Args:
            symbol: A single symbol string or a list of symbol strings.

        Returns:
            DataFrame of matching rows.

        Raises:
            ValueError: If none of the requested symbols are found.
        """
        symbols = [symbol] if isinstance(symbol, str) else symbol
        matching = self.df[self.df["symbol"].isin(symbols)]
        if matching.empty:
            raise ValueError(f"Symbol(s) {symbol} do not exist.")
        return matching

    def get_sorted(self, columns: str | list[str], ascending: bool = True) -> pd.DataFrame:
        """Return the DataFrame sorted by the specified column(s).

        Args:
            columns: Column name or list of column names to sort by.
            ascending: Sort direction; ``True`` for ascending (default).

        Returns:
            Sorted copy of the DataFrame.
        """
        if isinstance(columns, str):
            columns = [columns]
        return self.df.sort_values(by=columns, ascending=ascending)

    def get_all_symbols(self) -> list[str]:
        """Return a sorted list of all tracked symbol strings.

        Returns:
            Alphabetically sorted list of symbols.
        """
        return sorted(self.df["symbol"].tolist())

    def to_dict(self) -> dict:
        """Return the tracker data as a plain dictionary keyed by row index.

        Returns:
            Dict mapping integer row indices to row records.
        """
        return dict(self.df.iterrows())

    def to_df(self) -> pd.DataFrame:
        """Return a copy of the underlying DataFrame.

        Returns:
            Shallow copy of the internal DataFrame.
        """
        return self.df.copy()
