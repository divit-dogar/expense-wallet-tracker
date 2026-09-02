from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.expense import ExpenseStatus


# =========================================================
# CREATE EXPENSE
# =========================================================
class ExpenseCreate(BaseModel):
    wallet_id: UUID

    # Category is optional
    category_id: UUID | None = None

    amount: float = Field(gt=0)

    description: str | None = None

    expense_date: datetime


# =========================================================
# UPDATE EXPENSE
# =========================================================
class ExpenseUpdate(BaseModel):
    wallet_id: UUID | None = None

    category_id: UUID | None = None

    amount: float | None = Field(
        default=None,
        gt=0,
    )

    description: str | None = None

    expense_date: datetime | None = None

    status: ExpenseStatus | None = None


# =========================================================
# EXPENSE RESPONSE
# =========================================================
class ExpenseResponse(BaseModel):
    uuid: UUID

    wallet_id: UUID

    # Category can be NULL
    category_id: UUID | None = None

    amount: float

    description: str | None

    expense_date: datetime

    status: ExpenseStatus

    model_config = {
        "from_attributes": True
    }