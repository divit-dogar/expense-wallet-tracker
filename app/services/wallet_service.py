from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import Wallet
from app.repositories.wallet import WalletRepository
from app.services.currency import CurrencyService
from app.strategies.open_exchange_strategy import OpenExchangeStrategy


class WalletService:

    def __init__(self, db: AsyncSession):
        self.repository = WalletRepository(db)

        currency_strategy = OpenExchangeStrategy()

        self.currency_service = CurrencyService(
            strategy=currency_strategy,
        )

    async def create_wallet(
        self,
        wallet: Wallet,
    ) -> Wallet:

        converted_balance = (
            await self.currency_service.convert_to_inr(
                amount=wallet.opening_balance,
                currency=wallet.currency,
            )
        )

        wallet.opening_balance = converted_balance
        wallet.current_balance = converted_balance
        wallet.currency = "INR"

        return await self.repository.create(wallet)