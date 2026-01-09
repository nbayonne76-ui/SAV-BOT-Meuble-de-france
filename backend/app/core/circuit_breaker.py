# backend/app/core/circuit_breaker.py
"""
Circuit breaker pattern for external API calls.
Prevents cascading failures and provides graceful degradation.
"""
import asyncio
import functools
import logging
import time
from enum import Enum
from typing import Callable, Optional, Any, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, calls fail immediately
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Circuit breaker for external API calls.

    States:
    - CLOSED: Normal operation, calls pass through
    - OPEN: Too many failures, calls fail immediately
    - HALF_OPEN: Testing recovery, limited calls allowed

    Transitions:
    - CLOSED -> OPEN: After failure_threshold consecutive failures
    - OPEN -> HALF_OPEN: After recovery_timeout seconds
    - HALF_OPEN -> CLOSED: After success_threshold consecutive successes
    - HALF_OPEN -> OPEN: After any failure
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2,
        timeout: int = 30
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Name of the circuit (e.g., "openai", "cloudinary")
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before testing recovery
            success_threshold: Number of successes to close circuit from half-open
            timeout: Timeout for individual calls in seconds
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.timeout = timeout

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change: datetime = datetime.now()

        # Statistics
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0
        self.total_timeouts = 0

        logger.info(
            f"Circuit breaker '{name}' initialized: "
            f"failure_threshold={failure_threshold}, "
            f"recovery_timeout={recovery_timeout}s, "
            f"timeout={timeout}s"
        )

    def _can_attempt_call(self) -> bool:
        """Check if a call can be attempted based on current state."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.HALF_OPEN:
            return True

        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
                if time_since_failure >= self.recovery_timeout:
                    logger.info(f"Circuit '{self.name}' moving to HALF_OPEN (testing recovery)")
                    self._change_state(CircuitState.HALF_OPEN)
                    self.success_count = 0
                    return True

            return False

        return False

    def _change_state(self, new_state: CircuitState):
        """Change circuit state and log transition."""
        old_state = self.state
        self.state = new_state
        self.last_state_change = datetime.now()

        logger.warning(
            f"Circuit '{self.name}' state change: {old_state.value} -> {new_state.value} "
            f"(failures: {self.failure_count}, successes: {self.success_count})"
        )

    def _on_success(self):
        """Handle successful call."""
        self.total_calls += 1
        self.total_successes += 1

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                logger.info(
                    f"Circuit '{self.name}' recovered after {self.success_count} successes"
                )
                self._change_state(CircuitState.CLOSED)
                self.failure_count = 0
                self.success_count = 0

        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0

    def _on_failure(self, error: Exception):
        """Handle failed call."""
        self.total_calls += 1
        self.total_failures += 1
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        logger.error(
            f"Circuit '{self.name}' failure #{self.failure_count}: {type(error).__name__}: {str(error)}"
        )

        if self.state == CircuitState.HALF_OPEN:
            # Any failure in half-open state reopens the circuit
            logger.warning(f"Circuit '{self.name}' failed during recovery test, reopening")
            self._change_state(CircuitState.OPEN)
            self.success_count = 0

        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                logger.error(
                    f"Circuit '{self.name}' OPENED after {self.failure_count} consecutive failures"
                )
                self._change_state(CircuitState.OPEN)

    def _on_timeout(self):
        """Handle timeout."""
        self.total_timeouts += 1
        logger.warning(f"Circuit '{self.name}' call timed out after {self.timeout}s")

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function through the circuit breaker.

        Args:
            func: Async function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Original exception if call fails
        """
        if not self._can_attempt_call():
            raise CircuitBreakerError(
                f"Circuit breaker '{self.name}' is OPEN. "
                f"Service unavailable (last failure: {self.last_failure_time}). "
                f"Will retry after {self.recovery_timeout}s."
            )

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.timeout
            )
            self._on_success()
            return result

        except asyncio.TimeoutError:
            self._on_timeout()
            self._on_failure(Exception(f"Timeout after {self.timeout}s"))
            raise

        except Exception as e:
            self._on_failure(e)
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        uptime = (datetime.now() - self.last_state_change).total_seconds()

        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_calls": self.total_calls,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "total_timeouts": self.total_timeouts,
            "success_rate": (
                round(self.total_successes / self.total_calls * 100, 2)
                if self.total_calls > 0 else 0
            ),
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_state_change": self.last_state_change.isoformat(),
            "state_uptime_seconds": round(uptime, 2),
            "config": {
                "failure_threshold": self.failure_threshold,
                "recovery_timeout": self.recovery_timeout,
                "success_threshold": self.success_threshold,
                "timeout": self.timeout
            }
        }

    def reset(self):
        """Manually reset circuit to closed state."""
        logger.info(f"Circuit '{self.name}' manually reset to CLOSED")
        self._change_state(CircuitState.CLOSED)
        self.failure_count = 0
        self.success_count = 0


class CircuitBreakerManager:
    """
    Singleton manager for all circuit breakers.
    """

    _instance: Optional['CircuitBreakerManager'] = None
    _breakers: Dict[str, CircuitBreaker] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_breaker(
        cls,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2,
        timeout: int = 30
    ) -> CircuitBreaker:
        """
        Get or create a circuit breaker.

        Args:
            name: Circuit breaker name
            failure_threshold: Failures before opening
            recovery_timeout: Seconds before testing recovery
            success_threshold: Successes to close circuit
            timeout: Call timeout in seconds

        Returns:
            CircuitBreaker instance
        """
        instance = cls()

        if name not in instance._breakers:
            instance._breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                success_threshold=success_threshold,
                timeout=timeout
            )

        return instance._breakers[name]

    @classmethod
    def get_all_stats(cls) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers."""
        instance = cls()
        return {
            name: breaker.get_stats()
            for name, breaker in instance._breakers.items()
        }

    @classmethod
    def reset_all(cls):
        """Reset all circuit breakers."""
        instance = cls()
        for breaker in instance._breakers.values():
            breaker.reset()


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    success_threshold: int = 2,
    timeout: int = 30,
    fallback: Optional[Callable] = None
):
    """
    Decorator to add circuit breaker protection to async functions.

    Args:
        name: Circuit breaker name
        failure_threshold: Failures before opening circuit
        recovery_timeout: Seconds before testing recovery
        success_threshold: Successes to close circuit
        timeout: Call timeout in seconds
        fallback: Optional fallback function when circuit is open

    Usage:
        @circuit_breaker(name="openai", timeout=30, fallback=lambda: "Service unavailable")
        async def call_openai_api():
            # API call here
            pass
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            breaker = CircuitBreakerManager.get_breaker(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                success_threshold=success_threshold,
                timeout=timeout
            )

            try:
                return await breaker.call(func, *args, **kwargs)
            except CircuitBreakerError as e:
                logger.error(f"Circuit breaker prevented call: {e}")
                if fallback:
                    logger.info(f"Using fallback for '{name}'")
                    if asyncio.iscoroutinefunction(fallback):
                        return await fallback(*args, **kwargs)
                    else:
                        return fallback(*args, **kwargs)
                raise

        return wrapper
    return decorator


# Convenience function for getting breaker stats
def get_circuit_stats() -> Dict[str, Dict[str, Any]]:
    """Get statistics for all circuit breakers."""
    return CircuitBreakerManager.get_all_stats()


# Convenience function for resetting all breakers
def reset_all_circuits():
    """Reset all circuit breakers to closed state."""
    CircuitBreakerManager.reset_all()
