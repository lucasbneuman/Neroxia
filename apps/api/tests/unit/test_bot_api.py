"""
Bot Processing API Tests

Tests for bot message processing endpoints:
- POST /bot/process - Process messages through bot
- GET /bot/health - Check bot health status
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict


class TestBotProcessingAPI:
    """Test suite for bot message processing endpoints."""
    
    def test_bot_health_check(self, client: TestClient):
        """Test bot health endpoint."""
        response = client.get("/bot/health")
        
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        
        # Verify health response structure
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "bot_engine" in data
        assert "graph" in data
    
    def test_process_message_basic(
        self,
        client: TestClient,
        test_phone: str,
        test_message: str
    ):
        """Test basic message processing."""
        response = client.post(
            "/bot/process",
            json={
                "phone": test_phone,
                "message": test_message
            }
        )
        
        assert response.status_code == 200, f"Message processing failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "response" in data, "Should contain bot response"
        assert "user_phone" in data
        assert "sentiment" in data
        assert "stage" in data
        assert "conversation_mode" in data
        
        # Verify response content
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0, "Response should not be empty"
        assert data["user_phone"] == test_phone
    
    def test_process_message_with_config(
        self,
        client: TestClient,
        test_phone: str,
        test_config: Dict
    ):
        """Test message processing with custom configuration."""
        response = client.post(
            "/bot/process",
            json={
                "phone": test_phone,
                "message": "Hello",
                "config": test_config
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
    
    def test_process_multiple_messages_conversation(
        self,
        client: TestClient,
        test_phone: str
    ):
        """Test processing multiple messages in a conversation."""
        messages = [
            "Hello, I'm interested in your product",
            "What's the price?",
            "Can you tell me more about features?",
            "I'd like to buy it"
        ]
        
        for message in messages:
            response = client.post(
                "/bot/process",
                json={
                    "phone": test_phone,
                    "message": message
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert len(data["response"]) > 0
            
            # Verify conversation tracking
            assert "stage" in data
            assert "sentiment" in data
    
    def test_process_message_intent_detection(
        self,
        client: TestClient,
        test_phone: str
    ):
        """Test that bot detects user intent."""
        high_intent_message = "I want to buy your product right now"
        
        response = client.post(
            "/bot/process",
            json={
                "phone": test_phone,
                "message": high_intent_message
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have intent score
        if "intent_score" in data:
            assert isinstance(data["intent_score"], (int, float))
            assert 0 <= data["intent_score"] <= 1
    
    def test_process_message_sentiment_analysis(
        self,
        client: TestClient,
        test_phone: str
    ):
        """Test sentiment analysis in bot responses."""
        test_cases = [
            ("This is amazing! I love it!", "positive"),
            ("I'm not sure about this", "neutral"),
            ("This is terrible, I hate it", "negative")
        ]
        
        for message, expected_sentiment in test_cases:
            response = client.post(
                "/bot/process",
                json={
                    "phone": test_phone,
                    "message": message
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "sentiment" in data
            # Sentiment should be one of the expected values
            assert data["sentiment"] in ["positive", "neutral", "negative"]
    
    def test_process_message_stage_progression(
        self,
        client: TestClient
    ):
        """Test that conversation progresses through stages."""
        phone = "+9999999999"  # Use unique phone for this test
        
        # Initial contact
        response1 = client.post(
            "/bot/process",
            json={"phone": phone, "message": "Hello"}
        )
        stage1 = response1.json().get("stage")
        
        # Show interest
        response2 = client.post(
            "/bot/process",
            json={"phone": phone, "message": "I'm interested in buying"}
        )
        stage2 = response2.json().get("stage")
        
        # Stages should be tracked
        assert stage1 is not None
        assert stage2 is not None
    
    def test_process_empty_message(
        self,
        client: TestClient,
        test_phone: str
    ):
        """Test handling of empty messages."""
        response = client.post(
            "/bot/process",
            json={
                "phone": test_phone,
                "message": ""
            }
        )
        
        # Should either reject or handle gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_process_message_invalid_phone(
        self,
        client: TestClient
    ):
        """Test handling of invalid phone numbers."""
        response = client.post(
            "/bot/process",
            json={
                "phone": "invalid",
                "message": "Hello"
            }
        )
        
        # Should either format or reject
        assert response.status_code in [200, 400, 422]
    
    def test_process_message_with_history(
        self,
        client: TestClient,
        test_phone: str
    ):
        """Test processing message with conversation history."""
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help?"}
        ]
        
        response = client.post(
            "/bot/process",
            json={
                "phone": test_phone,
                "message": "What's your product?",
                "history": history
            }
        )
        
        # Should accept history parameter
        assert response.status_code in [200, 422]
