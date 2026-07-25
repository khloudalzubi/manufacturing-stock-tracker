import logging

import requests

TWELVE_DATA_QUOTE_URL = "https://api.twelvedata.com/quote"
LOGGER = logging.getLogger(__name__)


class TwelveDataError(RuntimeError):
    """Raised when Twelve Data returns an unusable response."""


def fetch_quotes(symbols: list[str], api_key: str) -> dict:
    if not api_key.strip():
        raise TwelveDataError("TWELVE_DATA_API_KEY is required.")
    if not symbols:
        raise TwelveDataError("At least one ticker symbol is required.")

    params = {
        "symbol": ",".join(symbols),
        "apikey": api_key,
    }
    safe_params = {key: value for key, value in params.items() if key != "apikey"}
    LOGGER.info("Requesting Twelve Data quotes for %s", params["symbol"])
    LOGGER.debug("Twelve Data request parameters without API key: %s", safe_params)

    try:
        response = requests.get(TWELVE_DATA_QUOTE_URL, params=params, timeout=20)
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
        raise TwelveDataError("Twelve Data quote response should be a JSON object.")
    if not payload:
        raise TwelveDataError("Twelve Data returned no quote data for the requested symbols.")

    return payload
