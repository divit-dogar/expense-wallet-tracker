from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense
from app.models.wallet import Wallet
from app.models.expense_category import ExpenseCategory


class ExpenseRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        expense: Expense,
    ) -> Expense:
        self.db.add(expense)
        await self.db.commit()
        await self.db.refresh(expense)

        return expense

    async def get_by_uuid(
        self,
        expense_uuid: UUID,
    ) -> Expense | None:
        statement = select(Expense).where(
            Expense.uuid == expense_uuid
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: int,
        wallet_id: int | None = None,
        category_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[Expense]:

        statement = select(Expense).where(
            Expense.user_id == user_id
        )

        if wallet_id is not None:
            statement = statement.where(
                Expense.wallet_id == wallet_id
            )

        if category_id is not None:
            statement = statement.where(
                Expense.category_id == category_id
            )

        if from_date is not None:
            statement = statement.where(
                Expense.expense_date >= from_date
            )

        if to_date is not None:
            statement = statement.where(
                Expense.expense_date <= to_date
            )

        result = await self.db.execute(statement)

        return list(result.scalars().all())

    async def get_wallet_by_uuid(
        self,
        wallet_uuid: UUID,
    ) -> Wallet | None:
        statement = select(Wallet).where(
            Wallet.uuid == wallet_uuid
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def get_category_by_uuid(
        self,
        category_uuid: UUID,
    ) -> ExpenseCategory | None:
        statement = select(ExpenseCategory).where(
            ExpenseCategory.uuid == category_uuid
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def update(
        self,
        expense: Expense,
    ) -> Expense:
        await self.db.commit()
        await self.db.refresh(expense)

        return expense

    async def delete(
        self,
        expense: Expense,
    ) -> None:
        await self.db.delete(expense)
        await self.db.commit()