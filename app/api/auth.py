from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserStatus
from app.repositories.user import UserRepository
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserCreate,
)
from app.api.dependencies import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register")
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)

    existing_user = await repository.get_by_email(
        user_data.email
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        status=UserStatus.ACTIVE,
    )

    created_user = await repository.create(user)

    return {
        "message": "User registered successfully",
        "uuid": created_user.uuid,
        "email": created_user.email,
        "status": created_user.status,
    }

@router.post("/login")
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)

    user = await repository.get_by_email(
        login_data.email
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(
        login_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        str(user.uuid)
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )

@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "uuid": current_user.uuid,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "status": current_user.status,
    }