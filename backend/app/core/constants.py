# backend/app/core/constants.py
"""
Application constants and configuration values.
Centralizes all hardcoded values to improve maintainability.
"""

from typing import Dict, List

# ===========================================
# OpenAI Configuration
# ===========================================

# Model selection
OPENAI_MODEL = "gpt-3.5-turbo"  # 10x cheaper than GPT-4, suitable for chatbot
OPENAI_MODEL_REALTIME = "gpt-4o-realtime-preview-2024-10-01"  # For voice features

# Token limits
OPENAI_MAX_TOKENS = 500  # Reduced from 1000 to save costs
"""
Max tokens per response. 500 tokens ≈ 375 words in French.
Sufficient for chatbot responses while keeping costs low.
"""

# Temperature for creativity
OPENAI_TEMPERATURE = 0.7  # Balance between creativity and consistency
"""
Temperature 0.7 provides good balance:
- 0.0 = Deterministic, repetitive
- 0.7 = Creative but consistent (recommended)
- 1.0 = Very creative, less predictable
"""

# Timeout configuration
OPENAI_TIMEOUT_SECONDS = 30  # Max wait time for API response
OPENAI_MAX_RETRIES = 2  # Number of automatic retries on failure


# ===========================================
# Session Management
# ===========================================

SESSION_TTL_HOURS = 24  # Sessions expire after 24 hours of inactivity
"""
Session TTL (Time To Live) in hours.
After this period, Redis automatically deletes inactive sessions.
24 hours = reasonable balance between UX and memory usage.
"""

CONVERSATION_HISTORY_LIMIT = 6  # Keep only last 6 messages (3 exchanges)
"""
Conversation history limit to reduce costs and context size.
6 messages = last 3 user-bot exchanges.
Older messages are dropped from context.
"""

SESSION_KEY_PREFIX = "session:"  # Redis key prefix for sessions


# ===========================================
# Priority System
# ===========================================

# Priority levels (from most urgent to least urgent)
PRIORITY_LEVELS = ["P0", "P1", "P2", "P3"]

# Priority emojis for visual representation
PRIORITY_EMOJIS: Dict[str, str] = {
    "P0": "🔴",  # Critical - Red circle
    "P1": "🟠",  # High - Orange circle
    "P2": "🟡",  # Medium - Yellow circle
    "P3": "🟢"   # Low - Green circle
}

# Priority labels in French
PRIORITY_LABELS: Dict[str, str] = {
    "P0": "CRITIQUE",
    "P1": "HAUTE",
    "P2": "MOYENNE",
    "P3": "BASSE"
}

# SLA times (Service Level Agreement) by priority
# Used consistently across priority_scorer.py and sav_workflow_engine.py
PRIORITY_SLA_TIMES: Dict[str, Dict[str, int]] = {
    "P0": {
        "response_hours": 4,      # Must respond within 4 hours
        "intervention_hours": 24  # Must intervene within 24 hours
    },
    "P1": {
        "response_hours": 24,     # Must respond within 24 hours
        "intervention_hours": 48  # Must intervene within 48 hours
    },
    "P2": {
        "response_hours": 120,    # Must respond within 5 days
        "intervention_hours": 168  # Must intervene within 7 days
    },
    "P3": {
        "response_hours": 168,    # Must respond within 7 days
        "intervention_hours": 336  # Must intervene within 14 days
    }
}


# ===========================================
# Priority Scoring Weights
# ===========================================

# Problem type weights (0-30 points)
PROBLEM_TYPE_WEIGHTS: Dict[str, int] = {
    "structural": 30,    # Most critical - safety risk
    "mechanism": 25,     # High - product unusable
    "delivery": 20,      # High - customer waiting
    "dimensions": 18,    # Medium-high - wrong product
    "cushions": 15,      # Medium - comfort issue
    "assembly": 15,      # Medium - installation problem
    "fabric": 10,        # Low - cosmetic issue
    "smell": 8,          # Low - will dissipate
    "unknown": 5         # Lowest - needs investigation
}

# Severity weights (0-25 points)
SEVERITY_WEIGHTS: Dict[str, int] = {
    "P0": 25,  # Critical severity
    "P1": 20,  # High severity
    "P2": 10,  # Medium severity
    "P3": 5    # Low severity
}

# Age scoring thresholds (days since purchase)
AGE_THRESHOLDS = {
    "very_recent": 7,      # < 7 days = 20 points
    "recent": 30,          # < 30 days = 15 points
    "under_warranty": 730, # < 2 years = 10 points
    "old": 730             # > 2 years = 5 points
}

# Customer tier weights
CUSTOMER_TIER_WEIGHTS: Dict[str, int] = {
    "vip": 15,      # VIP customers - highest priority
    "gold": 10,     # Gold loyalty - high priority
    "silver": 5,    # Silver loyalty - medium priority
    "standard": 0   # Standard - no bonus
}

# Critical keywords score bonus
CRITICAL_KEYWORDS_SCORE = 20  # Added when critical words detected (danger, blessure, etc.)

# Repeat customer penalty/bonus
REPEAT_CUSTOMER_SCORE_PER_CLAIM = 5  # +5 points per previous claim

# Product value thresholds
PRODUCT_VALUE_THRESHOLDS = {
    "high_value": 2000,    # > 2000€ = 15 points
    "medium_value": 1000,  # > 1000€ = 10 points
    "standard_value": 500  # > 500€ = 5 points
}

# Total score to priority mapping
SCORE_TO_PRIORITY_THRESHOLDS = {
    "P0": 85,  # Score >= 85 → P0 (Critical)
    "P1": 60,  # Score >= 60 → P1 (High)
    "P2": 30,  # Score >= 30 → P2 (Medium)
    "P3": 0    # Score < 30 → P3 (Low)
}


