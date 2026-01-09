# backend/app/core/slow_query_logger.py
"""
Slow query logging for performance monitoring.
Tracks database query execution time and logs slow queries.
"""
import logging
import time
from typing import Any
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import settings

logger = logging.getLogger(__name__)


class SlowQueryLogger:
    """
    SQLAlchemy event listener for tracking slow queries.
    Logs queries that exceed the configured threshold.
    """

    def __init__(self, threshold_ms: int = 1000):
        """
        Initialize slow query logger.

        Args:
            threshold_ms: Threshold in milliseconds - queries slower than this are logged
        """
        self.threshold_ms = threshold_ms
        self.query_count = 0
        self.slow_query_count = 0
        self.total_query_time_ms = 0.0

    def before_cursor_execute(
        self,
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool
    ):
        """
        Event listener called before query execution.
        Records the start time for measuring execution duration.
        """
        conn.info.setdefault("query_start_time", []).append(time.time())

    def after_cursor_execute(
        self,
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool
    ):
        """
        Event listener called after query execution.
        Calculates execution time and logs if it exceeds threshold.
        """
        total_time = time.time() - conn.info["query_start_time"].pop()
        total_time_ms = total_time * 1000

        # Update statistics
        self.query_count += 1
        self.total_query_time_ms += total_time_ms

        # Log slow queries
        if total_time_ms > self.threshold_ms:
            self.slow_query_count += 1

            # Clean up the query for logging (remove extra whitespace)
            clean_query = " ".join(statement.split())

            # Truncate very long queries
            if len(clean_query) > 500:
                clean_query = clean_query[:500] + "..."

            # Format parameters for logging (truncate if too long)
            params_str = str(parameters)
            if len(params_str) > 200:
                params_str = params_str[:200] + "..."

            logger.warning(
                f"SLOW QUERY [{total_time_ms:.2f}ms] "
                f"(threshold: {self.threshold_ms}ms)\n"
                f"Query: {clean_query}\n"
                f"Params: {params_str}\n"
                f"Stats: {self.slow_query_count}/{self.query_count} queries slow "
                f"({(self.slow_query_count/self.query_count*100):.1f}%)"
            )

    def get_stats(self) -> dict:
        """
        Get query performance statistics.

        Returns:
            Dictionary with query statistics
        """
        avg_query_time = (
            self.total_query_time_ms / self.query_count
            if self.query_count > 0 else 0
        )

        slow_query_percentage = (
            (self.slow_query_count / self.query_count * 100)
            if self.query_count > 0 else 0
        )

        return {
            "total_queries": self.query_count,
            "slow_queries": self.slow_query_count,
            "slow_query_percentage": round(slow_query_percentage, 2),
            "average_query_time_ms": round(avg_query_time, 2),
            "total_query_time_ms": round(self.total_query_time_ms, 2),
            "threshold_ms": self.threshold_ms
        }


# Global slow query logger instance
_slow_query_logger: SlowQueryLogger = None


def setup_slow_query_logging(engine: Engine | AsyncEngine, threshold_ms: int = None):
    """
    Setup slow query logging for a SQLAlchemy engine.

    Args:
        engine: SQLAlchemy engine (sync or async)
        threshold_ms: Optional threshold override (uses config default if not provided)
    """
    global _slow_query_logger

    # Use configured threshold if not provided
    if threshold_ms is None:
        threshold_ms = settings.SLOW_QUERY_THRESHOLD_MS

    # Create logger instance
    _slow_query_logger = SlowQueryLogger(threshold_ms=threshold_ms)

    # For async engines, we need to listen to the sync engine underneath
    target_engine = engine.sync_engine if isinstance(engine, AsyncEngine) else engine

    # Register event listeners
    event.listen(
        target_engine,
        "before_cursor_execute",
        _slow_query_logger.before_cursor_execute
    )

    event.listen(
        target_engine,
        "after_cursor_execute",
        _slow_query_logger.after_cursor_execute
    )

    logger.info(
        f"Slow query logging enabled (threshold: {threshold_ms}ms = {threshold_ms/1000:.1f}s)"
    )


def get_query_stats() -> dict:
    """
    Get current query performance statistics.

    Returns:
        Dictionary with query statistics, or None if logger not initialized
    """
    if _slow_query_logger is None:
        return {
            "error": "Slow query logger not initialized",
            "total_queries": 0,
            "slow_queries": 0
        }

    return _slow_query_logger.get_stats()
