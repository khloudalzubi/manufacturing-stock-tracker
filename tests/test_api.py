import pytest
import requests

from manufacturing_stock_tracker.api import TWELVE_DATA_QUOTE_URL, TwelveDataError, fetch_quotes


class FakeResponse:
    def __init__(self, payload, status_code: int = 200, reason: str = "OK") -> None:
        self.payload = payload
        self.status_code = status_code
        self.reason = reason

    def json(self):
        return self.payload


def test_fetch_quotes_sends_expected_watchlist_request_without_exposing_key(monkeypatch) -> None:
    calls = []
    payload = {"CAT": {"symbol": "CAT", "close": "356.42"}}

    def fake_get(url, params, timeout):
        calls.append({"url": url, "params": params, "timeout": timeout})
        return FakeResponse(payload)

    monkeypatch.setattr("manufacturing_stock_tracker.api.requests.get", fake_get)

    assert fetch_quotes(["CAT", "DE", "HON"], "secret-key") == payload
    assert calls == [
        {
            "url": TWELVE_DATA_QUOTE_URL,
            "params": {
                "symbol": "CAT,DE,HON",
                "apikey": "secret-key",
            },
            "timeout": 20,
        }
    ]


def test_fetch_quotes_turns_api_error_payload_into_clear_error(monkeypatch) -> None:
    def fake_get(url, params, timeout):
        return FakeResponse({"status": "error", "message": "Invalid API key."})

    monkeypatch.setattr("manufacturing_stock_tracker.api.requests.get", fake_get)

    with pytest.raises(TwelveDataError, match="Invalid API key"):
        fetch_quotes(["CAT"], "secret-key")


def test_fetch_quotes_turns_http_failure_into_sanitized_error(monkeypatch) -> None:
    def fake_get(url, params, timeout):
        return FakeResponse({}, status_code=429, reason="Too Many Requests")

    monkeypatch.setattr("manufacturing_stock_tracker.api.requests.get", fake_get)

    with pytest.raises(TwelveDataError, match="HTTP 429 Too Many Requests") as exc_info:
        fetch_quotes(["CAT"], "secret-key")

    assert "secret-key" not in str(exc_info.value)
    assert "apikey" not in str(exc_info.value)


def test_fetch_quotes_turns_request_exception_into_sanitized_error(monkeypatch) -> None:
    def fake_get(url, params, timeout):
        raise requests.ConnectionError("network unavailable")

    monkeypatch.setattr("manufacturing_stock_tracker.api.requests.get", fake_get)

    with pytest.raises(TwelveDataError, match="ConnectionError") as exc_info:
        fetch_quotes(["CAT"], "secret-key")

    assert "secret-key" not in str(exc_info.value)
    assert "apikey" not in str(exc_info.value)


def test_fetch_quotes_requires_api_key() -> None:
    with pytest.raises(TwelveDataError, match="TWELVE_DATA_API_KEY"):
        fetch_quotes(["CAT"], "")
