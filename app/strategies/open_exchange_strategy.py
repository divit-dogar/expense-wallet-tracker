from decimal import Decimal

import httpx

from app.strategies.currency_strategy import CurrencyStrategy


class OpenExchangeStrategy(CurrencyStrategy):

    BASE_URL = "https://open.er-api.com/v6/latest"

    async def convert_to_inr(
        self,
        amount,
        currency: str,
    ) -> Decimal:

        currency = currency.upper()

        amount = Decimal(str(amount))

        if currency == "INR":
            return amount

        url = f"{self.BASE_URL}/{currency}"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                timeout=10.0,
            )

            response.raise_for_status()

            data = response.json()

        rates = data.get("rates", {})

        if "INR" not in rates:
            raise ValueError(
                f"Currency conversion rate not available "
                f"for {currency} -> INR"
            )

        rate = Decimal(str(rates["INR"]))

        return amount * rate