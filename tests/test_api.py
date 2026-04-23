from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "ops-weather-platform"


def test_weather_endpoint_returns_stable_mock_data() -> None:
    response = client.get("/weather", params={"date": "2026-04-23", "city": "Moscow"})
    assert response.status_code == 200
    body = response.json()
    assert body["city"] == "Moscow"
    assert body["date"] == "2026-04-23"
    assert body["source"] == "mock-weather-provider"
    assert "temperature_c" in body


def test_rates_endpoint_normalizes_currency_codes() -> None:
    response = client.get(
        "/rates",
        params={"date": "2026-04-23", "base": "usd", "target": "rub"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["base"] == "USD"
    assert body["target"] == "RUB"
    assert body["rate"] > 0


def test_rates_endpoint_rejects_unknown_pair() -> None:
    response = client.get(
        "/rates",
        params={"date": "2026-04-23", "base": "GBP", "target": "JPY"},
    )
    assert response.status_code == 404
    assert "not supported" in response.json()["detail"]
