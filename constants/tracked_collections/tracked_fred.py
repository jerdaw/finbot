import datetime
import re
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from constants.path_constants import TRACKED_COLLECTIONS_DIR
from constants.tracked_collections._utils import CollectionTrackerBase


# Helper function for regular expression validation
def _validate_with_regex(value: str, pattern: str, error_message: str) -> None:
    if not re.match(pattern, value):
        raise ValueError(error_message)


@dataclass
class FredData:
    """Dataclass for storing FRED information."""

    symbol: str
    name: str
    category: str
    frequency: str
    seasonally_adjusted: bool
    start_date: str
    units: str

    # Constants
    VALID_FREQUENCIES: set[str] = field(default_factory=lambda: {"daily", "weekly", "monthly", "quarterly", "annual"})
    VALID_CATEGORIES: set[str] = field(
        default_factory=lambda: {
            "Business",
            "Volatility Indexes",
            "Income",
            "Stocks",
            "Spending",
            "GDP",
            "Currency",
            "Money Supply",
            "Real Estate",
            "Employment",
            "Financial Indicators",
            "Debt",
            "Interest Rates",
            "Inflation",
        },
    )
    TRACKED_ATTRS: dict[str, type] = field(
        default_factory=lambda: {
            "symbol": str,
            "name": str,
            "category": str,
            "frequency": str,
            "seasonally_adjusted": bool,
            "start_date": str,
            "units": str,
        },
    )

    def __post_init__(self):
        if not hasattr(self, "TRACKED_ATTRS"):
            raise AttributeError("TRACKED_ATTRS must be defined.")

        for attr in self.TRACKED_ATTRS:
            val = getattr(self, attr)
            if isinstance(val, str):
                setattr(self, attr, val.strip())
            self.symbol = self.symbol.upper()

        self.validate_fred_data()

    def validate_fred_data(self):
        for attr, attr_type in self.TRACKED_ATTRS.items():
            val = getattr(self, attr)
            if not val and (attr != "seasonally_adjusted" and not isinstance(val, bool)):
                raise ValueError(f"Field cannot be empty: {attr} -> {val}")
            if not isinstance(val, attr_type):
                raise TypeError(f"Field must be of type {attr_type}: {attr} -> {val}")

        _validate_with_regex(
            self.symbol,
            r"^[A-Z0-9]+$",
            f"Symbol ({self.symbol}) must contain only uppercase letters or numbers",
        )

        if self.frequency not in self.VALID_FREQUENCIES:
            raise ValueError(f"Frequency {self.frequency} must be one of {self.VALID_FREQUENCIES}.")

        if self.category not in self.VALID_CATEGORIES:
            raise ValueError(f"Category {self.category} must be one of {self.VALID_CATEGORIES}.")

    def to_dict(self) -> dict:
        """Convert FundData instance to a dictionary."""
        return {attr: getattr(self, attr) for attr in self.TRACKED_ATTRS}

    def to_df(self) -> pd.DataFrame:
        """Convert FundData instance to a DataFrame."""
        return pd.DataFrame.from_dict(self.to_dict(), orient="index").T

    def get_start_as_date(self) -> datetime.date:
        """Get the start date as a datetime.date object."""
        return datetime.datetime.strptime(self.start_date, "%Y-%m-%d").date()


class FredTracker(CollectionTrackerBase):
    def __init__(self, csv_path: Path = TRACKED_COLLECTIONS_DIR / "tracked_fred.csv") -> None:
        super().__init__(Path(csv_path))

    def get_start_date_range(self, min_date: datetime.date, max_date: datetime.date) -> pd.DataFrame:
        return self.df[
            (self.df["start_date"] >= min_date.strftime("%Y-%m-%d"))
            & (self.df["start_date"] <= max_date.strftime("%Y-%m-%d"))
        ]

    def get_start_date_before_or_on(self, target_date: datetime.date) -> pd.DataFrame:
        return self.get_start_date_range(datetime.date.min, target_date)

    def get_categories(self, category: str | list[str]) -> pd.DataFrame:
        categories = [category] if isinstance(category, str) else category
        return self.df[self.df["category"].isin(categories)]

    def get_frequencies(self, frequency: str | list[str]) -> pd.DataFrame:
        frequencies = [frequency] if isinstance(frequency, str) else frequency
        return self.df[self.df["frequency"].isin(frequencies)]

    def get_seasonally_adjusted(self, seasonally_adjusted: bool | list[bool]) -> pd.DataFrame:
        seasonally_adjusted = [seasonally_adjusted] if isinstance(seasonally_adjusted, bool) else seasonally_adjusted
        return self.df[self.df["seasonally_adjusted"].isin(seasonally_adjusted)]


TrackedFred = FredTracker()

# Main execution
if __name__ == "__main__":
    fred_df = TrackedFred.to_df()
    fred_df.info()
    print(fred_df)
