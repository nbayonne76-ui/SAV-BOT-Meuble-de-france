"""
Tests for health check endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns app info"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "app" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"

    def test_health_endpoint(self, client: TestClient):
        """Test health endpoint returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "version" in data

    def test_readiness_endpoint(self, client: TestClient):
        """Test readiness endpoint checks dependencies"""
        response = client.get("/ready")
        assert response.status_code == 200

        data = response.json()
        assert "ready" in data
        assert "checks" in data

        # Check that all required services are checked
        checks = data["checks"]
        assert "database" in checks
        assert "cache" in checks
        assert "uploads_dir" in checks
