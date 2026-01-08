# backend/app/core/logging.py
"""
Secure logging configuration with sensitive data filtering
"""
import logging
import sys
import re
from pathlib import Path
from typing import Dict, List, Pattern


class SensitiveDataFilter(logging.Filter):
    """
    Logging filter that redacts sensitive data from log messages.
    Protects passwords, API keys, tokens, emails, and other PII.
    """

    # Patterns for sensitive data detection
    SENSITIVE_PATTERNS: List[Dict[str, Pattern]] = [
        # API Keys and Tokens
        {
            "name": "OpenAI API Key",
            "pattern": re.compile(r'(sk-[a-zA-Z0-9]{20,})', re.IGNORECASE),
            "replacement": "sk-***REDACTED***"
        },
        {
            "name": "Generic API Key",
            "pattern": re.compile(r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9]{20,})', re.IGNORECASE),
            "replacement": r'\1***REDACTED***'
        },
        {
            "name": "Bearer Token",
            "pattern": re.compile(r'(Bearer\s+)([a-zA-Z0-9\-._~+/]+=*)', re.IGNORECASE),
            "replacement": r'\1***REDACTED***'
        },
        {
            "name": "JWT Token",
            "pattern": re.compile(r'(eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*)', re.IGNORECASE),
            "replacement": "***REDACTED_JWT***"
        },
        # Passwords
        {
            "name": "Password Field",
            "pattern": re.compile(r'(password["\']?\s*[:=]\s*["\']?)([^"\'}\s,]+)', re.IGNORECASE),
            "replacement": r'\1***REDACTED***'
        },
        {
            "name": "Secret Field",
            "pattern": re.compile(r'(secret["\']?\s*[:=]\s*["\']?)([^"\'}\s,]+)', re.IGNORECASE),
            "replacement": r'\1***REDACTED***'
        },
        # Database URLs with credentials
        {
            "name": "Database URL",
            "pattern": re.compile(r'(postgresql://|postgres://|mysql://)([^:]+):([^@]+)@', re.IGNORECASE),
            "replacement": r'\1\2:***REDACTED***@'
        },
        # Email addresses (optional - comment out if emails should be logged)
        {
            "name": "Email Address",
            "pattern": re.compile(r'\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'),
            "replacement": r'***@\2'  # Keep domain for debugging, redact local part
        },
        # Credit Card Numbers (basic pattern)
        {
            "name": "Credit Card",
            "pattern": re.compile(r'\b(?:\d[ -]*?){13,16}\b'),
            "replacement": "***CARD_REDACTED***"
        },
        # Authorization Headers
        {
            "name": "Authorization Header",
            "pattern": re.compile(r'(authorization["\']?\s*[:=]\s*["\']?)([^"\'}\s,]+)', re.IGNORECASE),
            "replacement": r'\1***REDACTED***'
        },
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record to redact sensitive information.

        Args:
            record: The log record to filter

        Returns:
            True to allow the record to be logged
        """
        # Redact sensitive data from the message
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = self.redact_sensitive_data(record.msg)

        # Redact from args if present
        if hasattr(record, 'args') and record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: self.redact_sensitive_data(str(v)) if isinstance(v, str) else v
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(
                    self.redact_sensitive_data(str(arg)) if isinstance(arg, str) else arg
                    for arg in record.args
                )

        return True

    def redact_sensitive_data(self, text: str) -> str:
        """
        Redact sensitive data from text using predefined patterns.

        Args:
            text: Text to redact

        Returns:
            Text with sensitive data redacted
        """
        if not text:
            return text

        redacted_text = text

        # Apply all patterns
        for pattern_info in self.SENSITIVE_PATTERNS:
            pattern = pattern_info["pattern"]
            replacement = pattern_info["replacement"]
            redacted_text = pattern.sub(replacement, redacted_text)

        return redacted_text


def setup_logging():
    """
    Configure application logging with sensitive data filtering.

    Returns:
        Logger instance
    """
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create sensitive data filter
    sensitive_filter = SensitiveDataFilter()

    # Create file handler
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setLevel(logging.INFO)
    file_handler.addFilter(sensitive_filter)
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.addFilter(sensitive_filter)
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Add our secure handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Set specific log levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)  # Don't log SQL with parameters

    logger = logging.getLogger(__name__)
    logger.info("🔒 Secure logging initialized with sensitive data filtering")

    return logger
