# backend/app/models/user.py
"""
User models for authentication
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum
import re


class UserRole(str, Enum):
    """User roles for authorization"""
    CUSTOMER = "CUSTOMER"
    AGENT = "AGENT"
    ADMIN = "ADMIN"
    API_SERVICE = "API_SERVICE"


class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"


# ============== Request/Response Models ==============

class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)

    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must be alphanumeric (underscores and hyphens allowed)')
        return v.lower()


class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = UserRole.CUSTOMER

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """Model for user login"""
    username: str  # Can be username or email
    password: str


class UserUpdate(BaseModel):
    """Model for updating user profile"""
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    """Model for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator('new_password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserResponse(UserBase):
    """Model for user response (without sensitive data)"""
    id: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    """User model as stored in database"""
    id: str
    hashed_password: str
    role: UserRole = UserRole.CUSTOMER
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    api_key_hash: Optional[str] = None  # For service accounts

    class Config:
        from_attributes = True


# ============== SQLAlchemy Model ==============

from sqlalchemy import Column, String, DateTime, Integer, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserDB(Base):
    """SQLAlchemy User model for database"""
    __tablename__ = "users"
    __table_args__ = (
        # Composite indexes for common query patterns
        {'comment': 'User accounts with authentication and authorization'},
    )

    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.CUSTOMER, nullable=False, index=True)  # Index for role-based queries
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False, index=True)  # Index for status filtering
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)  # Index for sorting
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True, index=True)  # Index for checking locked accounts
    api_key_hash = Column(String(255), nullable=True)

    def to_response(self) -> UserResponse:
        """Convert DB model to response model"""
        return UserResponse(
            id=self.id,
            email=self.email,
            username=self.username,
            full_name=self.full_name,
            role=self.role,
            status=self.status,
            created_at=self.created_at,
            last_login=self.last_login
        )


# ============== API Key Model ==============

class APIKeyCreate(BaseModel):
    """Model for creating an API key"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    scopes: List[str] = Field(default_factory=list)


class APIKeyResponse(BaseModel):
    """Response when creating an API key (only time the key is shown)"""
    id: str
    name: str
    key: str  # Only shown once at creation
    scopes: List[str]
    created_at: datetime


class APIKeyDB(Base):
    """SQLAlchemy API Key model"""
    __tablename__ = "api_keys"
    __table_args__ = (
        # Composite index for finding active keys for a user
        {'comment': 'API keys for programmatic access'},
    )

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    key_hash = Column(String(255), nullable=False, index=True)  # Index for key lookup
    user_id = Column(String(36), nullable=False, index=True)  # Index for user's keys
    scopes = Column(String(500), default="")  # Comma-separated scopes
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    is_active = Column(Integer, default=1, index=True)  # Index for filtering active keys
