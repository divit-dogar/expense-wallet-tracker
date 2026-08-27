from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.expense import Expense, ExpenseStatus
from app.repositories.expense import ExpenseRepository
from app.repositories.wallet import WalletRepository
from app.repositories.expense_category import ExpenseCategoryRepository
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
)


router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"],
)


@router.post(
    "/",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_expense(
    expense_data: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
):
    expense_repository = ExpenseRepository(db)
    wallet_repository = WalletRepository(db)
    category_repository = ExpenseCategoryRepository(db)

    wallet = await wallet_repository.get_by_uuid(
        expense_data.wallet_id
    )

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    category = await category_repository.get_by_uuid(
        expense_data.category_id
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense category not found",
        )

    expense = Expense(
        user_id=1,
        wallet_id=wallet.id,
        category_id=category.id,
        amount=expense_data.amount,
        description=expense_data.description,
        expense_date=expense_data.expense_date,
        status=ExpenseStatus.ACTIVE,
    )

    created_expense = await expense_repository.create(expense)

    return ExpenseResponse(
        uuid=created_expense.uuid,
        wallet_id=wallet.uuid,
        category_id=category.uuid,
        amount=created_expense.amount,
        description=created_expense.description,
        expense_date=created_expense.expense_date,
        status=created_expense.status,
    )


@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
)
async def get_expense(
    expense_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    expense_repository = ExpenseRepository(db)
    wallet_repository = WalletRepository(db)
    category_repository = ExpenseCategoryRepository(db)

    expense = await expense_repository.get_by_uuid(
        expense_id
    )

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    wallet = await wallet_repository.get_by_id(
        expense.wallet_id
    )

    category = await category_repository.get_by_id(
        expense.category_id
    )

    return ExpenseResponse(
        uuid=expense.uuid,
        wallet_id=wallet.uuid,
        category_id=category.uuid,
        amount=expense.amount,
        description=expense.description,
        expense_date=expense.expense_date,
        status=expense.status,
    )

@router.patch(
    "/{expense_id}",
    response_model=ExpenseResponse,
)
async def update_expense(
    expense_id: UUID,
    expense_data: ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
):
    expense_repository = ExpenseRepository(db)
    wallet_repository = WalletRepository(db)
    category_repository = ExpenseCategoryRepository(db)

    expense = await expense_repository.get_by_uuid(
        expense_id
    )

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    update_data = expense_data.model_dump(
        exclude_unset=True
    )

    if "wallet_id" in update_data:
        wallet = await wallet_repository.get_by_uuid(
            update_data["wallet_id"]
        )

        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found",
            )

        update_data["wallet_id"] = wallet.id

    if "category_id" in update_data:
        category = await category_repository.get_by_uuid(
            update_data["category_id"]
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense category not found",
            )

        update_data["category_id"] = category.id

    for field, value in update_data.items():
        setattr(expense, field, value)

    return await expense_repository.update(expense)

@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_expense(
    expense_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    repository = ExpenseRepository(db)

    expense = await repository.get_by_uuid(
        expense_id
    )

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    await repository.delete(expense)

    return None