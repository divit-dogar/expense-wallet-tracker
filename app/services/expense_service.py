from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense, ExpenseStatus
from app.repositories.expense import ExpenseRepository
from app.repositories.expense_category import ExpenseCategoryRepository
from app.repositories.wallet import WalletRepository


class ExpenseService:

    def __init__(self, db: AsyncSession):
        self.expense_repository = ExpenseRepository(db)
        self.wallet_repository = WalletRepository(db)
        self.category_repository = ExpenseCategoryRepository(db)

    async def create_expense(
        self,
        user_id: int,
        wallet_uuid: UUID,
        category_uuid: UUID,
        amount: float,
        description: str | None,
        expense_date: datetime,
    ) -> Expense:

        wallet = await self.wallet_repository.get_by_uuid(
            wallet_uuid
        )

        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found",
            )

        if wallet.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found",
            )

        category = await self.category_repository.get_by_uuid(
            category_uuid
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense category not found",
            )

        if category.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense category not found",
            )

        expense_amount = Decimal(str(amount))

        if wallet.current_balance < expense_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient wallet balance",
            )

        expense = Expense(
            user_id=user_id,
            wallet_id=wallet.id,
            category_id=category.id,
            amount=expense_amount,
            description=description,
            expense_date=expense_date,
            status=ExpenseStatus.ACTIVE,
        )

        wallet.current_balance -= expense_amount

        return await self.expense_repository.create(
            expense
        )

    async def get_expenses(
        self,
        user_id: int,
        wallet_uuid: UUID | None = None,
        category_uuid: UUID | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[Expense]:

        wallet_id = None
        category_id = None

        # Validate wallet and convert UUID to database ID
        if wallet_uuid is not None:
            wallet = await self.wallet_repository.get_by_uuid(
                wallet_uuid
            )

            if not wallet:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Wallet not found",
                )

            if wallet.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Wallet not found",
                )

            wallet_id = wallet.id

        # Validate category and convert UUID to database ID
        if category_uuid is not None:
            category = await self.category_repository.get_by_uuid(
                category_uuid
            )

            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Expense category not found",
                )

            if category.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Expense category not found",
                )

            category_id = category.id

        return await self.expense_repository.get_by_user(
            user_id=user_id,
            wallet_id=wallet_id,
            category_id=category_id,
            from_date=from_date,
            to_date=to_date,
        )

    async def update_expense(
        self,
        user_id: int,
        expense_uuid: UUID,
        wallet_uuid: UUID | None = None,
        category_uuid: UUID | None = None,
        amount: float | None = None,
        description: str | None = None,
        expense_date: datetime | None = None,
        status: ExpenseStatus | None = None,
    ) -> Expense:

        expense = await self.expense_repository.get_by_uuid(
            expense_uuid
        )

        if not expense or expense.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found",
            )

        old_amount = Decimal(str(expense.amount))
        old_wallet_id = expense.wallet_id

        # Get current wallet
        old_wallet = await self.wallet_repository.get_by_id(
            old_wallet_id
        )

        if not old_wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found",
            )

        # Convert new amount to Decimal
        new_amount = (
            Decimal(str(amount))
            if amount is not None
            else old_amount
        )

        # Handle wallet change
        if wallet_uuid is not None:

            new_wallet = await self.wallet_repository.get_by_uuid(
                wallet_uuid
            )

            if (
                not new_wallet
                or new_wallet.user_id != user_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Wallet not found",
                )

            if new_wallet.id != old_wallet_id:

                if new_wallet.current_balance < new_amount:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Insufficient wallet balance",
                    )

                # Return old expense amount to old wallet
                old_wallet.current_balance += old_amount

                # Deduct new expense amount from new wallet
                new_wallet.current_balance -= new_amount

                expense.wallet_id = new_wallet.id

            else:
                # Same wallet, only amount changed
                difference = new_amount - old_amount

                if difference > 0:

                    if old_wallet.current_balance < difference:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Insufficient wallet balance",
                        )

                    old_wallet.current_balance -= difference

                elif difference < 0:

                    old_wallet.current_balance += abs(
                        difference
                    )

        # Handle amount change without wallet change
        elif amount is not None and new_amount != old_amount:

            difference = new_amount - old_amount

            if difference > 0:

                if old_wallet.current_balance < difference:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Insufficient wallet balance",
                    )

                old_wallet.current_balance -= difference

            elif difference < 0:

                old_wallet.current_balance += abs(
                    difference
                )

        # Handle category change
        if category_uuid is not None:

            category = await self.category_repository.get_by_uuid(
                category_uuid
            )

            if (
                not category
                or category.user_id != user_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Expense category not found",
                )

            expense.category_id = category.id

        # Update expense fields
        if amount is not None:
            expense.amount = new_amount

        if description is not None:
            expense.description = description

        if expense_date is not None:
            expense.expense_date = expense_date

        if status is not None:
            expense.status = status

        return await self.expense_repository.update(
            expense
        )

    async def delete_expense(
        self,
        user_id: int,
        expense_uuid: UUID,
    ) -> None:

        expense = await self.expense_repository.get_by_uuid(
            expense_uuid
        )

        if not expense or expense.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found",
            )

        wallet = await self.wallet_repository.get_by_id(
            expense.wallet_id
        )

        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found",
            )

        # Return the expense amount to the wallet
        if expense.status == ExpenseStatus.ACTIVE:
            wallet.current_balance += Decimal(
                str(expense.amount)
            )

        await self.expense_repository.delete(expense)