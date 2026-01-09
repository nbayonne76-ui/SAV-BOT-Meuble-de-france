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
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

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
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(32)  # Unique token ID for revocation
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


# ============== JWT Token Blacklist ==============

async def blacklist_token(token: str) -> bool:
    """
    Add a token to the blacklist.
    Token will be blacklisted until its natural expiration.

    Args:
        token: The JWT token string to blacklist

    Returns:
        True if successfully blacklisted, False otherwise
    """
    try:
        from app.core.redis import get_cache

        # Decode token to get expiration and jti
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti:
            logger.warning("Cannot blacklist token without jti")
            return False

        # Calculate TTL (time until token expires)
        exp_datetime = datetime.fromtimestamp(exp)
        ttl_seconds = int((exp_datetime - datetime.utcnow()).total_seconds())

        if ttl_seconds <= 0:
            # Token already expired, no need to blacklist
            return True

        # Store in cache with expiration
        cache = get_cache()
        key = f"blacklist:token:{jti}"
        await cache.set(key, "revoked", expire=ttl_seconds)

        logger.info(f"Token blacklisted: {jti[:16]}... (TTL: {ttl_seconds}s)")
        return True

    except JWTError as e:
        logger.error(f"Failed to decode token for blacklisting: {e}")
        return False
    except Exception as e:
        logger.error(f"Error blacklisting token: {e}")
        return False


async def is_token_blacklisted(token: str) -> bool:
    """
    Check if a token is blacklisted.

    Args:
        token: The JWT token string to check

    Returns:
        True if token is blacklisted, False otherwise
    """
    try:
        from app.core.redis import get_cache

        # Decode token to get jti
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")

        if not jti:
            # Old tokens without jti cannot be blacklisted
            # Consider them valid (or update all tokens to have jti)
            return False

        # Check cache
        cache = get_cache()
        key = f"blacklist:token:{jti}"
        return await cache.exists(key)

    except JWTError:
        # If token is invalid, treat as blacklisted
        return True
    except Exception as e:
        logger.error(f"Error checking token blacklist: {e}")
        # Fail secure: treat as blacklisted on error
        return True


async def verify_token_with_blacklist(token: str, token_type: str = "access") -> Optional[TokenData]:
    """
    Verify a JWT token and check if it's blacklisted.

    Args:
        token: The JWT token string
        token_type: Expected token type ("access" or "refresh")

    Returns:
        TokenData if valid and not blacklisted, None otherwise
    """
    # First check if token is blacklisted
    if await is_token_blacklisted(token):
        logger.warning("Attempted use of blacklisted token")
        return None

    # Then do standard token verification
    return verify_token(token, token_type)
