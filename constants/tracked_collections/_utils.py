from pathlib import Path
from typing import Any

import pandas as pd


class CollectionTrackerBase:
    def __init__(self, csv_path: Path) -> None:
        self.csv_path = Path(csv_path)
        self.df = self.load_csv()

    def load_csv(self) -> pd.DataFrame:
        # Function to convert "None" strings to None
        def convert_none(value):
            value = str(value)
            return {
                "None": None,
                "nan": None,
                "True": True,
                "False": False,
            }.get(value, value)

        try:
            # Apply the converter to all columns
            converters = {col: convert_none for col in pd.read_csv(self.csv_path, nrows=0).columns}
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
                    if pd.isna(new_val) and old_val is None or pd.isna(old_val) and new_val is None:
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
        if not self.df.empty and symbol.upper() not in self.df["symbol"].values:
            raise ValueError(f"Symbol {symbol} does not exist.")
        self.df = self.df[self.df["symbol"] != symbol]
        new_row = pd.DataFrame([updated_data.to_dict()])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.save_csv()

    def delete_entry(self, symbol: str | list[str]) -> None:
        symbols = [symbol] if isinstance(symbol, str) else symbol
        for symbol in symbols:
            self.df = self.df[self.df["symbol"] != symbol]
            self.save_csv()

    def get_symbols(self, symbol: str | list[str]) -> pd.Series | pd.DataFrame:
        symbols = [symbol] if isinstance(symbol, str) else symbol
        matching = self.df[self.df["symbol"].isin(symbols)]
        if matching.empty:
            raise ValueError(f"Symbol(s) {symbol} do not exist.")
        return matching

    def get_sorted(self, columns: str | list[str], ascending: bool = True) -> pd.DataFrame:
        if isinstance(columns, str):
            columns = [columns]
        return self.df.sort_values(by=columns, ascending=ascending)

    def get_all_symbols(self) -> list[str]:
        return sorted(self.df["symbol"].tolist())

    def to_dict(self) -> dict:
        return {index: row for index, row in self.df.iterrows()}

    def to_df(self) -> pd.DataFrame:
        return self.df.copy()
