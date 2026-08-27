from uuid import UUID

from pydantic import BaseModel, Field

from app.models.expense_category import ExpenseCategoryStatus


class ExpenseCategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    parent_id: UUID | None = None


class ExpenseCategoryUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    description: str | None = None
    parent_id: UUID | None = None
    status: ExpenseCategoryStatus | None = None


class ExpenseCategoryResponse(BaseModel):
    uuid: UUID
    name: str
    description: str | None
    parent_id: UUID | None
    status: ExpenseCategoryStatus

    model_config = {
        "from_attributes": True
    }