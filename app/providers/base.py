from abc import ABC, abstractmethod
from datetime import date

from app.schemas import RatesResponse, WeatherResponse


class WeatherProvider(ABC):
    @abstractmethod
    async def get_weather(self, requested_date: date, city: str) -> WeatherResponse:
        raise NotImplementedError


class RatesProvider(ABC):
    @abstractmethod
    async def get_rate(self, requested_date: date, base: str, target: str) -> RatesResponse:
        raise NotImplementedError
