"""
API Constants

This module defines constants related to the application's interaction with external APIs,
such as API keys (loaded from environment variables), base URLs, headers, and function
names for endpoints.

Attributes:
    ALPHA_VANTAGE_RAPI_BASE_URL (str): Base URL for the AlphaVantage RapidAPI endpoint.
    ALPHA_VANTAGE_RAPI_HEADERS (dict): Headers to use for AlphaVantage RapidAPI requests.
    ALPHA_VANTAGE_RAPI_FUNCTIONS (set): Function names for the AlphaVantage RapidAPI endpoint.
    ALPHA_VANTAGE_API_BASE_URL (str): Base URL for the AlphaVantage API.
    ALPHA_VANTAGE_API_FUNCTIONS (set): Function names for the AlphaVantage API.
"""
from __future__ import annotations

from config import Config

# AlphaVantage RapidAPI constants
ALPHA_VANTAGE_RAPI_BASE_URL = "https://alpha-vantage.p.rapidapi.com/query"
ALPHA_VANTAGE_RAPI_HEADERS = {
    "X-RapidAPI-Key": Config.alpha_vantage_api_key,
    "X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com",
}
ALPHA_VANTAGE_RAPI_FUNCTIONS = {
    "TIME_SERIES_INTRADAY",
    "TIME_SERIES_DAILY_ADJUSTED",
    "TIME_SERIES_DAILY",
    "TIME_SERIES_WEEKLY_ADJUSTED",
    "TIME_SERIES_WEEKLY",
    "TIME_SERIES_MONTHLY_ADJUSTED",
    "TIME_SERIES_MONTHLY",
    "GLOBAL_QUOTE",
    "SYMBOL_SEARCH",
    "FX_MONTHLY",
    "FX_WEEKLY",
    "FX_DAILY",
    "FX_INTRADAY",
    "CURRENCY_EXCHANGE_RATE",
    "DIGITAL_CURRENCY_MONTHLY",
    "DIGITAL_CURRENCY_WEEKLY",
    "DIGITAL_CURRENCY_DAILY",
    "SMA",
    "EMA",
    "WMA",
    "DEMA",
    "TEMA",
    "TRIMA",
    "KAMA",
    "MAMA",
    "VWAP Premium",
    "T3",
    "MACD Premium",
    "MACDEXT",
    "STOCH",
    "STOCHF",
    "RSI",
    "STOCHRSI",
    "WILLR",
    "ADX",
    "ADXR",
    "APO",
    "PPO",
    "MOM",
    "BOP",
    "CCI",
    "CMO",
    "ROC",
    "ROCR",
    "AROON",
    "AROONOSC",
    "MFI",
    "TRIX",
    "ULTOSC",
    "DX",
    "MINUS_DI",
    "PLUS_DI",
    "MINUS_DM",
    "PLUS_DM",
    "BBANDS",
    "MIDPOINT",
    "MIDPRICE",
    "SAR",
    "TRANGE",
    "ATR",
    "NATR",
    "AD",
    "ADOSC",
    "OBV",
    "HT_TRENDLINE",
    "HT_SINE",
    "HT_TRENDMODE",
    "HT_DCPERIOD",
    "HT_DCPHASE",
    "HT_PHASOR",
}

# AlphaVantage API constants
ALPHA_VANTAGE_API_BASE_URL = "https://www.alphavantage.co/query"
ALPHA_VANTAGE_API_FUNCTIONS = {
    "NEWS_SENTIMENT",
    "REAL_GDP",
    "REAL_GDP_PER_CAPITA",
    "TREASURY_YIELD",
    "FEDERAL_FUNDS_RATE",
    "CPI",
    "INFLATION",
    "RETAIL_SALES",
    "DURABLES",
    "UNEMPLOYMENT",
    "NONFARM_PAYROLL",
}
