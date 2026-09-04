from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.factories.currency_factory import CurrencyFactory
from app.models.wallet import Wallet
from app.repositories.wallet import WalletRepository
from app.services.currency import CurrencyService


class WalletService:

    def __init__(self, db: AsyncSession):
        self.repository = WalletRepository(db)

        currency_strategy = CurrencyFactory.create_strategy(
            settings.CURRENCY_PROVIDER
        )

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