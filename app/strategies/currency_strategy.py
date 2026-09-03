from abc import ABC, abstractmethod
from decimal import Decimal


class CurrencyStrategy(ABC):

    @abstractmethod
    async def convert_to_inr(
        self,
        amount,
        currency: str,
    ) -> Decimal:
        pass