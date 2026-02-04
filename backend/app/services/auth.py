"""Authentication service."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.models.user import User
from app.schemas.auth import Token, UserRegister


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: UserRegister) -> User:
        """Register a new user."""
        # Check if email already exists
        existing = await self.get_user_by_email(data.email)
        if existing:
            raise ValueError("Email already registered")

        # Create user
        user = User(
            email=data.email,
            hashed_password=get_password_hash(data.password),
            name=data.name,
            phone=data.phone,
            hospital_name=data.hospital_name,
            qualification=data.qualification,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    def create_tokens(self, user: User) -> Token:
        """Create access and refresh tokens for a user."""
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh_tokens(self, refresh_token: str) -> Optional[Token]:
        """Refresh access token using refresh token."""
        user_id = verify_token(refresh_token, token_type="refresh")
        if user_id is None:
            return None

        user = await self.get_user_by_id(UUID(user_id))
        if user is None or not user.is_active:
            return None

        return self.create_tokens(user)

    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> bool:
        """Change user password."""
        if not verify_password(current_password, user.hashed_password):
            return False

        user.hashed_password = get_password_hash(new_password)
        await self.db.commit()

        return True
