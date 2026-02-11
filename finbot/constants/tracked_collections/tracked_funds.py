import datetime
import decimal
import re
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from finbot.constants.path_constants import TRACKED_COLLECTIONS_DIR
from finbot.constants.tracked_collections._utils import CollectionTrackerBase


# Helper function for regular expression validation
def _validate_with_regex(value: str, pattern: str, error_message: str) -> None:
    if not re.match(pattern, value):
        raise ValueError(error_message)


@dataclass
class FundData:
    """Dataclass for storing fund information."""

    symbol: str
    name: str
    asset_region: str
    category: str
    sector: str
    issuer: str
    issuer_region: str
    inception_date: str
    mer: str
    leverage_multiple: float
    leverage_reset_period: str
    underlying_index: str
    url: str

    TRACKED_ATTRS: dict[str, type] = field(
        default_factory=lambda: {
            "symbol": str,
            "name": str,
            "asset_region": str,
            "category": str,
            "sector": str,
            "issuer": str,
            "issuer_region": str,
            "inception_date": str,
            "mer": str,
            "leverage_multiple": str,
            "leverage_reset_period": str,
            "underlying_index": str,
            "url": str,
        },
    )

    def __post_init__(self):
        if not hasattr(self, "TRACKED_ATTRS"):
            raise AttributeError("TRACKED_ATTRS must be defined.")

        for attr in self.TRACKED_ATTRS:
            val = getattr(self, attr)
            if isinstance(val, str):
                setattr(self, attr, val.lower().strip())

        self.validate_fund_data()

    def validate_fund_data(self):
        for expected_attr, expected_type in self.TRACKED_ATTRS.items():
            actual_attr = getattr(self, expected_attr)
            if not actual_attr and not (
                expected_attr in ("leverage_reset_period", "underlying_index") and actual_attr == ""
            ):
                raise ValueError(f"Field cannot be empty: {expected_attr} -> {actual_attr}")
            if not isinstance(actual_attr, expected_type):
                raise TypeError(
                    f"Field must be of type {expected_type}: {expected_attr} but received {type(actual_attr)}: {actual_attr}",
                )

        _validate_with_regex(
            self.symbol,
            r"^[a-z0-9.]+$",
            f"Symbol ({self.symbol}) must contain only lowercase letters, numbers, or '.'",
        )

        _validate_with_regex(self.mer, r"^\d+\.\d+%$", f"MER ({self.mer}) must end with % and include a decimal.")

        mer_value = decimal.Decimal(self.mer.rstrip("%"))
        if mer_value > decimal.Decimal("3.00"):
            warnings.warn(f"The MER {mer_value}% is greater than 3.00%.", UserWarning, stacklevel=2)

        try:
            datetime.datetime.strptime(self.inception_date, "%Y-%m-%d")
        except ValueError as err:
            raise ValueError(f"inception_date ({self.inception_date}) must be in YYYY-MM-DD format.") from err

    def to_dict(self) -> dict:
        """Convert FundData instance to a dictionary."""
        return {attr: getattr(self, attr) for attr in self.TRACKED_ATTRS}

    def to_df(self) -> pd.DataFrame:
        """Convert FundData instance to a DataFrame."""
        return pd.DataFrame.from_dict(self.to_dict(), orient="index").T

    @staticmethod
    def _convert_percentage_to_decimal(percentage: str) -> decimal.Decimal:
        """Convert a percentage string to a decimal."""
        if percentage.endswith("%"):
            return decimal.Decimal(percentage.rstrip("%")) / decimal.Decimal(100)
        raise ValueError(f"Percentage ({percentage}) must end with %.")

    def get_mer_as_decimal(self) -> decimal.Decimal:
        """Get the MER as a decimal."""
        return self._convert_percentage_to_decimal(self.mer)

    def get_leverage_multiple_as_decimal(self) -> decimal.Decimal:
        """Get the leverage multiple as a decimal."""
        return decimal.Decimal(self.leverage_multiple)

    def get_inception_as_date(self) -> datetime.date:
        """Get the inception date as a datetime.date object."""
        return datetime.datetime.strptime(self.inception_date, "%Y-%m-%d").date()


