# backend/app/core/security.py
"""
Security utilities for JWT authentication and password hashing
"""
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import secrets

from app.core.config import settings

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[str] = None
    username: Optional[str] = None
    scopes: list[str] = []


class Token(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str
    exp: datetime
    type: str  # "access" or "refresh"
    scopes: list[str] = []


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, int],
    scopes: list[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token

    Args:
        subject: The subject (usually user_id or username)
        scopes: List of permission scopes
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "access",
        "scopes": scopes or [],
        "iat": datetime.utcnow()
    }

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token

    Args:
        subject: The subject (usually user_id or username)
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT refresh token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(32)  # Unique token ID for revocation
    }

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenPayload]:
    """
    Decode and validate a JWT token

    Args:
        token: The JWT token string

    Returns:
        TokenPayload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(
            sub=payload.get("sub"),
            exp=datetime.fromtimestamp(payload.get("exp")),
            type=payload.get("type", "access"),
            scopes=payload.get("scopes", [])
        )
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    """
    Verify a JWT token and return token data

    Args:
        token: The JWT token string
        token_type: Expected token type ("access" or "refresh")

    Returns:
        TokenData if valid, None otherwise
    """
    payload = decode_token(token)
    if payload is None:
        return None

    if payload.type != token_type:
        return None

    if payload.exp < datetime.utcnow():
        return None

    return TokenData(
        user_id=payload.sub,
        username=payload.sub,
        scopes=payload.scopes
    )


def generate_api_key() -> str:
    """Generate a secure API key for service-to-service auth"""
    return f"mdf_{secrets.token_urlsafe(32)}"


def verify_api_key(api_key: str, stored_key_hash: str) -> bool:
    """Verify an API key against its stored hash"""
    return pwd_context.verify(api_key, stored_key_hash)


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage"""
    return pwd_context.hash(api_key)


# ===== TOKEN REVOCATION (Redis Blacklist) =====

async def revoke_token(token: str) -> bool:
    """
    Revoke a JWT token by adding it to Redis blacklist

    Args:
        token: The JWT token to revoke

    Returns:
        True if revoked successfully, False otherwise
    """
    try:
        from app.core.redis import get_cache

        # Decode token to get expiration
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        exp = datetime.fromtimestamp(payload.get("exp"))

        # Calculate remaining TTL in seconds
        remaining_ttl = int((exp - datetime.utcnow()).total_seconds())

        # Only store if token hasn't expired yet
        if remaining_ttl > 0:
            cache = get_cache()
            # Store in Redis with TTL matching token expiration
            await cache.set(f"revoked_token:{token}", "1", expire=remaining_ttl)
            return True

        return False
    except Exception as e:
        # Log error but don't fail - worst case, token stays valid until expiry
        import logging
        logging.error(f"Failed to revoke token: {e}")
        return False


async def is_token_revoked(token: str) -> bool:
    """
    Check if a JWT token has been revoked

    Args:
        token: The JWT token to check

    Returns:
        True if token is revoked, False otherwise
    """
    try:
        from app.core.redis import get_cache

        cache = get_cache()
        result = await cache.get(f"revoked_token:{token}")
        return result is not None
    except Exception as e:
        # If Redis is down, fail open (allow access)
        # This prevents Redis outage from locking out all users
        import logging
        logging.error(f"Failed to check token revocation: {e}")
        return False


async def revoke_user_tokens(user_id: str) -> bool:
    """
    Revoke all tokens for a specific user
    This is useful when forcing logout or account suspension

    Args:
        user_id: The user ID whose tokens should be revoked

    Returns:
        True if operation succeeded
    """
    try:
        from app.core.redis import get_cache

        cache = get_cache()
        # Store a user-level revocation flag
        # Valid for max refresh token expiration time
        expire_seconds = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        await cache.set(f"revoked_user:{user_id}", "1", expire=expire_seconds)
        return True
    except Exception as e:
        import logging
        logging.error(f"Failed to revoke user tokens: {e}")
        return False


async def is_user_tokens_revoked(user_id: str) -> bool:
    """
    Check if all tokens for a user have been revoked

    Args:
        user_id: The user ID to check

    Returns:
        True if all user tokens are revoked
    """
    try:
        from app.core.redis import get_cache

        cache = get_cache()
        result = await cache.get(f"revoked_user:{user_id}")
        return result is not None
    except Exception as e:
        import logging
        logging.error(f"Failed to check user token revocation: {e}")
        return False
