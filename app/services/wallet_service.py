from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import Wallet
from app.repositories.wallet import WalletRepository


class WalletService:

    def __init__(self, db: AsyncSession):
        self.repository = WalletRepository(db)

    async def create_wallet(
        self,
        wallet: Wallet,
    ) -> Wallet:

        wallet.current_balance = wallet.opening_balance

        return await self.repository.create(wallet)