# ===========================================
# File Upload Configuration
# ===========================================

MAX_FILE_SIZE_BYTES = 10485760  # 10 MB in bytes
"""
Maximum file size for uploads.
10 MB is sufficient for photos and short videos.
"""

ALLOWED_FILE_EXTENSIONS: List[str] = [
    # Images
    "jpg", "jpeg", "png", "gif", "heic",
    # Videos
    "mp4", "mov", "avi", "webm"
]

# Upload directory
DEFAULT_UPLOAD_DIR = "./uploads"


# ===========================================
# Rate Limiting
# ===========================================

RATE_LIMIT_DEFAULT = "100/minute"  # General API endpoints
RATE_LIMIT_AUTH = "5/minute"       # Authentication endpoints (prevent brute force)
RATE_LIMIT_UPLOAD = "10/minute"    # File upload endpoints
RATE_LIMIT_CHAT = "30/minute"      # Chat endpoint


# ===========================================
# JWT Token Configuration
# ===========================================

ACCESS_TOKEN_EXPIRE_MINUTES = 30   # Access tokens valid for 30 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7      # Refresh tokens valid for 7 days

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


# ===========================================
# Database Configuration
# ===========================================

# SQLite defaults (development only)
DEFAULT_DATABASE_URL = "sqlite:///./chatbot.db"

# Connection pool settings (for PostgreSQL production)
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_TIMEOUT = 30  # seconds


# ===========================================
# Redis Configuration
# ===========================================

DEFAULT_REDIS_URL = "memory://"  # Fallback for development
REDIS_TOKEN_PREFIX = "revoked_token:"  # Prefix for revoked JWT tokens
REDIS_USER_REVOKE_PREFIX = "user_revoked:"  # Prefix for user-level revocations


# ===========================================
# CORS Configuration
# ===========================================

DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative frontend port
]


# ===========================================
# Warranty Configuration
# ===========================================

WARRANTY_DURATION_YEARS = 2  # Standard warranty duration
WARRANTY_DURATION_DAYS = 730  # 2 years in days


# ===========================================
# SAV Workflow Configuration
# ===========================================

# Minimum confidence threshold for auto-resolution
AUTO_RESOLUTION_CONFIDENCE_THRESHOLD = 0.7  # 70% confidence required
"""
Confidence threshold for automatic problem resolution.
0.7 = 70% confidence required before auto-resolving without human review.
Lower = more automation but higher error risk.
Higher = safer but more human intervention needed.
"""

# Evidence quality thresholds
EVIDENCE_QUALITY_THRESHOLDS = {
    "excellent": 0.9,  # 90%+ quality
    "good": 0.7,       # 70%+ quality
    "acceptable": 0.5, # 50%+ quality
    "poor": 0.0        # < 50% quality
}


# ===========================================
# Chatbot Behavior Configuration
# ===========================================

# Tone analysis thresholds
TONE_ANGRY_THRESHOLD = 0.7     # Consider angry if score >= 0.7
TONE_URGENT_THRESHOLD = 0.6    # Consider urgent if score >= 0.6
TONE_POLITE_THRESHOLD = 0.5    # Consider polite if score >= 0.5

# Response templates
DEFAULT_GREETING = "Bonjour ! Bienvenue chez Mobilier de France. Comment puis-je vous aider aujourd'hui ?"
DEFAULT_GOODBYE = "Merci de nous avoir contactés. Passez une excellente journée !"

# Validation keywords
CONFIRMATION_KEYWORDS = ["oui", "yes", "ok", "d'accord", "valider", "confirmer", "exactement", "correct"]
REJECTION_KEYWORDS = ["non", "no", "annuler", "pas exactement", "incorrect", "faux"]
CLOSE_KEYWORDS = ["clôturer", "terminer", "fermer", "finir", "au revoir", "bye"]
CONTINUE_KEYWORDS = ["continuer", "autre chose", "oui", "encore", "besoin"]


# ===========================================
# Logging Configuration
# ===========================================

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL_DEFAULT = "INFO"
LOG_LEVEL_DEBUG = "DEBUG"


# ===========================================
# Application Metadata
# ===========================================

APP_NAME_DEFAULT = "Mobilier de France Chatbot"
APP_VERSION_DEFAULT = "1.0.0"


# ===========================================
# Helper Functions
# ===========================================

def get_priority_emoji(priority_code: str) -> str:
    """Get emoji for a priority code."""
    return PRIORITY_EMOJIS.get(priority_code, "🟡")  # Default to yellow


def get_priority_label(priority_code: str) -> str:
    """Get label for a priority code."""
    return PRIORITY_LABELS.get(priority_code, "MOYENNE")  # Default to MOYENNE


def get_sla_times(priority_code: str) -> Dict[str, int]:
    """Get SLA times for a priority code."""
    return PRIORITY_SLA_TIMES.get(
        priority_code,
        {"response_hours": 120, "intervention_hours": 168}  # Default to P2
    )


def is_confirmation(text: str) -> bool:
    """Check if text contains confirmation keywords."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in CONFIRMATION_KEYWORDS)


def is_rejection(text: str) -> bool:
    """Check if text contains rejection keywords."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in REJECTION_KEYWORDS)


def is_close_request(text: str) -> bool:
    """Check if text contains close keywords."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in CLOSE_KEYWORDS)


def is_continue_request(text: str) -> bool:
    """Check if text contains continue keywords."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in CONTINUE_KEYWORDS)
