"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.api.deps import CurrentUser, DBSession
from app.schemas.auth import (
    PasswordChange,
    RefreshToken,
    Token,
    UserRegister,
)
from app.schemas.user import UserResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister,
    db: DBSession,
):
    """
    Register a new user (doctor).

    - **email**: Valid email address (must be unique)
    - **password**: Password (min 8 chars, must include uppercase, lowercase, digit, special char)
    - **name**: Full name
    - **phone**: Phone number (optional)
    - **hospital_name**: Hospital/clinic name (optional)
    - **qualification**: Medical qualification (optional)
    """
    service = AuthService(db)
    try:
        user = await service.register(data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSession,
):
    """
    Login with email and password.

    Returns JWT access and refresh tokens.
    """
    service = AuthService(db)
    user = await service.authenticate(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return service.create_tokens(user)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    data: RefreshToken,
    db: DBSession,
):
    """
    Refresh access token using refresh token.
    """
    service = AuthService(db)
    tokens = await service.refresh_tokens(data.refresh_token)

    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUser,
):
    """
    Get current authenticated user information.
    """
    return current_user


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    data: PasswordChange,
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Change password for current user.
    """
    service = AuthService(db)
    success = await service.change_password(
        user=current_user,
        current_password=data.current_password,
        new_password=data.new_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    return {"message": "Password changed successfully"}
