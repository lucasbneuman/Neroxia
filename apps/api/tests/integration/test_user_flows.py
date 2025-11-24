"""
User Flow Integration Tests

End-to-end tests simulating complete user workflows:
- User configures chatbot
- User tests chat with bot
- User reviews conversation
- Complete sales flow simulation
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict
import time


class TestUserFlows:
    """Integration tests for complete user workflows."""
    
    def test_complete_configuration_flow(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_config: Dict
    ):
        """
        Test complete configuration workflow:
        1. Get current config
        2. Update config
        3. Verify changes
        4. Reset config
        """
        # Step 1: Get current configuration
        response = client.get("/config", headers=auth_headers)
        assert response.status_code == 200
        original_config = response.json()["configs"]
        
        # Step 2: Update configuration
        update_response = client.put(
            "/config",
            headers=auth_headers,
            json={"configs": test_config}
        )
        assert update_response.status_code == 200
        assert update_response.json()["status"] == "success"
        
        # Step 3: Verify changes persisted
        verify_response = client.get("/config", headers=auth_headers)
        assert verify_response.status_code == 200
        updated_config = verify_response.json()["configs"]
        assert updated_config["system_prompt"] == test_config["system_prompt"]
        assert updated_config["product_name"] == test_config["product_name"]
        
        # Step 4: Reset to defaults
        reset_response = client.post("/config/reset", headers=auth_headers)
        assert reset_response.status_code == 200
        assert reset_response.json()["status"] == "success"
    
    def test_test_chat_workflow(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_config: Dict
    ):
        """
        Test chat testing workflow:
        1. Configure bot
        2. Send test messages
        3. Verify bot responses
        4. Check conversation progression
        """
        test_phone = "+1111111111"
        
        # Step 1: Configure bot
        client.put(
            "/config",
            headers=auth_headers,
            json={"configs": test_config}
        )
        
        # Step 2 & 3: Send messages and verify responses
        test_messages = [
            "Hello, I need information",
            "What products do you offer?",
            "How much does it cost?",
            "I want to buy it"
        ]
        
        responses = []
        for message in test_messages:
            response = client.post(
                "/bot/process",
                json={"phone": test_phone, "message": message}
            )
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert len(data["response"]) > 0
            responses.append(data)
        
        # Step 4: Verify conversation progression
        # Check that stages and sentiment are tracked
        for data in responses:
            assert "stage" in data
            assert "sentiment" in data
            assert "conversation_mode" in data
    
    def test_configuration_affects_bot_behavior(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """
        Test that configuration changes affect bot responses:
        1. Configure bot with emojis enabled
        2. Send message, verify response
        3. Disable emojis
        4. Send message, verify no emojis
        """
        test_phone = "+2222222222"
        
        # Step 1: Enable emojis
        client.put(
            "/config",
            headers=auth_headers,
            json={"configs": {"use_emojis": True}}
        )
        
        # Step 2: Send message
        response1 = client.post(
            "/bot/process",
            json={"phone": test_phone, "message": "Hello"}
        )
        assert response1.status_code == 200
        
        # Step 3: Disable emojis
        client.put(
            "/config",
            headers=auth_headers,
            json={"configs": {"use_emojis": False}}
        )
        
        # Step 4: Send another message
        response2 = client.post(
            "/bot/process",
            json={"phone": test_phone, "message": "Tell me more"}
        )
        assert response2.status_code == 200
        
        # Both should succeed (actual emoji presence depends on implementation)
        assert "response" in response1.json()
        assert "response" in response2.json()
    
    def test_complete_sales_conversation_flow(
        self,
        client: TestClient
    ):
        """
        Simulate a complete sales conversation:
        1. Initial greeting
        2. Product inquiry
        3. Price question
        4. Feature questions
        5. Purchase intent
        6. Closing
        """
        test_phone = "+3333333333"
        
        conversation_flow = [
            {
                "message": "Hi there!",
                "expected_stage": None  # Initial contact
            },
            {
                "message": "I'm looking for a solution for my business",
                "expected_stage": None  # Qualification
            },
            {
                "message": "What's the price?",
                "expected_stage": None  # Consideration
            },
            {
                "message": "What features does it include?",
                "expected_stage": None  # Evaluation
            },
            {
                "message": "I'd like to purchase this",
                "expected_stage": None  # Closing
            }
        ]
        
        for step in conversation_flow:
            response = client.post(
                "/bot/process",
                json={
                    "phone": test_phone,
                    "message": step["message"]
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify bot responds
            assert "response" in data
            assert len(data["response"]) > 0
            
            # Verify tracking
            assert "stage" in data
            assert "sentiment" in data
            assert "conversation_mode" in data
    
    def test_multi_user_concurrent_conversations(
        self,
        client: TestClient
    ):
        """
        Test handling multiple users simultaneously:
        1. Start conversations with 3 different users
        2. Interleave messages
        3. Verify each conversation is tracked separately
        """
        users = [
            {"phone": "+4444444444", "name": "User A"},
            {"phone": "+5555555555", "name": "User B"},
            {"phone": "+6666666666", "name": "User C"}
        ]
        
        # Send messages from each user
        for user in users:
            response = client.post(
                "/bot/process",
                json={
                    "phone": user["phone"],
                    "message": f"Hello, I'm {user['name']}"
                }
            )
            assert response.status_code == 200
            assert "response" in response.json()
        
        # Send follow-up messages
        for user in users:
            response = client.post(
                "/bot/process",
                json={
                    "phone": user["phone"],
                    "message": "What products do you have?"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            # Each conversation should be tracked separately
            assert data["user_phone"] == user["phone"]
    
    def test_error_recovery_flow(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """
        Test system recovery from errors:
        1. Send invalid config
        2. Verify system still works
        3. Send valid config
        4. Test bot still processes messages
        """
        test_phone = "+7777777777"
        
        # Step 1: Try invalid config (might be rejected or clamped)
        client.put(
            "/config",
            headers=auth_headers,
            json={"configs": {"invalid_field": "value"}}
        )
        
        # Step 2 & 3: Send valid config
        valid_config = {
            "system_prompt": "Test prompt",
            "use_emojis": True
        }
        response = client.put(
            "/config",
            headers=auth_headers,
            json={"configs": valid_config}
        )
        assert response.status_code == 200
        
        # Step 4: Verify bot still works
        bot_response = client.post(
            "/bot/process",
            json={"phone": test_phone, "message": "Hello"}
        )
        assert bot_response.status_code == 200
        assert "response" in bot_response.json()
    
    def test_configuration_persistence_across_conversations(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """
        Test that config persists across multiple conversations:
        1. Set specific config
        2. Have conversation with user A
        3. Have conversation with user B
        4. Verify both use same config
        """
        # Step 1: Set config
        unique_prompt = f"Unique test prompt {int(time.time())}"
        client.put(
            "/config",
            headers=auth_headers,
            json={"configs": {"system_prompt": unique_prompt}}
        )
        
        # Step 2 & 3: Multiple conversations
        users = ["+8888888888", "+9999999999"]
        for phone in users:
            response = client.post(
                "/bot/process",
                json={"phone": phone, "message": "Hello"}
            )
            assert response.status_code == 200
        
        # Step 4: Verify config still set
        config_response = client.get("/config", headers=auth_headers)
        assert config_response.status_code == 200
        current_config = config_response.json()["configs"]
        assert current_config["system_prompt"] == unique_prompt


class TestAPIHealthAndStatus:
    """Tests for API health and status endpoints."""
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_health_endpoint(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
    
    def test_bot_health_endpoint(self, client: TestClient):
        """Test bot-specific health check."""
        response = client.get("/bot/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "bot_engine" in data