class FundTracker(CollectionTrackerBase):
    def __init__(self, csv_path: Path = TRACKED_COLLECTIONS_DIR / "tracked_funds.csv") -> None:
        super().__init__(Path(csv_path))

    def get_leverage_range(self, min_leverage: float, max_leverage: float) -> pd.DataFrame:
        return self.df[
            (self.df["leverage_multiple"].astype(float) >= min_leverage)
            & (self.df["leverage_multiple"].astype(float) <= max_leverage)
        ]

    def get_unlevered(self) -> pd.DataFrame:
        return self.get_leverage_range(1, 1)

    def get_levered(self) -> pd.DataFrame:
        unlevered = self.get_unlevered()
        return self.df[~self.df["symbol"].isin(unlevered["symbol"])]

    def get_levered_with_reset_period(self, reset_period: str) -> pd.DataFrame:
        levered = self.get_levered()
        return levered[levered["leverage_reset_period"] == reset_period]

    def get_mer_range(self, min_mer: float, max_mer: float) -> pd.DataFrame:
        return self.df[(self.df["mer"].astype(float) >= min_mer) & (self.df["mer"].astype(float) <= max_mer)]

    def get_inception_date_range(self, min_date: datetime.date, max_date: datetime.date) -> pd.DataFrame:
        return self.df[
            (self.df["inception_date"] >= min_date.strftime("%Y-%m-%d"))
            & (self.df["inception_date"] <= max_date.strftime("%Y-%m-%d"))
        ]

    def get_inception_date_before_or_on(self, target_date: datetime.date) -> pd.DataFrame:
        return self.get_inception_date_range(datetime.date.min, target_date)

    def get_matching_indeces(self, index: str | list[str]) -> pd.DataFrame:
        indices = [index] if isinstance(index, str) else index
        return self.df[self.df["underlying_index"].isin(indices)]

    def get_asset_regions(self, asset_region: str | list[str]) -> pd.DataFrame:
        asset_regions = [asset_region] if isinstance(asset_region, str) else asset_region
        return self.df[self.df["asset_region"].isin(asset_regions)]

    def get_categories(self, category: str | list[str]) -> pd.DataFrame:
        categories = [category] if isinstance(category, str) else category
        return self.df[self.df["category"].isin(categories)]

    def get_sectors(self, sector: str | list[str]) -> pd.DataFrame:
        sector = [sector] if isinstance(sector, str) else sector
        return self.df[self.df["sector"].isin(sector)]

    def get_issuers(self, issuer: str | list[str]) -> pd.DataFrame:
        issuers = [issuer] if isinstance(issuer, str) else issuer
        return self.df[self.df["issuer"].isin(issuers)]

    def validate_entries(self, symbols: str | list[str] | None = None) -> None:
        if symbols is None:
            symbols = self.get_all_symbols()
        symbols = [symbols] if isinstance(symbols, str) else symbols

        entries = self.get_symbols(symbols)
        for symbol in symbols:
            cur_data = entries[entries["symbol"] == symbol]
            sym = cur_data["symbol"].values[0]
            name = cur_data["name"].values[0]
            asset_region = cur_data["asset_region"].values[0]
            category = cur_data["category"].values[0]
            sector = cur_data["sector"].values[0]
            issuer = cur_data["issuer"].values[0]
            issuer_region = cur_data["issuer_region"].values[0]
            inception_date = cur_data["inception_date"].values[0]
            mer = cur_data["mer"].values[0]
            leverage_multiple = cur_data["leverage_multiple"].values[0]
            leverage_reset_period = cur_data["leverage_reset_period"].values[0]
            underlying_index = cur_data["underlying_index"].values[0]
            url = cur_data["url"].values[0]

            fund_datum = FundData(
                symbol=sym,
                name=name,
                asset_region=asset_region,
                category=category,
                sector=sector,
                issuer=issuer,
                issuer_region=issuer_region,
                inception_date=inception_date,
                mer=mer,
                leverage_multiple=leverage_multiple,
                leverage_reset_period=leverage_reset_period,
                underlying_index=underlying_index,
                url=url,
            )
            fund_datum.validate_fund_data()


TrackedFunds = FundTracker()

# Main execution
if __name__ == "__main__":
    TrackedFunds.validate_entries()
    fund_df = TrackedFunds.to_df()
    fund_df.info()
    print(fund_df)
