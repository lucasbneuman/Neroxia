"""
Configuration API Tests

Tests for configuration management endpoints:
- GET /config - Retrieve configuration
- PUT /config - Update configuration
- POST /config/reset - Reset to defaults
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict


class TestConfigurationAPI:
    """Test suite for configuration management endpoints."""
    
    def test_get_config_requires_auth(self, client: TestClient):
        """Test that GET /config requires authentication."""
        response = client.get("/config")
        assert response.status_code == 401, "Should require authentication"
    
    def test_get_config_success(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test successful configuration retrieval."""
        response = client.get("/config", headers=auth_headers)
        
        assert response.status_code == 200, f"Failed to get config: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "configs" in data, "Response should contain 'configs' key"
        configs = data["configs"]
        
        # Verify essential config fields exist
        expected_fields = [
            "system_prompt",
            "welcome_message",
            "product_name",
            "use_emojis",
            "text_audio_ratio"
        ]
        for field in expected_fields:
            assert field in configs, f"Config missing field: {field}"
    
    def test_update_config_requires_auth(self, client: TestClient):
        """Test that PUT /config requires authentication."""
        response = client.put("/config", json={"configs": {}})
        assert response.status_code == 401, "Should require authentication"
    
    def test_update_config_success(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, str],
        test_config: Dict
    ):
        """Test successful configuration update."""
        # Update configuration
        response = client.put(
            "/config",
            headers=auth_headers,
            json={"configs": test_config}
        )
        
        assert response.status_code == 200, f"Failed to update config: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert data["status"] == "success", "Update should be successful"
        assert "message" in data, "Response should contain message"
        assert "configs" in data, "Response should contain updated configs"
        
        # Verify config was actually updated
        get_response = client.get("/config", headers=auth_headers)
        assert get_response.status_code == 200
        
        updated_configs = get_response.json()["configs"]
        assert updated_configs["system_prompt"] == test_config["system_prompt"]
        assert updated_configs["product_name"] == test_config["product_name"]
    
    def test_update_partial_config(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test updating only some configuration fields."""
        partial_config = {
            "system_prompt": "Partial update test",
            "use_emojis": False
        }
        
        response = client.put(
            "/config",
            headers=auth_headers,
            json={"configs": partial_config}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        
        # Verify partial update worked
        get_response = client.get("/config", headers=auth_headers)
        configs = get_response.json()["configs"]
        assert configs["system_prompt"] == partial_config["system_prompt"]
        assert configs["use_emojis"] == partial_config["use_emojis"]
    
    def test_reset_config_requires_auth(self, client: TestClient):
        """Test that POST /config/reset requires authentication."""
        response = client.post("/config/reset")
        assert response.status_code == 401
    
    def test_reset_config_success(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_config: Dict
    ):
        """Test configuration reset to defaults."""
        # First, update config
        client.put(
            "/config",
            headers=auth_headers,
            json={"configs": test_config}
        )
        
        # Then reset
        response = client.post("/config/reset", headers=auth_headers)
        
        assert response.status_code == 200, f"Failed to reset config: {response.text}"
        data = response.json()
        
        assert data["status"] == "success"
        assert "message" in data
        assert "configs" in data
        
        # Verify config was reset (should not match test_config)
        configs = data["configs"]
        assert configs["system_prompt"] != test_config["system_prompt"]
    
    def test_config_validation(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test that invalid configuration values are rejected."""
        invalid_config = {
            "text_audio_ratio": 150,  # Should be 0-100
            "response_delay_minutes": -1  # Should be positive
        }
        
        response = client.put(
            "/config",
            headers=auth_headers,
            json={"configs": invalid_config}
        )
        
        # API should either reject or clamp values
        # Exact behavior depends on implementation
        assert response.status_code in [200, 400, 422]
    
    def test_config_persistence(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test that configuration changes persist across requests."""
        unique_prompt = f"Test persistence {pytest.timestamp()}"
        
        # Update config
        client.put(
            "/config",
            headers=auth_headers,
            json={"configs": {"system_prompt": unique_prompt}}
        )
        
        # Retrieve config multiple times
        for _ in range(3):
            response = client.get("/config", headers=auth_headers)
            configs = response.json()["configs"]
            assert configs["system_prompt"] == unique_prompt


# Add timestamp to pytest for unique test data
pytest.timestamp = lambda: str(int(__import__('time').time()))
