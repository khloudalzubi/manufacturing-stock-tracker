import requests

ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"


class AlphaVantageError(RuntimeError):
    """Raised when Alpha Vantage returns an unusable response."""


def fetch_daily_prices(symbol: str, api_key: str) -> dict:
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol.upper(),
        "outputsize": "compact",
        "apikey": api_key,
    }
    response = requests.get(ALPHA_VANTAGE_URL, params=params, timeout=20)
    response.raise_for_status()
    payload = response.json()

    if "Error Message" in payload:
        raise AlphaVantageError(payload["Error Message"])
    if "Note" in payload:
        raise AlphaVantageError(payload["Note"])
    if "Information" in payload:
        raise AlphaVantageError(payload["Information"])
    if "Time Series (Daily)" not in payload:
        raise AlphaVantageError("Alpha Vantage response did not include daily time series data.")

    return payload
