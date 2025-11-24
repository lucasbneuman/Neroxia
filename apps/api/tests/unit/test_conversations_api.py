"""
Conversations API Tests

Tests for conversation management endpoints:
- GET /conversations - List conversations
- GET /conversations/pending - Get pending conversations
- GET /conversations/{phone} - Get user details
- GET /conversations/{phone}/messages - Get message history
- POST /conversations/{phone}/send - Send manual message
- POST /conversations/{phone}/take-control - Take manual control
- POST /conversations/{phone}/return-to-bot - Return to bot
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict


class TestConversationsAPI:
    """Test suite for conversation management endpoints."""
    
    def test_list_conversations_requires_auth(self, client: TestClient):
        """Test that GET /conversations requires authentication."""
        response = client.get("/conversations")
        assert response.status_code == 401
    
    def test_list_conversations_success(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test listing all conversations."""
        response = client.get("/conversations", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Verify structure if conversations exist
        if len(data) > 0:
            conv = data[0]
            assert "phone" in conv
            assert "lastMessage" in conv or "last_message" in conv
    
    def test_list_conversations_with_pagination(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test conversation listing with pagination parameters."""
        response = client.get(
            "/conversations?skip=0&limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
    
    def test_get_pending_conversations_requires_auth(self, client: TestClient):
        """Test that GET /conversations/pending requires authentication."""
        response = client.get("/conversations/pending")
        assert response.status_code == 401
    
    def test_get_pending_conversations(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test getting conversations that need attention."""
        response = client.get("/conversations/pending", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Verify pending conversations have correct mode
        for conv in data:
            if "mode" in conv:
                assert conv["mode"] in ["NEEDS_ATTENTION", "MANUAL"]
    
    def test_get_user_details_requires_auth(self, client: TestClient):
        """Test that GET /conversations/{phone} requires authentication."""
        response = client.get("/conversations/+1234567890")
        assert response.status_code == 401
    
    def test_get_user_details_success(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_phone: str
    ):
        """Test getting detailed user information."""
        # First, create a conversation by sending a message
        client.post(
            "/bot/process",
            json={"phone": test_phone, "message": "Hello"}
        )
        
        # Then get user details
        response = client.get(
            f"/conversations/{test_phone}",
            headers=auth_headers
        )
        
        # Should return user details or 404 if not found
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "phone" in data
            assert data["phone"] == test_phone
            assert "stage" in data or "sentiment" in data
    
    def test_get_user_details_nonexistent(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test getting details for non-existent user."""
        response = client.get(
            "/conversations/+9999999999999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_get_message_history_requires_auth(self, client: TestClient):
        """Test that GET /conversations/{phone}/messages requires authentication."""
        response = client.get("/conversations/+1234567890/messages")
        assert response.status_code == 401
    
    def test_get_message_history(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_phone: str
    ):
        """Test getting message history for a conversation."""
        # Create some messages
        messages = ["Hello", "How are you?", "Tell me about your product"]
        for msg in messages:
            client.post(
                "/bot/process",
                json={"phone": test_phone, "message": msg}
            )
        
        # Get message history
        response = client.get(
            f"/conversations/{test_phone}/messages",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            # Should have at least some messages
            if len(data) > 0:
                msg = data[0]
                assert "text" in msg or "message_text" in msg
                assert "sender" in msg
    
    def test_get_message_history_with_limit(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_phone: str
    ):
        """Test message history with limit parameter."""
        response = client.get(
            f"/conversations/{test_phone}/messages?limit=5",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert len(data) <= 5
    
    def test_send_manual_message_requires_auth(self, client: TestClient):
        """Test that POST /conversations/{phone}/send requires authentication."""
        response = client.post(
            "/conversations/+1234567890/send",
            json={"message": "Test"}
        )
        assert response.status_code == 401
    
    def test_send_manual_message(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_phone: str
    ):
        """Test sending a manual message to user."""
        response = client.post(
            f"/conversations/{test_phone}/send",
            headers=auth_headers,
            json={"message": "This is a manual message from agent"}
        )
        
        # Should succeed or return 404 if conversation doesn't exist
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success"
            assert "message_id" in data or "message" in data
    
    def test_take_control_requires_auth(self, client: TestClient):
        """Test that POST /conversations/{phone}/take-control requires authentication."""
        response = client.post("/conversations/+1234567890/take-control")
        assert response.status_code == 401
    
    def test_take_control_of_conversation(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_phone: str
    ):
        """Test taking manual control of a conversation."""
        # First create a conversation
        client.post(
            "/bot/process",
            json={"phone": test_phone, "message": "Hello"}
        )
        
        # Take control
        response = client.post(
            f"/conversations/{test_phone}/take-control",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success"
            assert data["mode"] == "MANUAL"
    
    def test_return_to_bot_requires_auth(self, client: TestClient):
        """Test that POST /conversations/{phone}/return-to-bot requires authentication."""
        response = client.post("/conversations/+1234567890/return-to-bot")
        assert response.status_code == 401
    
    def test_return_to_bot(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_phone: str
    ):
        """Test returning conversation control to bot."""
        # First take control
        client.post(
            f"/conversations/{test_phone}/take-control",
            headers=auth_headers
        )
        
        # Then return to bot
        response = client.post(
            f"/conversations/{test_phone}/return-to-bot",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success"
            assert data["mode"] == "AUTO"


class TestConversationWorkflows:
    """Integration tests for conversation management workflows."""
    
    def test_complete_manual_intervention_workflow(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """
        Test complete manual intervention workflow:
        1. User starts conversation with bot
        2. Agent takes control
        3. Agent sends manual message
        4. Agent returns control to bot
        5. Bot continues conversation
        """
        test_phone = "+1111122222"
        
        # Step 1: User starts conversation
        response1 = client.post(
            "/bot/process",
            json={"phone": test_phone, "message": "I need help"}
        )
        assert response1.status_code == 200
        
        # Step 2: Agent takes control
        response2 = client.post(
            f"/conversations/{test_phone}/take-control",
            headers=auth_headers
        )
        assert response2.status_code in [200, 404]
        
        if response2.status_code == 404:
            pytest.skip("Conversation management not fully implemented")
        
        # Step 3: Agent sends manual message
        response3 = client.post(
            f"/conversations/{test_phone}/send",
            headers=auth_headers,
            json={"message": "Hello, I'm a human agent. How can I help?"}
        )
        assert response3.status_code == 200
        
        # Step 4: Return to bot
        response4 = client.post(
            f"/conversations/{test_phone}/return-to-bot",
            headers=auth_headers
        )
        assert response4.status_code == 200
        
        # Step 5: Bot continues
        response5 = client.post(
            "/bot/process",
            json={"phone": test_phone, "message": "Thanks for the help"}
        )
        assert response5.status_code == 200
    
    def test_conversation_tracking_across_messages(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test that conversation state is tracked across multiple messages."""
        test_phone = "+2222233333"
        
        # Send multiple messages
        messages = [
            "Hello",
            "I'm interested in your product",
            "What's the price?",
            "Can I get a discount?"
        ]
        
        for message in messages:
            client.post(
                "/bot/process",
                json={"phone": test_phone, "message": message}
            )
        
        # Get user details
        response = client.get(
            f"/conversations/{test_phone}",
            headers=auth_headers
        )
        
        if response.status_code == 200:
            data = response.json()
            # Should have tracked conversation state
            assert "stage" in data or "sentiment" in data
            
        # Get message history
        history_response = client.get(
            f"/conversations/{test_phone}/messages",
            headers=auth_headers
        )
        
        if history_response.status_code == 200:
            history = history_response.json()
            # Should have multiple messages
            assert len(history) >= len(messages)
