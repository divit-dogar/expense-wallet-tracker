from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense_category import ExpenseCategory


class ExpenseCategoryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        category: ExpenseCategory,
    ) -> ExpenseCategory:
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)

        return category
    
    async def get_by_id(
        self,
        category_id: int,
    ) -> ExpenseCategory | None:
        statement = select(ExpenseCategory).where(
            ExpenseCategory.id == category_id
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_uuid(
        self,
        category_uuid: UUID,
    ) -> ExpenseCategory | None:
        statement = select(ExpenseCategory).where(
            ExpenseCategory.uuid == category_uuid
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: int,
    ) -> list[ExpenseCategory]:
        statement = select(ExpenseCategory).where(
            ExpenseCategory.user_id == user_id
        )

        result = await self.db.execute(statement)

        return list(result.scalars().all())

    async def update(
        self,
        category: ExpenseCategory,
    ) -> ExpenseCategory:
        await self.db.commit()
        await self.db.refresh(category)

        return category

    async def delete(
        self,
        category: ExpenseCategory,
    ) -> None:
        await self.db.delete(category)
        await self.db.commit()