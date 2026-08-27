from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.expense_category import ExpenseCategory
from app.repositories.expense_category import ExpenseCategoryRepository
from app.schemas.expense_category import (
    ExpenseCategoryCreate,
    ExpenseCategoryResponse,
    ExpenseCategoryUpdate,
)

router = APIRouter(
    prefix="/expense-categories",
    tags=["Expense Categories"],
)


@router.post(
    "/",
    response_model=ExpenseCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category_data: ExpenseCategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    repository = ExpenseCategoryRepository(db)

    category = ExpenseCategory(
        user_id=1,
        name=category_data.name,
        description=category_data.description,
        parent_id=category_data.parent_id,
        status="ACTIVE",
    )

    return await repository.create(category)


@router.get("/")
async def get_categories(
    db: AsyncSession = Depends(get_db),
):
    repository = ExpenseCategoryRepository(db)

    categories = await repository.get_by_user(
        user_id=1
    )

    return {
        "categories": categories,
    }


@router.get(
    "/{category_uuid}",
    response_model=ExpenseCategoryResponse,
)
async def get_category(
    category_uuid: UUID,
    db: AsyncSession = Depends(get_db),
):
    repository = ExpenseCategoryRepository(db)

    category = await repository.get_by_uuid(category_uuid)

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Expense category not found",
        )

    return category


@router.patch(
    "/{category_uuid}",
    response_model=ExpenseCategoryResponse,
)
async def update_category(
    category_uuid: UUID,
    category_data: ExpenseCategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    repository = ExpenseCategoryRepository(db)

    category = await repository.get_by_uuid(category_uuid)

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Expense category not found",
        )

    update_data = category_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(category, field, value)

    return await repository.update(category)


@router.delete(
    "/{category_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    category_uuid: UUID,
    db: AsyncSession = Depends(get_db),
):
    repository = ExpenseCategoryRepository(db)

    category = await repository.get_by_uuid(category_uuid)

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Expense category not found",
        )

    await repository.delete(category)