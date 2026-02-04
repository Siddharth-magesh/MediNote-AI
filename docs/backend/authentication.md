# Authentication System

## Overview
JWT-based authentication with support for email/password login and optional OAuth providers.

## Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Authentication Flow                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Registration:                                                       │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐          │
│  │  Form   │ →  │Validate │ →  │Hash Pwd │ →  │Create   │          │
│  │  Data   │    │ Input   │    │(bcrypt) │    │ User    │          │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘          │
│                                                      │               │
│                                                      ▼               │
│                                               ┌─────────┐           │
│                                               │  Send   │           │
│                                               │Verify   │           │
│                                               │ Email   │           │
│                                               └─────────┘           │
│                                                                      │
│  Login:                                                              │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐          │
│  │Email/Pwd│ →  │ Verify  │ →  │Generate │ →  │ Return  │          │
│  │ Input   │    │Password │    │  JWT    │    │ Tokens  │          │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘          │
│                                                                      │
│  Protected Request:                                                  │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐          │
│  │  API    │ →  │Extract  │ →  │ Verify  │ →  │ Process │          │
│  │ Request │    │  Token  │    │  JWT    │    │ Request │          │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Implementation

### Security Module
```python
# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": "access",
    }

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

def create_refresh_token(subject: str) -> str:
    """Create JWT refresh token (7 days)."""
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

def decode_token(token: str) -> Optional[dict]:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None
```

### User Schemas
```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=100)

class UserCreate(UserBase):
    password: str = Field(min_length=8)
    hospital_name: Optional[str] = None
    qualification: Optional[str] = None
    registration_number: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds

class TokenRefresh(BaseModel):
    refresh_token: str
```

### Auth Service
```python
# app/services/auth.py
from datetime import timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, TokenResponse
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.config import settings

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: UserCreate) -> User:
        """Register a new user."""
        # Check if email exists
        existing = await self._get_user_by_email(data.email)
        if existing:
            raise ValueError("Email already registered")

        # Create user
        user = User(
            email=data.email,
            name=data.name,
            hashed_password=get_password_hash(data.password),
            hospital_name=data.hospital_name,
            qualification=data.qualification,
            registration_number=data.registration_number,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # TODO: Send verification email

        return user

    async def login(self, data: UserLogin) -> TokenResponse:
        """Authenticate user and return tokens."""
        user = await self._get_user_by_email(data.email)

        if not user or not verify_password(data.password, user.hashed_password):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Account is disabled")

        # Generate tokens
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        payload = decode_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")

        user_id = payload.get("sub")
        user = await self.db.get(User, user_id)

        if not user or not user.is_active:
            raise ValueError("Invalid user")

        # Generate new tokens
        new_access_token = create_access_token(str(user.id))
        new_refresh_token = create_refresh_token(str(user.id))

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def _get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
```

### Auth Endpoints
```python
# app/api/v1/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import DBSession
from app.schemas.user import (
    UserCreate,
    UserResponse,
    TokenResponse,
    TokenRefresh,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: DBSession):
    """Register a new doctor account."""
    service = AuthService(db)
    try:
        user = await service.register(data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(
    db: DBSession,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """Login with email and password."""
    from app.schemas.user import UserLogin
    service = AuthService(db)
    try:
        tokens = await service.login(
            UserLogin(email=form_data.username, password=form_data.password)
        )
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: TokenRefresh, db: DBSession):
    """Refresh access token."""
    service = AuthService(db)
    try:
        tokens = await service.refresh_tokens(data.refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/logout")
async def logout():
    """Logout (client should discard tokens)."""
    return {"message": "Successfully logged out"}
```

## User Model

```python
# app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
import uuid

from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Doctor specific fields
    hospital_name = Column(String(255))
    qualification = Column(String(255))
    registration_number = Column(String(100))
    department = Column(String(100))
    signature_url = Column(String(500))

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

## Token Structure

### Access Token Payload
```json
{
  "sub": "user-uuid",
  "exp": 1704067200,
  "type": "access"
}
```

### Refresh Token Payload
```json
{
  "sub": "user-uuid",
  "exp": 1704672000,
  "type": "refresh"
}
```

## Security Best Practices

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Token Security
- Access tokens expire in 30 minutes
- Refresh tokens expire in 7 days
- Tokens are signed with HS256
- Secrets are stored in environment variables

### Rate Limiting
```python
# Implement rate limiting for auth endpoints
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login(...):
    ...
```

### Account Security
- Account lockout after 5 failed attempts
- Email verification required
- Password reset via email

## OAuth Integration (Optional)

### Google OAuth
```python
# app/services/oauth.py
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@router.get("/oauth/google")
async def google_login(request: Request):
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/oauth/google/callback")
async def google_callback(request: Request, db: DBSession):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get('userinfo')
    # Create or get user, return tokens
    ...
```

## Testing Auth

```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "name": "Test User",
        "password": "SecurePass123!",
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    # First register
    await client.post("/api/v1/auth/register", json={...})

    # Then login
    response = await client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "SecurePass123!",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## Related Documentation
- [Backend Architecture](./architecture.md)
- [API Documentation](../api/auth.md)
- [Security Guidelines](../security/overview.md)
