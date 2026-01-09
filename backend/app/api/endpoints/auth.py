# backend/app/api/endpoints/auth.py
"""
Authentication endpoints for login, logout, registration, and token management
"""
from datetime import datetime, timedelta
from typing import Optional
import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from pydantic import BaseModel

from app.db.session import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    Token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    generate_api_key,
    hash_api_key,
    blacklist_token
)
from app.models.user import (
    UserDB,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    PasswordChange,
    UserRole,
    UserStatus,
    APIKeyDB,
    APIKeyCreate,
    APIKeyResponse
)
from app.api.deps import get_current_active_user, require_admin
from app.core.rate_limit import limiter, RateLimits

logger = logging.getLogger(__name__)
router = APIRouter()

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

# Constants
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh"""
    refresh_token: str


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str
    success: bool = True


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.AUTH_REGISTER)
async def register(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.
    Rate limited to prevent abuse.
    """
    # Check if email already exists
    result = await db.execute(select(UserDB).where(UserDB.email == user_data.email))
    existing_email = result.scalar_one_or_none()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    result = await db.execute(select(UserDB).where(UserDB.username == user_data.username.lower()))
    existing_username = result.scalar_one_or_none()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create new user
    new_user = UserDB(
        id=str(uuid.uuid4()),
        email=user_data.email,
        username=user_data.username.lower(),
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        status=UserStatus.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(f"New user registered: {new_user.username} ({new_user.email})")

    return new_user.to_response()


@router.post("/login", response_model=Token)
@limiter.limit(RateLimits.AUTH_LOGIN)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible login endpoint.
    Returns access and refresh tokens.
    Rate limited to prevent brute force attacks.
    """
    # Find user by username or email
    result = await db.execute(
        select(UserDB).where(
            or_(
                UserDB.username == form_data.username.lower(),
                UserDB.email == form_data.username
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"Login failed: user not found - {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        remaining = (user.locked_until - datetime.utcnow()).seconds // 60
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked. Try again in {remaining} minutes."
        )

    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        # Increment failed attempts
        user.failed_login_attempts += 1

        # Lock account if too many attempts
        if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            await db.commit()
            logger.warning(f"Account locked due to failed attempts: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account locked for {LOCKOUT_DURATION_MINUTES} minutes due to too many failed attempts"
            )

        await db.commit()
        logger.warning(f"Login failed: wrong password - {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check user status
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.status.value}"
        )

    # Reset failed attempts and update last login
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    await db.commit()

    # Generate tokens
    access_token = create_access_token(
        subject=user.id,
        scopes=[user.role.value]
    )
    refresh_token = create_refresh_token(subject=user.id)

    logger.info(f"User logged in: {user.username}")

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=Token)
@limiter.limit(RateLimits.AUTH_LOGIN)
async def refresh_token(
    request: Request,
    token_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using a valid refresh token.
    The old refresh token is blacklisted to prevent reuse.
    Rate limited to prevent token enumeration attacks.
    """
    token_data = verify_token(token_request.refresh_token, token_type="refresh")

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user
    result = await db.execute(select(UserDB).where(UserDB.id == token_data.user_id))
    user = result.scalar_one_or_none()
    if not user or user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Blacklist the old refresh token to prevent replay attacks
    try:
        await blacklist_token(token_request.refresh_token)
        logger.info(f"Old refresh token blacklisted for user: {user.username}")
    except Exception as e:
        logger.error(f"Failed to blacklist old refresh token: {e}")
        # Continue anyway - security is defense in depth

    # Generate new tokens
    access_token = create_access_token(
        subject=user.id,
        scopes=[user.role.value]
    )
    new_refresh_token = create_refresh_token(subject=user.id)

    logger.info(f"Tokens refreshed for user: {user.username}")

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: UserDB = Depends(get_current_active_user),
    token: Optional[str] = Depends(oauth2_scheme)
):
    """
    Logout current user and blacklist their access token.
    The token will be invalidated until its natural expiration.
    Client should also delete the token locally.
    """
    # Blacklist the access token
    if token:
        try:
            await blacklist_token(token)
            logger.info(f"✅ User logged out and token blacklisted: {current_user.username}")
        except Exception as e:
            logger.error(f"Failed to blacklist token on logout: {e}")
            # Still log out the user even if blacklisting fails
    else:
        logger.info(f"User logged out: {current_user.username}")

    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserDB = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.
    """
    return current_user.to_response()


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: UserDB = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user profile.
    """
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name

    if user_data.email is not None:
        # Check if email is already taken by another user
        result = await db.execute(
            select(UserDB).where(
                UserDB.email == user_data.email,
                UserDB.id != current_user.id
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        current_user.email = user_data.email

    current_user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)

    logger.info(f"User updated profile: {current_user.username}")

    return current_user.to_response()


@router.post("/me/change-password", response_model=MessageResponse)
@limiter.limit(RateLimits.AUTH_PASSWORD_RESET)
async def change_password(
    request: Request,
    password_data: PasswordChange,
    current_user: UserDB = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change current user's password.
    Rate limited to prevent brute force attacks.
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    await db.commit()

    logger.info(f"User changed password: {current_user.username}")

    return MessageResponse(message="Password changed successfully")


# ============== API Key Management ==============

@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.API_WRITE)
async def create_api_key(
    request: Request,
    key_data: APIKeyCreate,
    current_user: UserDB = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new API key for the current user.
    The key is only shown once in this response.
    Rate limited to prevent abuse.
    """
    # Generate API key
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)

    # Create record
    api_key_record = APIKeyDB(
        id=str(uuid.uuid4()),
        name=key_data.name,
        key_hash=key_hash,
        user_id=current_user.id,
        scopes=",".join(key_data.scopes),
        created_at=datetime.utcnow(),
        is_active=1
    )

    db.add(api_key_record)
    await db.commit()

    logger.info(f"API key created: {key_data.name} for user {current_user.username}")

    return APIKeyResponse(
        id=api_key_record.id,
        name=api_key_record.name,
        key=api_key,  # Only shown once!
        scopes=key_data.scopes,
        created_at=api_key_record.created_at
    )


@router.delete("/api-keys/{key_id}", response_model=MessageResponse)
@limiter.limit(RateLimits.API_WRITE)
async def revoke_api_key(
    request: Request,
    key_id: str,
    current_user: UserDB = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke an API key.
    Rate limited to prevent abuse.
    """
    result = await db.execute(
        select(APIKeyDB).where(
            APIKeyDB.id == key_id,
            APIKeyDB.user_id == current_user.id
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    api_key.is_active = 0
    await db.commit()

    logger.info(f"API key revoked: {api_key.name}")

    return MessageResponse(message="API key revoked successfully")


# ============== Admin Endpoints ==============

@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserDB = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List all users (admin only).
    """
    result = await db.execute(select(UserDB).offset(skip).limit(limit))
    users = result.scalars().all()
    return [u.to_response() for u in users]


@router.put("/users/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: str,
    new_status: UserStatus,
    current_user: UserDB = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a user's status (admin only).
    """
    result = await db.execute(select(UserDB).where(UserDB.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.status = new_status
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)

    logger.info(f"Admin {current_user.username} changed user {user.username} status to {new_status.value}")

    return user.to_response()
