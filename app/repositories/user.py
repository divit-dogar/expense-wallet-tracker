from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_uuid(self,user_uuid: UUID,) -> User | None:
        statement = select(User).where(
            User.uuid == user_uuid
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_email(self,email: str,) -> User | None:
        statement = select(User).where(
            User.email == email
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()