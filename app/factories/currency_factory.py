from app.strategies.currency_strategy import CurrencyStrategy
from app.strategies.open_exchange_strategy import OpenExchangeStrategy


class CurrencyFactory:

    @staticmethod
    def create_strategy(
        provider: str,
    ) -> CurrencyStrategy:

        provider = provider.lower()

        if provider == "open_exchange":
            return OpenExchangeStrategy()

        raise ValueError(
            f"Unsupported currency provider: {provider}"
        )