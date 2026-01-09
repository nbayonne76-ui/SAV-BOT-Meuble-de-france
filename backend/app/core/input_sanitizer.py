# backend/app/core/input_sanitizer.py
"""
Input sanitization utilities to prevent XSS, injection attacks, and other security issues
"""
import re
import html
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class InputSanitizer:
    """
    Centralized input sanitization for security
    Prevents XSS, SQL injection, log injection, and other attacks
    """

    # Maximum lengths for different field types
    MAX_LENGTHS = {
        "customer_id": 100,
        "order_number": 50,
        "product_sku": 100,
        "product_name": 200,
        "problem_description": 5000,
        "warranty_id": 100,
        "ticket_id": 50,
        "evidence_url": 2048,
        "evidence_description": 1000,
        "general_text": 500
    }

    # Dangerous patterns to remove
    DANGEROUS_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # Script tags
        r"javascript:",  # Javascript protocol
        r"on\w+\s*=",  # Event handlers (onclick, onerror, etc.)
        r"<iframe[^>]*>",  # iframes
        r"<object[^>]*>",  # objects
        r"<embed[^>]*>",  # embeds
    ]

    # SQL injection patterns
    SQL_PATTERNS = [
        r"(\bOR\b|\bAND\b).*=.*",  # OR/AND equality
        r";\s*DROP\s+TABLE",  # Drop table
        r";\s*DELETE\s+FROM",  # Delete
        r"UNION\s+SELECT",  # Union select
        r"--",  # SQL comments
        r"/\*.*\*/",  # Multi-line comments
    ]

    @classmethod
    def sanitize_text(
        cls,
        text: Optional[str],
        field_name: str = "general_text",
        allow_html: bool = False,
        max_length: Optional[int] = None
    ) -> str:
        """
        Sanitize text input

        Args:
            text: Input text to sanitize
            field_name: Field name for length validation
            allow_html: Whether to allow HTML (default: False)
            max_length: Custom max length (overrides field_name lookup)

        Returns:
            Sanitized text
        """
        if text is None:
            return ""

        # Convert to string
        text = str(text).strip()

        # Check max length
        max_len = max_length or cls.MAX_LENGTHS.get(field_name, cls.MAX_LENGTHS["general_text"])
        if len(text) > max_len:
            logger.warning(f"Input truncated: {field_name} exceeded {max_len} characters")
            text = text[:max_len]

        # Remove null bytes
        text = text.replace("\x00", "")

        # Remove dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        # Check for SQL injection patterns
        for pattern in cls.SQL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected in {field_name}: {text[:50]}")
                text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        # HTML escape if not allowing HTML
        if not allow_html:
            text = html.escape(text)

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    @classmethod
    def sanitize_order_number(cls, order_number: Optional[str]) -> str:
        """
        Sanitize and validate order number format

        Args:
            order_number: Raw order number

        Returns:
            Sanitized order number

        Raises:
            ValueError: If format is invalid
        """
        if not order_number:
            return ""

        order_number = str(order_number).strip().upper()

        # Remove dangerous characters
        order_number = re.sub(r"[^\w\-]", "", order_number)

        # Validate format: CMD-XXXX-XXXXX
        if not re.match(r"^CMD-\d{4}-\d{5}$", order_number):
            logger.warning(f"Invalid order number format: {order_number}")
            # Try to clean it up
            cleaned = re.sub(r"[^A-Z0-9\-]", "", order_number)
            if not re.match(r"^CMD-?\d{4}-?\d{5}$", cleaned):
                raise ValueError(f"Invalid order number format: {order_number}")
            order_number = cleaned

        # Ensure max length
        if len(order_number) > cls.MAX_LENGTHS["order_number"]:
            raise ValueError(f"Order number too long: {order_number}")

        return order_number

    @classmethod
    def sanitize_url(cls, url: Optional[str]) -> str:
        """
        Sanitize URL input

        Args:
            url: Raw URL

        Returns:
            Sanitized URL

        Raises:
            ValueError: If URL is invalid or potentially malicious
        """
        if not url:
            return ""

        url = str(url).strip()

        # Check length
        if len(url) > cls.MAX_LENGTHS["evidence_url"]:
            raise ValueError(f"URL too long: {len(url)} characters")

        # Remove null bytes
        url = url.replace("\x00", "")

        # Check for dangerous protocols
        dangerous_protocols = ["javascript:", "data:", "vbscript:", "file:"]
        url_lower = url.lower()
        for protocol in dangerous_protocols:
            if url_lower.startswith(protocol):
                logger.warning(f"Dangerous protocol detected: {protocol}")
                raise ValueError(f"Unsupported URL protocol: {protocol}")

        # Must start with http:// or https://
        if not re.match(r"^https?://", url):
            logger.warning(f"URL missing protocol: {url}")
            raise ValueError("URL must start with http:// or https://")

        # Remove any HTML encoding attempts
        url = html.unescape(url)

        return url

    @classmethod
    def sanitize_customer_id(cls, customer_id: Optional[str]) -> str:
        """
        Sanitize customer ID

        Args:
            customer_id: Raw customer ID

        Returns:
            Sanitized customer ID
        """
        if not customer_id:
            raise ValueError("Customer ID is required")

        customer_id = str(customer_id).strip()

        # Remove dangerous characters (allow alphanumeric, @, ., -, _)
        customer_id = re.sub(r"[^\w@.\-]", "", customer_id)

        if len(customer_id) > cls.MAX_LENGTHS["customer_id"]:
            raise ValueError(f"Customer ID too long: {len(customer_id)} characters")

        if len(customer_id) == 0:
            raise ValueError("Customer ID cannot be empty after sanitization")

        return customer_id

    @classmethod
    def sanitize_product_sku(cls, sku: Optional[str]) -> str:
        """
        Sanitize product SKU

        Args:
            sku: Raw SKU

        Returns:
            Sanitized SKU
        """
        if not sku:
            raise ValueError("Product SKU is required")

        sku = str(sku).strip().upper()

        # Remove dangerous characters (allow alphanumeric and -)
        sku = re.sub(r"[^\w\-]", "", sku)

        if len(sku) > cls.MAX_LENGTHS["product_sku"]:
            raise ValueError(f"Product SKU too long: {len(sku)} characters")

        if len(sku) == 0:
            raise ValueError("Product SKU cannot be empty after sanitization")

        return sku

    @classmethod
    def sanitize_for_logging(cls, text: str, max_length: int = 100) -> str:
        """
        Sanitize text for safe logging (prevent log injection)

        Args:
            text: Text to sanitize
            max_length: Maximum length for log entry

        Returns:
            Sanitized text safe for logging
        """
        if not text:
            return ""

        text = str(text)

        # Remove newlines and carriage returns (log injection)
        text = text.replace("\n", " ").replace("\r", " ")

        # Remove ANSI escape codes
        text = re.sub(r"\x1b\[[0-9;]*m", "", text)

        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length] + "..."

        return text


# Convenience instance
input_sanitizer = InputSanitizer()
