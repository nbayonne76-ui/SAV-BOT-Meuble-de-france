# backend/app/core/redis.py
"""
Redis connection manager for session storage and caching.
Supports fallback to in-memory storage for development.
"""
import asyncio
import json
import logging
from typing import Any, Optional, Dict
from datetime import timedelta
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseCache(ABC):
    """Abstract base class for cache implementations."""

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get a value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set a value in cache with optional expiration in seconds."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        pass

    @abstractmethod
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on a key."""
        pass

    @abstractmethod
    async def ttl(self, key: str) -> int:
        """Get time-to-live for a key."""
        pass

    @abstractmethod
    async def keys(self, pattern: str) -> list:
        """Get keys matching a pattern."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the connection."""
        pass

    @abstractmethod
    async def ping(self) -> bool:
        """Check if the connection is alive."""
        pass


class MemoryCache(BaseCache):
    """
    In-memory cache implementation for development.
    NOT suitable for production use with multiple workers.
    """

    def __init__(self):
        self._data: Dict[str, str] = {}
        self._expiry: Dict[str, float] = {}
        self._lock = asyncio.Lock()
        logger.info("Using in-memory cache (development mode)")

    async def _cleanup_expired(self):
        """Remove expired keys."""
        import time
        current_time = time.time()
        expired_keys = [
            key for key, expiry in self._expiry.items()
            if expiry and current_time > expiry
        ]
        for key in expired_keys:
            self._data.pop(key, None)
            self._expiry.pop(key, None)

    async def get(self, key: str) -> Optional[str]:
        async with self._lock:
            await self._cleanup_expired()
            return self._data.get(key)

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        import time
        async with self._lock:
            self._data[key] = value
            if expire:
                self._expiry[key] = time.time() + expire
            else:
                self._expiry.pop(key, None)
            return True

    async def delete(self, key: str) -> bool:
        async with self._lock:
            deleted = key in self._data
            self._data.pop(key, None)
            self._expiry.pop(key, None)
            return deleted

    async def exists(self, key: str) -> bool:
        async with self._lock:
            await self._cleanup_expired()
            return key in self._data

    async def expire(self, key: str, seconds: int) -> bool:
        import time
        async with self._lock:
            if key in self._data:
                self._expiry[key] = time.time() + seconds
                return True
            return False

    async def ttl(self, key: str) -> int:
        import time
        async with self._lock:
            if key not in self._expiry:
                return -1  # No expiry set
            if key not in self._data:
                return -2  # Key doesn't exist
            remaining = int(self._expiry[key] - time.time())
            return max(0, remaining)

    async def keys(self, pattern: str) -> list:
        import fnmatch
        async with self._lock:
            await self._cleanup_expired()
            # Convert Redis pattern to fnmatch pattern
            fnmatch_pattern = pattern.replace('*', '*')
            return [k for k in self._data.keys() if fnmatch.fnmatch(k, fnmatch_pattern)]

    async def close(self) -> None:
        async with self._lock:
            self._data.clear()
            self._expiry.clear()

    async def ping(self) -> bool:
        return True


class RedisCache(BaseCache):
    """
    Redis cache implementation for production.
    Uses redis-py async client.
    """

    def __init__(self, url: str):
        self._url = url
        self._client = None
        logger.info(f"Connecting to Redis: {url.split('@')[-1] if '@' in url else url}")

    async def _get_client(self):
        """Lazy initialization of Redis client."""
        if self._client is None:
            import redis.asyncio as redis
            self._client = redis.from_url(
                self._url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
                retry_on_timeout=True,
            )
        return self._client

    async def get(self, key: str) -> Optional[str]:
        try:
            client = await self._get_client()
            return await client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        try:
            client = await self._get_client()
            if expire:
                await client.setex(key, expire, value)
            else:
                await client.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            client = await self._get_client()
            result = await client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False

    async def exists(self, key: str) -> bool:
        try:
            client = await self._get_client()
            return await client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        try:
            client = await self._get_client()
            return await client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis EXPIRE error: {e}")
            return False

    async def ttl(self, key: str) -> int:
        try:
            client = await self._get_client()
            return await client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error: {e}")
            return -2

    async def keys(self, pattern: str) -> list:
        try:
            client = await self._get_client()
            return await client.keys(pattern)
        except Exception as e:
            logger.error(f"Redis KEYS error: {e}")
            return []

    async def close(self) -> None:
        if self._client:
            try:
                await self._client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
            finally:
                self._client = None

    async def ping(self) -> bool:
        try:
            client = await self._get_client()
            return await client.ping()
        except Exception as e:
            logger.error(f"Redis PING error: {e}")
            return False


class CacheManager:
    """
    Singleton cache manager that provides the appropriate cache implementation
    based on configuration.
    """

    _instance: Optional['CacheManager'] = None
    _cache: Optional[BaseCache] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls, redis_url: str) -> 'CacheManager':
        """
        Initialize the cache manager with the given Redis URL.

        Args:
            redis_url: Redis connection URL or 'memory://' for in-memory cache

        Returns:
            CacheManager instance
        """
        instance = cls()

        if redis_url.startswith("memory://"):
            instance._cache = MemoryCache()
        else:
            instance._cache = RedisCache(redis_url)

        return instance

    @classmethod
    def get_cache(cls) -> BaseCache:
        """
        Get the cache instance.

        Returns:
            BaseCache instance

        Raises:
            RuntimeError: If cache is not initialized
        """
        instance = cls()
        if instance._cache is None:
            raise RuntimeError(
                "Cache not initialized. Call CacheManager.initialize() first."
            )
        return instance._cache

    @classmethod
    async def close(cls):
        """Close the cache connection."""
        instance = cls()
        if instance._cache:
            await instance._cache.close()
            instance._cache = None


# Convenience function for getting the cache
def get_cache() -> BaseCache:
    """Get the cache instance."""
    return CacheManager.get_cache()


# JSON helpers for storing complex objects
async def cache_get_json(key: str) -> Optional[Any]:
    """Get a JSON value from cache."""
    cache = get_cache()
    value = await cache.get(key)
    if value:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None
    return None


async def cache_set_json(key: str, value: Any, expire: Optional[int] = None) -> bool:
    """Set a JSON value in cache."""
    cache = get_cache()
    try:
        json_str = json.dumps(value, default=str)
        return await cache.set(key, json_str, expire)
    except (TypeError, ValueError) as e:
        logger.error(f"Failed to serialize value to JSON: {e}")
        return False
