"""Pydantic models for validated Twelve Data response structures."""

from pydantic import BaseModel, ConfigDict, Field


class TwelveDataQuote(BaseModel):
    """Validated current quote object returned by Twelve Data."""

    model_config = ConfigDict(extra="allow")

    symbol: str = Field(min_length=1)
    name: str | None = None
    exchange: str | None = None
    currency: str | None = None
    datetime: str | None = None
    timestamp: int | None = None
    open_price: float | None = Field(default=None, alias="open")
    high: float | None = None
    low: float | None = None
    close: float
    volume: int | None = None
    previous_close: float | None = None
    change: float | None = None
    percent_change: float | None = None


class TwelveDataTimeSeriesMeta(BaseModel):
    """Metadata for a Twelve Data historical time-series response."""

    model_config = ConfigDict(extra="allow")

    symbol: str = Field(min_length=1)
    interval: str | None = None
    currency: str | None = None
    exchange: str | None = None
    exchange_timezone: str | None = None
    type: str | None = None


class TwelveDataPriceBar(BaseModel):
    """One validated OHLCV bar from a Twelve Data time series."""

    model_config = ConfigDict(extra="allow")

    datetime: str = Field(min_length=1)
    open_price: float = Field(alias="open")
    high: float
    low: float
    close: float
    volume: int | None = None


class TwelveDataTimeSeries(BaseModel):
    """Validated historical time-series response for one ticker symbol."""

    model_config = ConfigDict(extra="allow")

    meta: TwelveDataTimeSeriesMeta
    values: list[TwelveDataPriceBar] = Field(min_length=2)
    status: str | None = None
