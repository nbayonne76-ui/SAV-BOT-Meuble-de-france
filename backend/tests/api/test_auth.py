"""
Tests for authentication endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestAuthEndpoints:
    """Test authentication endpoints"""

    def test_register_new_user(self, client: TestClient, test_user_data):
        """Test user registration with valid data"""
        response = client.post("/api/auth/register", json=test_user_data)

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert data["email"] == test_user_data["email"]

    def test_register_duplicate_email(self, client: TestClient, test_user_data):
        """Test registration fails with duplicate email"""
        # Register first time
        client.post("/api/auth/register", json=test_user_data)

        # Try to register again with same email
        response = client.post("/api/auth/register", json=test_user_data)

        assert response.status_code == 400
        assert "email already registered" in response.json()["detail"].lower()

    def test_login_valid_credentials(self, client: TestClient, test_user_data):
        """Test login with valid credentials"""
        # Register user first
        client.post("/api/auth/register", json=test_user_data)

        # Login
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_password(self, client: TestClient, test_user_data):
        """Test login fails with wrong password"""
        # Register user first
        client.post("/api/auth/register", json=test_user_data)

        # Try to login with wrong password
        response = client.post(
            "/api/auth/login",
            json={"email": test_user_data["email"], "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login fails for non-existent user"""
        response = client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )

        assert response.status_code == 401

    def test_get_current_user(self, authenticated_client: TestClient, test_user_data):
        """Test getting current user info with valid token"""
        response = authenticated_client.get("/api/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert "full_name" in data

    def test_get_current_user_no_token(self, client: TestClient):
        """Test getting current user fails without token"""
        response = client.get("/api/auth/me")

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user fails with invalid token"""
        client.headers["Authorization"] = "Bearer invalid_token"
        response = client.get("/api/auth/me")

        assert response.status_code == 401
