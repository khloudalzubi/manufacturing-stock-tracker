"""Twelve Data API boundary with sanitized errors and request helpers."""

import logging

import requests

TWELVE_DATA_QUOTE_URL = "https://api.twelvedata.com/quote"
TWELVE_DATA_TIME_SERIES_URL = "https://api.twelvedata.com/time_series"
LOGGER = logging.getLogger(__name__)


class TwelveDataError(RuntimeError):
    """Raised when Twelve Data returns an unusable response."""


def _get_json(url: str, params: dict, api_key: str) -> dict:
    """Request JSON from Twelve Data and raise sanitized errors on failure."""
    safe_params = {key: value for key, value in params.items() if key != "apikey"}
    LOGGER.debug("Twelve Data request parameters without API key: %s", safe_params)

    try:
        response = requests.get(url, params=params, timeout=20)
    except requests.RequestException as exc:
        raise TwelveDataError(
            f"Twelve Data request failed before receiving a response: {type(exc).__name__}"
        ) from exc

    if response.status_code >= 400:
        raise TwelveDataError(
            f"Twelve Data request failed with HTTP {response.status_code} {response.reason}."
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise TwelveDataError("Twelve Data response was not valid JSON.") from exc

    if isinstance(payload, dict) and payload.get("status") == "error":
        raise TwelveDataError(str(payload.get("message", "Twelve Data returned an error.")))
    if not isinstance(payload, dict):
        raise TwelveDataError("Twelve Data response should be a JSON object.")
    if not payload:
        raise TwelveDataError("Twelve Data returned no data for the requested symbols.")

    return payload


def fetch_quotes(symbols: list[str], api_key: str) -> dict:
    """Fetch current quote data for one or more ticker symbols."""
    if not api_key.strip():
        raise TwelveDataError("TWELVE_DATA_API_KEY is required.")
    if not symbols:
        raise TwelveDataError("At least one ticker symbol is required.")

    params = {
        "symbol": ",".join(symbols),
        "apikey": api_key,
    }
    LOGGER.info("Requesting Twelve Data quotes for %s", params["symbol"])
    return _get_json(TWELVE_DATA_QUOTE_URL, params, api_key)


def fetch_time_series(
    symbols: list[str],
    api_key: str,
    interval: str = "1day",
    outputsize: int = 30,
) -> dict:
    """Fetch historical time-series data for one or more ticker symbols."""
    if not api_key.strip():
        raise TwelveDataError("TWELVE_DATA_API_KEY is required.")
    if not symbols:
        raise TwelveDataError("At least one ticker symbol is required.")
    if outputsize < 2:
        raise TwelveDataError("Historical outputsize must be at least 2.")

    params = {
        "symbol": ",".join(symbols),
        "interval": interval,
        "outputsize": outputsize,
        "apikey": api_key,
    }
    LOGGER.info("Requesting Twelve Data time series for %s", params["symbol"])
    return _get_json(TWELVE_DATA_TIME_SERIES_URL, params, api_key)
