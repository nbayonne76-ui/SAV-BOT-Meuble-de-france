# backend/app/core/cache_decorators.py
"""
Cache decorators for frequently accessed data
"""
import functools
import logging
import json
import hashlib
from typing import Optional, Callable, Any
from app.core.redis import get_cache

logger = logging.getLogger(__name__)


def cache_key(*args, **kwargs) -> str:
    """
    Generate a cache key from function arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Hash-based cache key
    """
    # Create a deterministic string from arguments
    key_parts = []

    # Add positional args (skip self/cls if method)
    for arg in args:
        if hasattr(arg, '__name__'):  # Skip self/cls
            continue
        key_parts.append(str(arg))

    # Add keyword args
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")

    # Create hash
    key_string = ":".join(key_parts)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()[:16]

    return key_hash


def cached(
    prefix: str,
    ttl: int = 300,  # 5 minutes default
    key_builder: Optional[Callable] = None
):
    """
    Decorator to cache async function results.

    Args:
        prefix: Cache key prefix (e.g., "user", "ticket")
        ttl: Time-to-live in seconds
        key_builder: Optional custom key builder function

    Usage:
        @cached(prefix="user", ttl=600)
        async def get_user_by_id(db: AsyncSession, user_id: str):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                key_suffix = key_builder(*args, **kwargs)
            else:
                key_suffix = cache_key(*args[1:], **kwargs)  # Skip first arg (usually db session)

            full_key = f"cache:{prefix}:{key_suffix}"

            # Try to get from cache
            try:
                cache = get_cache()
                cached_value = await cache.get(full_key)

                if cached_value:
                    logger.debug(f"Cache HIT: {full_key}")
                    try:
                        return json.loads(cached_value)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to deserialize cached value for {full_key}")
            except Exception as e:
                logger.error(f"Cache GET error: {e}")

            # Cache miss - call the function
            logger.debug(f"Cache MISS: {full_key}")
            result = await func(*args, **kwargs)

            # Store in cache
            if result is not None:
                try:
                    cache = get_cache()
                    # Serialize result
                    if hasattr(result, '__dict__'):
                        # SQLAlchemy model or dataclass
                        cache_value = json.dumps(result.__dict__, default=str)
                    else:
                        cache_value = json.dumps(result, default=str)

                    await cache.set(full_key, cache_value, expire=ttl)
                    logger.debug(f"Cached: {full_key} (TTL: {ttl}s)")
                except Exception as e:
                    logger.error(f"Cache SET error: {e}")

            return result

        return wrapper
    return decorator


def invalidate_cache(prefix: str, *keys):
    """
    Decorator to invalidate cache entries after a function call.

    Args:
        prefix: Cache key prefix
        *keys: Key patterns to invalidate

    Usage:
        @invalidate_cache("user", "user:*", "users:list")
        async def update_user(db: AsyncSession, user_id: str, data: dict):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Call the function first
            result = await func(*args, **kwargs)

            # Invalidate cache entries
            try:
                cache = get_cache()

                for pattern in keys:
                    # If pattern contains wildcard, get all matching keys
                    if '*' in pattern:
                        matching_keys = await cache.keys(f"cache:{prefix}:{pattern}")
                        for key in matching_keys:
                            await cache.delete(key)
                            logger.debug(f"Invalidated cache: {key}")
                    else:
                        # Direct key deletion
                        full_key = f"cache:{prefix}:{pattern}"
                        await cache.delete(full_key)
                        logger.debug(f"Invalidated cache: {full_key}")

            except Exception as e:
                logger.error(f"Cache invalidation error: {e}")

            return result

        return wrapper
    return decorator


# Convenience functions for manual cache operations

async def get_cached(prefix: str, key: str) -> Optional[Any]:
    """
    Manually get a cached value.

    Args:
        prefix: Cache key prefix
        key: Cache key suffix

    Returns:
        Cached value or None
    """
    try:
        cache = get_cache()
        full_key = f"cache:{prefix}:{key}"
        value = await cache.get(full_key)

        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    except Exception as e:
        logger.error(f"get_cached error: {e}")
        return None


async def set_cached(prefix: str, key: str, value: Any, ttl: int = 300) -> bool:
    """
    Manually set a cached value.

    Args:
        prefix: Cache key prefix
        key: Cache key suffix
        value: Value to cache
        ttl: Time-to-live in seconds

    Returns:
        True if successful
    """
    try:
        cache = get_cache()
        full_key = f"cache:{prefix}:{key}"

        if hasattr(value, '__dict__'):
            cache_value = json.dumps(value.__dict__, default=str)
        else:
            cache_value = json.dumps(value, default=str)

        return await cache.set(full_key, cache_value, expire=ttl)
    except Exception as e:
        logger.error(f"set_cached error: {e}")
        return False


async def delete_cached(prefix: str, key: str) -> bool:
    """
    Manually delete a cached value.

    Args:
        prefix: Cache key prefix
        key: Cache key suffix

    Returns:
        True if successful
    """
    try:
        cache = get_cache()
        full_key = f"cache:{prefix}:{key}"
        return await cache.delete(full_key)
    except Exception as e:
        logger.error(f"delete_cached error: {e}")
        return False
