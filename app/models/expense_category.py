import uuid as uuid_lib
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.expense import Expense


class ExpenseCategoryStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

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

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="expense_categories"
    )

    expenses: Mapped[list["Expense"]] = relationship(
        back_populates="category"
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    parent_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("expense_categories.id"),
        nullable=True,
    )

    parent: Mapped["ExpenseCategory | None"] = relationship(
        back_populates="children",
        remote_side="ExpenseCategory.id",
    )

    children: Mapped[list["ExpenseCategory"]] = relationship(
        back_populates="parent"
    )

    status: Mapped[ExpenseCategoryStatus] = mapped_column(
        SAEnum(ExpenseCategoryStatus),
        nullable=False,
        default=ExpenseCategoryStatus.ACTIVE,
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