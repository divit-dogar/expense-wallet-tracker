from decimal import Decimal

import httpx


class CurrencyService:

    BASE_URL = "https://open.er-api.com/v6/latest"

    async def convert_to_inr(
        self,
        amount,
        currency: str,
    ) -> Decimal:

        currency = currency.upper()

        # Convert amount to Decimal safely
        amount = Decimal(str(amount))

        # No conversion needed
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

        # API rate may be float, so convert it to Decimal
        rate = Decimal(str(rates["INR"]))

        converted_amount = amount * rate

        return converted_amount