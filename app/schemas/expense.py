from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.expense import ExpenseStatus


class ExpenseCreate(BaseModel):
    wallet_id: UUID
    category_id: UUID
    amount: float = Field(gt=0)
    description: str | None = None
    expense_date: datetime


class ExpenseUpdate(BaseModel):
    wallet_id: UUID | None = None
    category_id: UUID | None = None
    amount: float | None = Field(default=None, gt=0)
    description: str | None = None
    expense_date: datetime | None = None
    status: ExpenseStatus | None = None


class ExpenseResponse(BaseModel):
    uuid: UUID
    wallet_id: UUID
    category_id: UUID
    amount: float
    description: str | None
    expense_date: datetime
    status: ExpenseStatus

    model_config = {
        "from_attributes": True
    }