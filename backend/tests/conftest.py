"""
Pytest configuration and fixtures for testing
"""
import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings

# Test database URL (in-memory SQLite)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    Rollback all changes after the test.
    """
    # Create tables
    Base.metadata.create_all(bind=test_engine)

    # Create session
    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a FastAPI test client with overridden database dependency
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123",
        "full_name": "Test User",
    }


@pytest.fixture
def test_product_data():
    """Sample product data for testing"""
    return {
        "id": "PROD-001",
        "name": "Canapé OSLO 3 places",
        "category": "Canapés",
        "price": 1890.00,
        "description": "Canapé moderne style scandinave",
        "dimensions": "210x90x85cm",
        "colors": ["Gris perle", "Gris anthracite"],
        "stock": 10,
        "rating": 4.8,
    }


@pytest.fixture
def authenticated_client(client, test_user_data):
    """
    Create an authenticated client with a test user
    """
    # Register user
    response = client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 201

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Add token to client headers
    client.headers["Authorization"] = f"Bearer {token}"

    return client


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Bonjour! Comment puis-je vous aider aujourd'hui?",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25},
    }
