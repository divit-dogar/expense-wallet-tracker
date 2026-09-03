import uuid as uuid_lib
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.wallet import Wallet
    from app.models.expense_category import ExpenseCategory
    from app.models.expense import Expense


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    uuid: Mapped[uuid_lib.UUID] = mapped_column(
        Uuid,
        unique=True,
        nullable=False,
        default=uuid_lib.uuid4,
    )

    wallets: Mapped[list["Wallet"]] = relationship(
        back_populates="user"
    )

    expense_categories: Mapped[list["ExpenseCategory"]] = relationship(
        back_populates="user"
    )

    expenses: Mapped[list["Expense"]] = relationship(
        back_populates="user"
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[UserStatus] = mapped_column(
        SAEnum(UserStatus),
        nullable=False,
        default=UserStatus.ACTIVE,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )