import logging
from datetime import date

from fastapi import Depends, FastAPI, Query

from app.config import Settings, get_settings
from app.exceptions import ProviderError, provider_error_handler
from app.logging_config import configure_logging
from app.providers.mock_rates import MockRatesProvider
from app.providers.mock_weather import MockWeatherProvider
from app.schemas import HealthResponse, RatesResponse, WeatherResponse


settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ops Weather Platform",
    description="Training service for weather and exchange-rate DevOps workflows.",
    version="1.0.0",
)
app.add_exception_handler(ProviderError, provider_error_handler)

weather_provider = MockWeatherProvider()
rates_provider = MockRatesProvider()


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    logger.info("Health check requested")
    return HealthResponse(service=settings.app_name, environment=settings.environment)


@app.get("/weather", response_model=WeatherResponse, tags=["data"])
async def weather(
    date: date = Query(..., description="Date in YYYY-MM-DD format"),
    city: str = Query(..., min_length=2, max_length=80),
) -> WeatherResponse:
    logger.info("Weather requested", extra={"city": city, "date": str(date)})
    return await weather_provider.get_weather(requested_date=date, city=city)


@app.get("/rates", response_model=RatesResponse, tags=["data"])
async def rates(
    date: date = Query(..., description="Date in YYYY-MM-DD format"),
    base: str = Query("USD", min_length=3, max_length=3),
    target: str = Query("RUB", min_length=3, max_length=3),
) -> RatesResponse:
    logger.info("Rate requested", extra={"base": base, "target": target, "date": str(date)})
    return await rates_provider.get_rate(requested_date=date, base=base, target=target)
