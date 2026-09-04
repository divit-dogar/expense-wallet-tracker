from decimal import Decimal

from app.strategies.currency_strategy import CurrencyStrategy


class CurrencyService:

    def __init__(
        self,
        strategy: CurrencyStrategy,
    ):
        self.strategy = strategy

    async def convert_to_inr(
        self,
        amount,
        currency: str,
    ) -> Decimal:

        return await self.strategy.convert_to_inr(
            amount=amount,
            currency=currency,
        )