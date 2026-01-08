# backend/app/api/deps.py
"""
API Dependencies for authentication and authorization
"""
from datetime import datetime
from typing import Optional, List
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from sqlalchemy.orm import Session

from app.core.security import verify_token_with_blacklist, TokenData, verify_api_key
from app.db.session import get_db
from app.models.user import UserDB, UserRole, UserStatus, APIKeyDB

# OAuth2 scheme for JWT authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False  # Don't auto-error, we handle it manually
)

# API Key header scheme
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)


async def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(api_key_header)
) -> Optional[UserDB]:
    """
    Get current authenticated user from JWT token or API key.
    Returns None if no authentication provided.
    Checks token blacklist for revoked tokens.
    """
    # Try JWT token first
    if token:
        # Verify token and check blacklist
        token_data = await verify_token_with_blacklist(token, token_type="access")
        if token_data:
            user = db.query(UserDB).filter(UserDB.id == token_data.user_id).first()
            if user and user.status == UserStatus.ACTIVE:
                return user

    # Try API key
    if api_key:
        # Find API key in database
        api_key_record = db.query(APIKeyDB).filter(APIKeyDB.is_active == 1).all()
        for record in api_key_record:
            if verify_api_key(api_key, record.key_hash):
                # Update last used
                record.last_used = datetime.utcnow()
                db.commit()
                # Get associated user
                user = db.query(UserDB).filter(UserDB.id == record.user_id).first()
                if user and user.status == UserStatus.ACTIVE:
                    return user

    return None


async def get_current_user_required(
    current_user: Optional[UserDB] = Depends(get_current_user)
) -> UserDB:
    """
    Require authenticated user. Raises 401 if not authenticated.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def get_current_active_user(
    current_user: UserDB = Depends(get_current_user_required)
) -> UserDB:
    """
    Get current active user. Raises 403 if user is inactive/suspended.
    """
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {current_user.status.value}"
        )

    # Check if account is locked
    if current_user.locked_until and current_user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked due to too many failed login attempts"
        )

    return current_user


def require_roles(allowed_roles: List[UserRole]):
    """
    Dependency factory to require specific roles.

    Usage:
        @router.get("/admin")
        async def admin_endpoint(user: UserDB = Depends(require_roles([UserRole.ADMIN]))):
            ...
    """
    async def role_checker(
        current_user: UserDB = Depends(get_current_active_user)
    ) -> UserDB:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user

    return role_checker


# Pre-built role dependencies
require_admin = require_roles([UserRole.ADMIN])
require_agent = require_roles([UserRole.ADMIN, UserRole.AGENT])
require_customer = require_roles([UserRole.ADMIN, UserRole.AGENT, UserRole.CUSTOMER])


class OptionalAuth:
    """
    Optional authentication dependency.
    Returns user if authenticated, None otherwise.
    Useful for endpoints that work differently for authenticated users.
    """

    async def __call__(
        self,
        current_user: Optional[UserDB] = Depends(get_current_user)
    ) -> Optional[UserDB]:
        return current_user


optional_auth = OptionalAuth()
