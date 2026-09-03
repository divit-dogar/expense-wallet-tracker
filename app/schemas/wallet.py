from uuid import UUID

from pydantic import BaseModel, Field

from app.models.wallet import Currency, WalletStatus, WalletType


class WalletCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    wallet_type: WalletType
    opening_balance: float = 0
    currency: Currency = Currency.INR


class WalletUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    wallet_type: WalletType | None = None
    currency: Currency | None = None
    status: WalletStatus | None = None


class WalletResponse(BaseModel):
    uuid: UUID
    name: str
    wallet_type: WalletType
    opening_balance: float
    current_balance: float
    currency: Currency
    status: WalletStatus

    model_config = {
        "from_attributes": True
    }