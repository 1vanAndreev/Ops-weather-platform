from datetime import date
from app.schemas import WeatherResponse


class MockWeatherProvider:
    conditions = ["clear", "cloudy", "rain", "windy", "snow"]

    async def get_weather(self, requested_date: date, city: str) -> WeatherResponse:
        seed = sum(ord(char) for char in city.lower()) + requested_date.toordinal()
        temperature = round(((seed % 420) / 10) - 12, 1)
        humidity = 35 + (seed % 55)
        wind = round(4 + (seed % 260) / 10, 1)
        condition = self.conditions[seed % len(self.conditions)]
        return WeatherResponse(
            city=city,
            date=requested_date,
            temperature_c=temperature,
            humidity_percent=humidity,
            wind_kph=wind,
            condition=condition,
            source="mock-weather-provider",
        )

