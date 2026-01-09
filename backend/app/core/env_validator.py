# backend/app/core/env_validator.py
"""
Environment variable validation at startup.
Validates required and recommended environment variables with helpful error messages.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for environment validation errors."""
    pass


class EnvironmentValidator:
    """
    Validates environment variables at application startup.
    Ensures all required variables are set and have valid values.
    """

    def __init__(self):
        """Initialize validator with validation results."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed_checks: List[str] = []

    def validate_required_string(
        self,
        var_name: str,
        description: str,
        min_length: int = 1
    ) -> Optional[str]:
        """
        Validate a required string environment variable.

        Args:
            var_name: Environment variable name
            description: Human-readable description
            min_length: Minimum required length

        Returns:
            Variable value if valid, None otherwise
        """
        value = os.getenv(var_name)

        if not value or len(value.strip()) < min_length:
            self.errors.append(
                f"{var_name}: {description} is required but not set or too short. "
                f"Please set this in your .env file."
            )
            return None

        self.passed_checks.append(f"{var_name}: ✓ Set ({description})")
        return value.strip()

    def validate_optional_string(
        self,
        var_name: str,
        description: str,
        recommend: bool = False
    ) -> Optional[str]:
        """
        Validate an optional string environment variable.

        Args:
            var_name: Environment variable name
            description: Human-readable description
            recommend: Whether to warn if not set

        Returns:
            Variable value if set, None otherwise
        """
        value = os.getenv(var_name)

        if not value or not value.strip():
            if recommend:
                self.warnings.append(
                    f"{var_name}: {description} is not set (recommended for production). "
                    f"Consider setting this in your .env file."
                )
            return None

        self.passed_checks.append(f"{var_name}: ✓ Set ({description})")
        return value.strip()

    def validate_integer(
        self,
        var_name: str,
        description: str,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        default: Optional[int] = None
    ) -> Optional[int]:
        """
        Validate an integer environment variable.

        Args:
            var_name: Environment variable name
            description: Human-readable description
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            default: Default value if not set

        Returns:
            Integer value or default
        """
        value = os.getenv(var_name)

        if not value:
            if default is not None:
                self.passed_checks.append(
                    f"{var_name}: Using default {default} ({description})"
                )
                return default
            else:
                self.errors.append(
                    f"{var_name}: {description} must be set as an integer."
                )
                return None

        try:
            int_value = int(value)

            if min_value is not None and int_value < min_value:
                self.errors.append(
                    f"{var_name}: {description} must be >= {min_value}, got {int_value}"
                )
                return None

            if max_value is not None and int_value > max_value:
                self.warnings.append(
                    f"{var_name}: {description} is {int_value}, which exceeds recommended maximum of {max_value}"
                )

            self.passed_checks.append(f"{var_name}: ✓ {int_value} ({description})")
            return int_value

        except ValueError:
            self.errors.append(
                f"{var_name}: {description} must be a valid integer, got '{value}'"
            )
            return None

    def validate_boolean(
        self,
        var_name: str,
        description: str,
        default: bool = False
    ) -> bool:
        """
        Validate a boolean environment variable.

        Args:
            var_name: Environment variable name
            description: Human-readable description
            default: Default value if not set

        Returns:
            Boolean value
        """
        value = os.getenv(var_name)

        if not value:
            self.passed_checks.append(
                f"{var_name}: Using default {default} ({description})"
            )
            return default

        bool_value = value.lower() in ("true", "1", "yes", "on")
        self.passed_checks.append(f"{var_name}: ✓ {bool_value} ({description})")
        return bool_value

    def validate_url(
        self,
        var_name: str,
        description: str,
        required_schemes: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Validate a URL environment variable.

        Args:
            var_name: Environment variable name
            description: Human-readable description
            required_schemes: List of required URL schemes (e.g., ['postgresql', 'postgres'])

        Returns:
            URL value if valid, None otherwise
        """
        value = os.getenv(var_name)

        if not value or not value.strip():
            self.errors.append(
                f"{var_name}: {description} URL is required but not set."
            )
            return None

        value = value.strip()

        # Check if URL has a scheme
        if "://" not in value:
            self.errors.append(
                f"{var_name}: {description} must be a valid URL with scheme (e.g., postgresql://...)"
            )
            return None

        # Validate scheme if required
        if required_schemes:
            scheme = value.split("://")[0]
            if scheme not in required_schemes:
                self.errors.append(
                    f"{var_name}: {description} must use one of these schemes: {', '.join(required_schemes)}. "
                    f"Got '{scheme}'."
                )
                return None

        self.passed_checks.append(f"{var_name}: ✓ Set ({description})")
        return value

    def validate_path(
        self,
        var_name: str,
        description: str,
        must_exist: bool = False,
        create_if_missing: bool = False
    ) -> Optional[str]:
        """
        Validate a file path environment variable.

        Args:
            var_name: Environment variable name
            description: Human-readable description
            must_exist: Whether the path must already exist
            create_if_missing: Whether to create the directory if missing

        Returns:
            Path value if valid, None otherwise
        """
        value = os.getenv(var_name)

        if not value or not value.strip():
            self.errors.append(
                f"{var_name}: {description} path is required but not set."
            )
            return None

        value = value.strip()
        path = Path(value)

        if must_exist and not path.exists():
            self.errors.append(
                f"{var_name}: {description} path '{value}' does not exist."
            )
            return None

        if create_if_missing and not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                self.passed_checks.append(
                    f"{var_name}: ✓ Created directory at {value} ({description})"
                )
            except Exception as e:
                self.errors.append(
                    f"{var_name}: Failed to create {description} directory at '{value}': {e}"
                )
                return None
        else:
            self.passed_checks.append(f"{var_name}: ✓ {value} ({description})")

        return value

    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get validation summary.

        Returns:
            Dictionary with validation results
        """
        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "passed_checks": self.passed_checks,
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "total_passed": len(self.passed_checks)
        }


def validate_environment() -> Dict[str, Any]:
    """
    Validate all environment variables at startup.

    Returns:
        Validation summary dictionary

    Raises:
        ValidationError: If required variables are missing or invalid
    """
    validator = EnvironmentValidator()

    logger.info("=" * 60)
    logger.info("VALIDATING ENVIRONMENT VARIABLES")
    logger.info("=" * 60)

    # Core Settings
    validator.validate_optional_string("APP_NAME", "Application name")
    validator.validate_optional_string("APP_VERSION", "Application version")
    validator.validate_boolean("DEBUG", "Debug mode", default=False)
    validator.validate_integer("PORT", "Server port", min_value=1, max_value=65535, default=8000)

    # Security Settings
    secret_key = validator.validate_required_string(
        "SECRET_KEY",
        "Secret key for JWT tokens",
        min_length=32
    )
    if secret_key and len(secret_key) < 32:
        validator.warnings.append(
            "SECRET_KEY: Key length is less than 32 characters. "
            "Consider using a longer key for better security."
        )

    # Database Settings
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Validate database URL format
        if database_url.startswith("sqlite"):
            # SQLite is OK for development
            if not validator.validate_boolean("DEBUG", "Debug mode", default=False):
                validator.errors.append(
                    "DATABASE_URL: SQLite is not recommended for production. "
                    "Please use PostgreSQL."
                )
        elif database_url.startswith(("postgresql", "postgres")):
            # PostgreSQL - validate format
            if "://" not in database_url:
                validator.errors.append(
                    "DATABASE_URL: PostgreSQL URL must include credentials "
                    "(postgresql://user:password@host:port/database)"
                )
        validator.passed_checks.append("DATABASE_URL: ✓ Set")
    else:
        # DATABASE_URL not set - check if DEBUG mode
        if not validator.validate_boolean("DEBUG", "Debug mode", default=False):
            validator.errors.append(
                "DATABASE_URL: Required in production mode. "
                "Please set a PostgreSQL connection string."
            )
        else:
            validator.warnings.append(
                "DATABASE_URL: Not set - will use SQLite for development"
            )

    # Redis Settings (optional but recommended)
    redis_url = validator.validate_optional_string(
        "REDIS_URL",
        "Redis connection URL",
        recommend=True
    )

    # API Keys
    openai_key = validator.validate_required_string(
        "OPENAI_API_KEY",
        "OpenAI API key",
        min_length=20
    )
    if openai_key and not openai_key.startswith("sk-"):
        validator.errors.append(
            "OPENAI_API_KEY: Must start with 'sk-'. "
            "Please check your API key at https://platform.openai.com/api-keys"
        )

    # Upload Settings
    validator.validate_path(
        "UPLOAD_DIR",
        "Upload directory",
        must_exist=False,
        create_if_missing=False
    )

    # Request Limits
    validator.validate_integer(
        "MAX_REQUEST_SIZE",
        "Maximum request size (bytes)",
        min_value=1024,  # At least 1KB
        default=5242880  # 5MB
    )
    validator.validate_integer(
        "REQUEST_TIMEOUT",
        "Request timeout (seconds)",
        min_value=1,
        max_value=300,  # 5 minutes max
        default=30
    )

    # Memory Thresholds
    validator.validate_integer(
        "MEMORY_WARNING_THRESHOLD_MB",
        "Memory warning threshold (MB)",
        min_value=100,
        default=500
    )
    validator.validate_integer(
        "MEMORY_CRITICAL_THRESHOLD_MB",
        "Memory critical threshold (MB)",
        min_value=100,
        default=1000
    )

    # Cloudinary (optional)
    cloudinary_name = validator.validate_optional_string(
        "CLOUDINARY_CLOUD_NAME",
        "Cloudinary cloud name"
    )
    if cloudinary_name:
        # If cloud name is set, require other Cloudinary variables
        validator.validate_required_string(
            "CLOUDINARY_API_KEY",
            "Cloudinary API key"
        )
        validator.validate_required_string(
            "CLOUDINARY_API_SECRET",
            "Cloudinary API secret"
        )

    # CORS Origins
    cors_origins = validator.validate_optional_string(
        "CORS_ORIGINS",
        "CORS allowed origins (comma-separated)"
    )

    # Get validation summary
    summary = validator.get_validation_summary()

    # Log results
    logger.info("=" * 60)
    logger.info(f"VALIDATION RESULTS: {'✓ PASSED' if summary['valid'] else '✗ FAILED'}")
    logger.info("=" * 60)

    if summary["errors"]:
        logger.error(f"❌ {summary['total_errors']} ERRORS FOUND:")
        for error in summary["errors"]:
            logger.error(f"   • {error}")

    if summary["warnings"]:
        logger.warning(f"⚠️  {summary['total_warnings']} WARNINGS:")
        for warning in summary["warnings"]:
            logger.warning(f"   • {warning}")

    logger.info(f"✓ {summary['total_passed']} checks passed")
    logger.info("=" * 60)

    # Raise exception if validation failed
    if not summary["valid"]:
        raise ValidationError(
            f"Environment validation failed with {summary['total_errors']} errors. "
            f"Please fix the issues above and restart the application."
        )

    return summary
