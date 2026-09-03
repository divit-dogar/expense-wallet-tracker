from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense, ExpenseStatus
from app.models.expense_category import ExpenseCategory
from app.models.wallet import Wallet


class DashboardRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_total_wallet_balance(
        self,
        user_id: int,
    ) -> float:

        statement = select(
            func.coalesce(
                func.sum(Wallet.current_balance),
                0,
            )
        ).where(
            Wallet.user_id == user_id
        )

        result = await self.db.execute(statement)

        return float(result.scalar_one())

    async def get_expense_total(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> float:

        statement = select(
            func.coalesce(
                func.sum(Expense.amount),
                0,
            )
        ).where(
            Expense.user_id == user_id,
            Expense.status == ExpenseStatus.ACTIVE,
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date,
        )

        result = await self.db.execute(statement)

        return float(result.scalar_one())

    async def get_wallet_wise_expenses(
        self,
        user_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ):

        statement = (
            select(
                Wallet.uuid,
                Wallet.name,
                func.coalesce(
                    func.sum(Expense.amount),
                    0,
                ).label("total"),
            )
            .join(
                Expense,
                Expense.wallet_id == Wallet.id,
            )
            .where(
                Wallet.user_id == user_id,
                Expense.user_id == user_id,
                Expense.status == ExpenseStatus.ACTIVE,
            )
            .group_by(
                Wallet.id,
                Wallet.uuid,
                Wallet.name,
            )
        )

        if start_date is not None:
            statement = statement.where(
                Expense.expense_date >= start_date
            )

        if end_date is not None:
            statement = statement.where(
                Expense.expense_date <= end_date
            )

        result = await self.db.execute(statement)

        return result.all()

    async def get_category_wise_expenses(
        self,
        user_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ):

        statement = (
            select(
                ExpenseCategory.uuid,
                ExpenseCategory.name,
                func.coalesce(
                    func.sum(Expense.amount),
                    0,
                ).label("total"),
            )
            .join(
                Expense,
                Expense.category_id == ExpenseCategory.id,
            )
            .where(
                ExpenseCategory.user_id == user_id,
                Expense.user_id == user_id,
                Expense.status == ExpenseStatus.ACTIVE,
            )
            .group_by(
                ExpenseCategory.id,
                ExpenseCategory.uuid,
                ExpenseCategory.name,
            )
        )

        if start_date is not None:
            statement = statement.where(
                Expense.expense_date >= start_date
            )

        if end_date is not None:
            statement = statement.where(
                Expense.expense_date <= end_date
            )

        result = await self.db.execute(statement)

        return result.all()

    async def get_recent_expenses(
        self,
        user_id: int,
        limit: int = 5,
    ) -> list[Expense]:

        statement = (
            select(Expense)
            .where(
                Expense.user_id == user_id,
                Expense.status == ExpenseStatus.ACTIVE,
            )
            .order_by(
                Expense.expense_date.desc()
            )
            .limit(limit)
        )

        result = await self.db.execute(statement)

        return list(result.scalars().all())