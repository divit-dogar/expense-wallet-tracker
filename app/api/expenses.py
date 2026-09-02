from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.expense import ExpenseRepository
from app.repositories.wallet import WalletRepository
from app.repositories.expense_category import ExpenseCategoryRepository
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
)
from app.services.expense_service import ExpenseService


router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"],
)


# =========================================================
# 1. CREATE EXPENSE
# =========================================================
@router.post(
    "/",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExpenseService(db)

    created_expense = await service.create_expense(
        user_id=current_user.id,
        wallet_uuid=expense_data.wallet_id,
        category_uuid=expense_data.category_id,
        amount=expense_data.amount,
        description=expense_data.description,
        expense_date=expense_data.expense_date,
    )

    wallet_repository = WalletRepository(db)
    category_repository = ExpenseCategoryRepository(db)

    # Get wallet
    wallet = await wallet_repository.get_by_id(
        created_expense.wallet_id
    )

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    # Category can be NULL
    category = None

    if created_expense.category_id is not None:
        category = await category_repository.get_by_id(
            created_expense.category_id
        )

    return ExpenseResponse(
        uuid=created_expense.uuid,
        wallet_id=wallet.uuid,
        category_id=category.uuid if category else None,
        amount=created_expense.amount,
        description=created_expense.description,
        expense_date=created_expense.expense_date,
        status=created_expense.status,
    )


# =========================================================
# 2. GET ALL EXPENSES / FILTER EXPENSES
# =========================================================
@router.get(
    "/",
    response_model=list[ExpenseResponse],
)
async def get_expenses(
    wallet_id: UUID | None = None,
    category_id: UUID | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExpenseService(db)

    expenses = await service.get_expenses(
        user_id=current_user.id,
        wallet_uuid=wallet_id,
        category_uuid=category_id,
        from_date=from_date,
        to_date=to_date,
    )

    wallet_repository = WalletRepository(db)
    category_repository = ExpenseCategoryRepository(db)

    response = []

    for expense in expenses:

        # Get wallet
        wallet = await wallet_repository.get_by_id(
            expense.wallet_id
        )

        if not wallet:
            continue

        # Category can be NULL
        category = None

        if expense.category_id is not None:
            category = await category_repository.get_by_id(
                expense.category_id
            )

        response.append(
            ExpenseResponse(
                uuid=expense.uuid,
                wallet_id=wallet.uuid,
                category_id=category.uuid if category else None,
                amount=expense.amount,
                description=expense.description,
                expense_date=expense.expense_date,
                status=expense.status,
            )
        )

    return response


# =========================================================
# 3. GET ONE EXPENSE
# =========================================================
@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
)
async def get_expense(
    expense_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    expense_repository = ExpenseRepository(db)
    wallet_repository = WalletRepository(db)
    category_repository = ExpenseCategoryRepository(db)

    expense = await expense_repository.get_by_uuid(
        expense_id
    )

    if not expense or expense.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    # Get wallet
    wallet = await wallet_repository.get_by_id(
        expense.wallet_id
    )

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    # Category can be NULL
    category = None

    if expense.category_id is not None:
        category = await category_repository.get_by_id(
            expense.category_id
        )

    return ExpenseResponse(
        uuid=expense.uuid,
        wallet_id=wallet.uuid,
        category_id=category.uuid if category else None,
        amount=expense.amount,
        description=expense.description,
        expense_date=expense.expense_date,
        status=expense.status,
    )


# =========================================================
# 4. UPDATE EXPENSE
# =========================================================
@router.patch(
    "/{expense_id}",
    response_model=ExpenseResponse,
)
async def update_expense(
    expense_id: UUID,
    expense_data: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExpenseService(db)

    update_data = expense_data.model_dump(
        exclude_unset=True
    )

    updated_expense = await service.update_expense(
        user_id=current_user.id,
        expense_uuid=expense_id,
        wallet_uuid=update_data.get("wallet_id"),
        category_uuid=update_data.get("category_id"),
        amount=update_data.get("amount"),
        description=update_data.get("description"),
        expense_date=update_data.get("expense_date"),
        status=update_data.get("status"),
    )

    wallet_repository = WalletRepository(db)
    category_repository = ExpenseCategoryRepository(db)

    # Get wallet
    wallet = await wallet_repository.get_by_id(
        updated_expense.wallet_id
    )

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    # Category can be NULL
    category = None

    if updated_expense.category_id is not None:
        category = await category_repository.get_by_id(
            updated_expense.category_id
        )

    return ExpenseResponse(
        uuid=updated_expense.uuid,
        wallet_id=wallet.uuid,
        category_id=category.uuid if category else None,
        amount=updated_expense.amount,
        description=updated_expense.description,
        expense_date=updated_expense.expense_date,
        status=updated_expense.status,
    )


# =========================================================
# 5. DELETE EXPENSE
# =========================================================
@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_expense(
    expense_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExpenseService(db)

    await service.delete_expense(
        user_id=current_user.id,
        expense_uuid=expense_id,
    )

    return {
        "message": "Expense deleted successfully"
    }