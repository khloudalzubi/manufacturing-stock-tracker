from pydantic import BaseModel, ConfigDict, Field


class TwelveDataQuote(BaseModel):
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
