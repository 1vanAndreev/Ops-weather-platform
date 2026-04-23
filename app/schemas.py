from datetime import date, datetime, timezone
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str
    environment: str
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WeatherResponse(BaseModel):
    city: str
    date: date
    temperature_c: float
    humidity_percent: int
    wind_kph: float
    condition: str
    source: str


class RatesResponse(BaseModel):
    date: date
    base: str
    target: str
    rate: float
    source: str

