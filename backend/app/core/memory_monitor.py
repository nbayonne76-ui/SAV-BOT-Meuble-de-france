# backend/app/core/memory_monitor.py
"""
Memory usage monitoring and alerting.
Tracks application memory usage and alerts when thresholds are exceeded.
"""
import logging
import os
import gc
from typing import Dict, Any
import psutil

from app.core.config import settings

logger = logging.getLogger(__name__)


class MemoryMonitor:
    """
    Monitor application memory usage and generate alerts when thresholds are exceeded.
    """

    def __init__(self):
        """Initialize memory monitor with configured thresholds."""
        self.process = psutil.Process(os.getpid())
        self.warning_threshold_mb = settings.MEMORY_WARNING_THRESHOLD_MB
        self.critical_threshold_mb = settings.MEMORY_CRITICAL_THRESHOLD_MB
        self.warning_percent = settings.MEMORY_WARNING_PERCENT
        self.critical_percent = settings.MEMORY_CRITICAL_PERCENT

        # Alert tracking to prevent spam
        self.last_warning_level = None
        self.warning_count = 0
        self.critical_count = 0

    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Get current memory usage statistics.

        Returns:
            Dictionary with memory usage details
        """
        # Process memory info
        memory_info = self.process.memory_info()
        rss_mb = memory_info.rss / 1024 / 1024  # Resident Set Size in MB
        vms_mb = memory_info.vms / 1024 / 1024  # Virtual Memory Size in MB

        # System memory info
        system_memory = psutil.virtual_memory()
        total_system_mb = system_memory.total / 1024 / 1024
        available_system_mb = system_memory.available / 1024 / 1024
        system_percent = system_memory.percent

        # Calculate process memory as percentage of system memory
        process_percent = (rss_mb / total_system_mb) * 100

        return {
            "process": {
                "rss_mb": round(rss_mb, 2),
                "vms_mb": round(vms_mb, 2),
                "percent_of_system": round(process_percent, 2)
            },
            "system": {
                "total_mb": round(total_system_mb, 2),
                "available_mb": round(available_system_mb, 2),
                "used_percent": round(system_percent, 2)
            },
            "thresholds": {
                "warning_mb": self.warning_threshold_mb,
                "critical_mb": self.critical_threshold_mb,
                "warning_percent": self.warning_percent,
                "critical_percent": self.critical_percent
            }
        }

    def check_thresholds(self) -> Dict[str, Any]:
        """
        Check current memory usage against configured thresholds.

        Returns:
            Dictionary with status and recommendations
        """
        usage = self.get_memory_usage()
        rss_mb = usage["process"]["rss_mb"]
        process_percent = usage["process"]["percent_of_system"]
        system_percent = usage["system"]["used_percent"]

        # Determine alert level
        status = "ok"
        alert_level = None
        messages = []
        recommendations = []

        # Check process memory (absolute)
        if rss_mb >= self.critical_threshold_mb:
            status = "critical"
            alert_level = "critical"
            messages.append(
                f"Process memory usage ({rss_mb:.0f}MB) exceeds CRITICAL threshold "
                f"({self.critical_threshold_mb}MB)"
            )
            recommendations.extend([
                "Restart application to free memory",
                "Check for memory leaks",
                "Review cache size configuration",
                "Consider scaling horizontally"
            ])
            self.critical_count += 1

        elif rss_mb >= self.warning_threshold_mb:
            status = "warning"
            alert_level = "warning"
            messages.append(
                f"Process memory usage ({rss_mb:.0f}MB) exceeds WARNING threshold "
                f"({self.warning_threshold_mb}MB)"
            )
            recommendations.extend([
                "Monitor memory usage closely",
                "Consider triggering garbage collection",
                "Review active connections and cache"
            ])
            self.warning_count += 1

        # Check system memory percentage
        if system_percent >= self.critical_percent:
            if status != "critical":
                status = "warning"
            alert_level = "warning" if alert_level is None else alert_level
            messages.append(
                f"System memory usage ({system_percent:.1f}%) exceeds threshold "
                f"({self.critical_percent}%)"
            )
            recommendations.append("System-wide memory pressure detected")

        elif system_percent >= self.warning_percent:
            if status == "ok":
                status = "warning"
                alert_level = "warning"
            messages.append(
                f"System memory usage ({system_percent:.1f}%) approaching threshold "
                f"({self.warning_percent}%)"
            )

        # Log alerts (but limit spam)
        if alert_level and alert_level != self.last_warning_level:
            for message in messages:
                if alert_level == "critical":
                    logger.error(f"MEMORY CRITICAL: {message}")
                else:
                    logger.warning(f"MEMORY WARNING: {message}")

            if recommendations:
                logger.warning(f"Recommendations: {', '.join(recommendations)}")

            self.last_warning_level = alert_level

        # Reset warning tracking if memory is ok
        if status == "ok":
            self.last_warning_level = None

        return {
            "status": status,
            "alert_level": alert_level,
            "messages": messages,
            "recommendations": recommendations,
            "usage": usage,
            "alert_counts": {
                "warnings": self.warning_count,
                "critical": self.critical_count
            }
        }

    def trigger_gc(self) -> Dict[str, Any]:
        """
        Manually trigger garbage collection.

        Returns:
            Dictionary with GC results and memory freed
        """
        # Get memory before GC
        before = self.process.memory_info().rss / 1024 / 1024

        # Run garbage collection
        collected = gc.collect()

        # Get memory after GC
        after = self.process.memory_info().rss / 1024 / 1024
        freed_mb = before - after

        logger.info(
            f"Garbage collection completed: "
            f"collected {collected} objects, "
            f"freed {freed_mb:.2f}MB"
        )

        return {
            "objects_collected": collected,
            "memory_before_mb": round(before, 2),
            "memory_after_mb": round(after, 2),
            "memory_freed_mb": round(freed_mb, 2)
        }


# Global memory monitor instance
_memory_monitor: MemoryMonitor = None


def get_memory_monitor() -> MemoryMonitor:
    """
    Get or create the global memory monitor instance.

    Returns:
        MemoryMonitor instance
    """
    global _memory_monitor

    if _memory_monitor is None:
        _memory_monitor = MemoryMonitor()
        logger.info(
            f"Memory monitor initialized (thresholds: "
            f"{settings.MEMORY_WARNING_THRESHOLD_MB}MB warning, "
            f"{settings.MEMORY_CRITICAL_THRESHOLD_MB}MB critical)"
        )

    return _memory_monitor


def get_memory_status() -> Dict[str, Any]:
    """
    Get current memory status with threshold checks.

    Returns:
        Dictionary with memory status
    """
    monitor = get_memory_monitor()
    return monitor.check_thresholds()


def get_memory_usage() -> Dict[str, Any]:
    """
    Get current memory usage without threshold checks.

    Returns:
        Dictionary with memory usage details
    """
    monitor = get_memory_monitor()
    return monitor.get_memory_usage()


def trigger_garbage_collection() -> Dict[str, Any]:
    """
    Manually trigger garbage collection.

    Returns:
        Dictionary with GC results
    """
    monitor = get_memory_monitor()
    return monitor.trigger_gc()
