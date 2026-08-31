from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.expense_category import ExpenseCategory
from app.models.user import User
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


# 1. CREATE
@router.post(
    "/",
    response_model=ExpenseCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category_data: ExpenseCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repository = ExpenseCategoryRepository(db)

    category = ExpenseCategory(
        user_id=current_user.id,
        name=category_data.name,
        description=category_data.description,
        parent_id=category_data.parent_id,
        status="ACTIVE",
    )

    return await repository.create(category)


# 2. GET ALL
@router.get("/")
async def get_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repository = ExpenseCategoryRepository(db)

    categories = await repository.get_by_user(
        user_id=current_user.id
    )

    return {
        "categories": categories,
    }


# 3. GET ONE
@router.get(
    "/{category_uuid}",
    response_model=ExpenseCategoryResponse,
)
async def get_category(
    category_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repository = ExpenseCategoryRepository(db)

    category = await repository.get_by_uuid(
        category_uuid
    )

    if not category or category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense category not found",
        )

    return category


# 4. UPDATE
@router.patch(
    "/{category_uuid}",
    response_model=ExpenseCategoryResponse,
)
async def update_category(
    category_uuid: UUID,
    category_data: ExpenseCategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repository = ExpenseCategoryRepository(db)

    category = await repository.get_by_uuid(
        category_uuid
    )

    if not category or category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense category not found",
        )

    update_data = category_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(category, field, value)

    return await repository.update(category)


# 5. DELETE
@router.delete(
    "/{category_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    category_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repository = ExpenseCategoryRepository(db)

    category = await repository.get_by_uuid(
        category_uuid
    )

    if not category or category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense category not found",
        )

    await repository.delete(category)

    return None