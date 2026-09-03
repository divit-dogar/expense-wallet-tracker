from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.wallet import Wallet
from app.repositories.wallet import WalletRepository
from app.repositories.expense import ExpenseRepository
from app.schemas.wallet import (
    WalletCreate,
    WalletResponse,
    WalletUpdate,
)
from app.services.wallet_service import WalletService


router = APIRouter(
    prefix="/wallets",
    tags=["Wallets"],
)


# 1. CREATE
@router.post(
    "/",
    response_model=WalletResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_wallet(
    wallet_data: WalletCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WalletService(db)

    wallet = Wallet(
        user_id=current_user.id,
        name=wallet_data.name,
        wallet_type=wallet_data.wallet_type,
        opening_balance=wallet_data.opening_balance,
        current_balance=wallet_data.opening_balance,
        currency=wallet_data.currency,
        status="ACTIVE",
    )

    return await service.create_wallet(wallet)


# 2. GET ALL
@router.get("/")
async def get_wallets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repository = WalletRepository(db)

    wallets = await repository.get_by_user(
        user_id=current_user.id
    )

    total_balance = sum(
        wallet.current_balance
        for wallet in wallets
    )

    return {
        "wallets": wallets,
        "total_balance": total_balance,
    }


# 3. GET ONE
@router.get(
    "/{wallet_uuid}",
    response_model=WalletResponse,
)
async def get_wallet(
    wallet_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repository = WalletRepository(db)

    wallet = await repository.get_by_uuid(
        wallet_uuid
    )

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    if wallet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    return wallet


# 4. UPDATE
@router.patch(
    "/{wallet_uuid}",
    response_model=WalletResponse,
)
async def update_wallet(
    wallet_uuid: UUID,
    wallet_data: WalletUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repository = WalletRepository(db)

    wallet = await repository.get_by_uuid(
        wallet_uuid
    )

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    if wallet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    update_data = wallet_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(wallet, field, value)

    return await repository.update(wallet)


# 5. DELETE
@router.delete(
    "/{wallet_uuid}",
    status_code=status.HTTP_200_OK,
)
async def delete_wallet(
    wallet_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repository = WalletRepository(db)

    wallet = await repository.get_by_uuid(
        wallet_uuid
    )

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    if wallet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    expense_repository = ExpenseRepository(db)

    has_expenses = await expense_repository.exists_by_wallet(
        wallet_id=wallet.id
    )

    if has_expenses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete wallet because it has associated expenses",
        )

    await repository.delete(wallet)

    return {
        "message": "Wallet deleted successfully"
    }