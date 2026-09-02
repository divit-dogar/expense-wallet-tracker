from uuid import UUID
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense


class ExpenseRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # CREATE
    async def create(
        self,
        expense: Expense,
    ) -> Expense:
        self.db.add(expense)

        await self.db.commit()
        await self.db.refresh(expense)

        return expense

    # GET BY INTERNAL ID
    async def get_by_id(
        self,
        expense_id: int,
    ) -> Expense | None:

        statement = select(Expense).where(
            Expense.id == expense_id
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    # GET BY UUID
    async def get_by_uuid(
        self,
        expense_uuid: UUID,
    ) -> Expense | None:

        statement = select(Expense).where(
            Expense.uuid == expense_uuid
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    # GET USER EXPENSES WITH FILTERS
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

        # FILTER BY WALLET
        if wallet_id is not None:
            statement = statement.where(
                Expense.wallet_id == wallet_id
            )

        # FILTER BY CATEGORY
        if category_id is not None:
            statement = statement.where(
                Expense.category_id == category_id
            )

        # FILTER FROM DATE
        if from_date is not None:
            statement = statement.where(
                Expense.expense_date >= from_date
            )

        # FILTER TO DATE
        if to_date is not None:
            statement = statement.where(
                Expense.expense_date <= to_date
            )

        result = await self.db.execute(statement)

        return list(result.scalars().all())

    # CHECK WHETHER WALLET HAS EXPENSES
    async def exists_by_wallet(
        self,
        wallet_id: int,
    ) -> bool:

        statement = (
            select(Expense.id)
            .where(
                Expense.wallet_id == wallet_id
            )
            .limit(1)
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none() is not None

    # UPDATE
    async def update(
        self,
        expense: Expense,
    ) -> Expense:

        await self.db.commit()
        await self.db.refresh(expense)

        return expense

    # DELETE
    async def delete(
        self,
        expense: Expense,
    ) -> None:

        await self.db.delete(expense)
        await self.db.commit()