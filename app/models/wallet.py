import uuid as uuid_lib
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.expense import Expense


class WalletType(str, Enum):
    CASH = "CASH"
    BANK = "BANK"
    UPI = "UPI"
    CREDIT_CARD = "CREDIT_CARD"
    OTHER = "OTHER"


class WalletStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    CLOSED = "CLOSED"


class Currency(str, Enum):
    INR = "INR"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    AED = "AED"


class Wallet(Base):
    __tablename__ = "wallets"

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
        back_populates="wallets"
    )

    expenses: Mapped[list["Expense"]] = relationship(
        back_populates="wallet"
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    wallet_type: Mapped[WalletType] = mapped_column(
        SAEnum(WalletType),
        nullable=False,
    )

    opening_balance: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    current_balance: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    currency: Mapped[Currency] = mapped_column(
        SAEnum(Currency),
        nullable=False,
        default=Currency.INR,
    )

    status: Mapped[WalletStatus] = mapped_column(
        SAEnum(WalletStatus),
        nullable=False,
        default=WalletStatus.ACTIVE,
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