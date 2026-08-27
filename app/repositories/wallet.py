from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import Wallet


class WalletRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, wallet: Wallet) -> Wallet:
        self.db.add(wallet)
        await self.db.commit()
        await self.db.refresh(wallet)
        return wallet
   
    async def get_by_id(
        self,
        wallet_id: int,
    ) -> Wallet | None:
        statement = select(Wallet).where(
            Wallet.id == wallet_id
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_uuid(
        self,
        wallet_uuid: UUID,
    ) -> Wallet | None:
        statement = select(Wallet).where(
            Wallet.uuid == wallet_uuid
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: int,
    ) -> list[Wallet]:
        statement = select(Wallet).where(
            Wallet.user_id == user_id
        )

        result = await self.db.execute(statement)

        return list(result.scalars().all())

    async def update(
        self,
        wallet: Wallet,
    ) -> Wallet:
        await self.db.commit()
        await self.db.refresh(wallet)

        return wallet

    async def delete(
        self,
        wallet: Wallet,
    ) -> None:
        await self.db.delete(wallet)
        await self.db.commit()