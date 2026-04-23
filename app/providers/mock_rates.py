from datetime import date
from app.exceptions import ProviderError
from app.schemas import RatesResponse


class MockRatesProvider:
    baseline_rates = {
        ("USD", "RUB"): 92.5,
        ("EUR", "RUB"): 99.8,
        ("USD", "EUR"): 0.93,
        ("RUB", "USD"): 0.0108,
    }

    async def get_rate(self, requested_date: date, base: str, target: str) -> RatesResponse:
        normalized_base = base.upper()
        normalized_target = target.upper()

        if normalized_base == normalized_target:
            rate = 1.0
        else:
            pair = (normalized_base, normalized_target)
            if pair not in self.baseline_rates:
                raise ProviderError(
                    f"Currency pair {normalized_base}/{normalized_target} is not supported by the mock provider",
                    status_code=404,
                )
            daily_offset = ((requested_date.toordinal() % 17) - 8) / 1000
            rate = round(self.baseline_rates[pair] * (1 + daily_offset), 4)

        return RatesResponse(
            date=requested_date,
            base=normalized_base,
            target=normalized_target,
            rate=rate,
            source="mock-rates-provider",
        )

