from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.wallet import Wallet
from app.repositories.wallet import WalletRepository
from app.schemas.wallet import (
    WalletCreate,
    WalletResponse,
    WalletUpdate,
)


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
    db: AsyncSession = Depends(get_db),
):
    repository = WalletRepository(db)

    wallet = Wallet(
        user_id=1,
        name=wallet_data.name,
        wallet_type=wallet_data.wallet_type,
        opening_balance=wallet_data.opening_balance,
        current_balance=wallet_data.opening_balance,
        currency=wallet_data.currency,
        status="ACTIVE",
    )

    return await repository.create(wallet)


# 2. GET ALL
@router.get("/")
async def get_wallets(
    db: AsyncSession = Depends(get_db),
):
    repository = WalletRepository(db)

    wallets = await repository.get_by_user(
        user_id=1
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
    db: AsyncSession = Depends(get_db),
):
    repository = WalletRepository(db)

    wallet = await repository.get_by_uuid(wallet_uuid)

    if not wallet:
        raise HTTPException(
            status_code=404,
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
    db: AsyncSession = Depends(get_db),
):
    repository = WalletRepository(db)

    wallet = await repository.get_by_uuid(wallet_uuid)

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found",
        )

    update_data = wallet_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(wallet, field, value)

    return await repository.update(wallet)

@router.delete(
    "/{wallet_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_wallet(
    wallet_uuid: UUID,
    db: AsyncSession = Depends(get_db),
):
    repository = WalletRepository(db)

    wallet = await repository.get_by_uuid(wallet_uuid)

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found",
        )

    await repository.delete(wallet)