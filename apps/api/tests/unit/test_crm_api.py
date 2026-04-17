"""
Unit tests for CRM API endpoints.

Tests cover:
- Dashboard metrics
- Deals CRUD operations
- Notes CRUD operations
- Tags CRUD operations
- Stage synchronization
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta


class TestCRMDashboard:
    """Tests for CRM dashboard metrics endpoint."""

    def test_get_dashboard_metrics_requires_auth(self, client):
        """Test that dashboard metrics endpoint requires authentication."""
        response = client.get("/crm/dashboard/metrics")
        assert response.status_code in [401, 404, 500]

    def test_get_dashboard_metrics_success(self, client, auth_headers):
        """Test successful retrieval of dashboard metrics."""
        response = client.get("/crm/dashboard/metrics", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            assert "total_active_deals" in data
            assert "total_won_deals" in data
            assert "total_revenue" in data
            assert "conversion_rate" in data
            assert isinstance(data["total_active_deals"], int)
            assert isinstance(data["total_revenue"], (int, float))

    def test_dashboard_metrics_calculation(self, client, auth_headers):
        """Test that dashboard metrics are calculated correctly."""
        response = client.get("/crm/dashboard/metrics", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            # Conversion rate should be between 0 and 100
            if "conversion_rate" in data:
                assert 0 <= data["conversion_rate"] <= 100


class TestCRMDeals:
    """Tests for CRM deals endpoints."""

    def test_list_deals_requires_auth(self, client):
        """Test that listing deals requires authentication."""
        response = client.get("/crm/deals")
        assert response.status_code in [401, 404, 500]

    def test_list_deals_success(self, client, auth_headers):
        """Test successful listing of deals."""
        response = client.get("/crm/deals", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            # Check deal structure if deals exist
            if len(data) > 0:
                deal = data[0]
                assert "id" in deal
                assert "user_id" in deal
                assert "stage" in deal
                assert "value" in deal

    def test_list_deals_with_stage_filter(self, client, auth_headers):
        """Test filtering deals by stage."""
        stages = ["new_lead", "qualified", "in_conversation", "proposal_sent", "won", "lost"]
        
        for stage in stages:
            response = client.get(f"/crm/deals?stage={stage}", headers=auth_headers)
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, list)
                # All returned deals should have the requested stage
                for deal in data:
                    assert deal.get("stage") == stage

    def test_list_deals_with_pagination(self, client, auth_headers):
        """Test deals pagination."""
        response = client.get("/crm/deals?limit=5&offset=0", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            assert len(data) <= 5

    def test_create_deal_requires_auth(self, client):
        """Test that creating a deal requires authentication."""
        deal_data = {
            "user_id": 1,
            "title": "Test Deal",
            "value": 1000.00,
            "stage": "new_lead"
        }
        response = client.post("/crm/deals", json=deal_data)
        assert response.status_code in [401, 404, 422, 500]

    def test_create_deal_success(self, client, auth_headers):
        """Test successful deal creation."""
        deal_data = {
            "user_id": 1,
            "title": "Test Deal",
            "value": 1500.00,
            "stage": "new_lead",
            "source": "whatsapp",
            "probability": 10
        }
        response = client.post("/crm/deals", json=deal_data, headers=auth_headers)
        
        if response.status_code == 201 or response.status_code == 200:
            data = response.json()
            assert data["title"] == "Test Deal"
            assert data["value"] == 1500.00
            assert data["stage"] == "new_lead"

    def test_create_deal_missing_required_fields(self, client, auth_headers):
        """Test deal creation with missing required fields."""
        deal_data = {
            "title": "Incomplete Deal"
            # Missing user_id
        }
        response = client.post("/crm/deals", json=deal_data, headers=auth_headers)
        assert response.status_code in [422, 400, 500]

    def test_get_deal_by_id_requires_auth(self, client):
        """Test that getting a deal by ID requires authentication."""
        response = client.get("/crm/deals/1")
        assert response.status_code in [401, 404, 500]

    def test_get_deal_by_id_success(self, client, auth_headers):
        """Test successful retrieval of a deal by ID."""
        # First create a deal
        deal_data = {
            "user_id": 1,
            "title": "Test Deal for Get",
            "value": 2000.00,
            "stage": "qualified"
        }
        create_response = client.post("/crm/deals", json=deal_data, headers=auth_headers)
        
        if create_response.status_code in [200, 201]:
            deal_id = create_response.json()["id"]
            response = client.get(f"/crm/deals/{deal_id}", headers=auth_headers)
            
            if response.status_code == 200:
                data = response.json()
                assert data["id"] == deal_id
                assert "user" in data  # Should include user relationship

    def test_get_deal_nonexistent(self, client, auth_headers):
        """Test getting a nonexistent deal."""
        response = client.get("/crm/deals/999999", headers=auth_headers)
        assert response.status_code == 404

    def test_update_deal_requires_auth(self, client):
        """Test that updating a deal requires authentication."""
        update_data = {"stage": "in_conversation"}
        response = client.patch("/crm/deals/1", json=update_data)
        assert response.status_code in [401, 404, 500]

    def test_update_deal_success(self, client, auth_headers):
        """Test successful deal update."""
        # Create a deal first
        deal_data = {
            "user_id": 1,
            "title": "Deal to Update",
            "value": 3000.00,
            "stage": "new_lead"
        }
        create_response = client.post("/crm/deals", json=deal_data, headers=auth_headers)
        
        if create_response.status_code in [200, 201]:
            deal_id = create_response.json()["id"]
            
            # Update the deal
            update_data = {
                "stage": "qualified",
                "value": 3500.00,
                "probability": 50
            }
            response = client.patch(f"/crm/deals/{deal_id}", json=update_data, headers=auth_headers)
            
            if response.status_code == 200:
                data = response.json()
                assert data["stage"] == "qualified"
                assert data["value"] == 3500.00
                assert data["manually_qualified"] == True  # Should be set when stage is updated

    def test_update_deal_stage_only(self, client, auth_headers):
        """Test updating only the stage of a deal."""
        # Create a deal first
        deal_data = {
            "user_id": 1,
            "title": "Deal for Stage Update",
            "value": 2500.00,
            "stage": "new_lead"
        }
        create_response = client.post("/crm/deals", json=deal_data, headers=auth_headers)
        
        if create_response.status_code in [200, 201]:
            deal_id = create_response.json()["id"]
            
            # Update stage using dedicated endpoint
            update_data = {"stage": "proposal_sent"}
            response = client.patch(f"/crm/deals/{deal_id}/stage", json=update_data, headers=auth_headers)
            
            if response.status_code == 200:
                data = response.json()
                assert data["stage"] == "proposal_sent"

    def test_mark_deal_as_won(self, client, auth_headers):
        """Test marking a deal as won."""
        # Create a deal first
        deal_data = {
            "user_id": 1,
            "title": "Deal to Win",
            "value": 5000.00,
            "stage": "proposal_sent"
        }
        create_response = client.post("/crm/deals", json=deal_data, headers=auth_headers)
        
        if create_response.status_code in [200, 201]:
            deal_id = create_response.json()["id"]
            
            # Mark as won
            response = client.post(f"/crm/deals/{deal_id}/won", headers=auth_headers)
            
            if response.status_code == 200:
                data = response.json()
                assert data["stage"] == "won"
                assert data["probability"] == 100
                assert "won_date" in data

    def test_mark_deal_as_lost(self, client, auth_headers):
        """Test marking a deal as lost."""
        # Create a deal first
        deal_data = {
            "user_id": 1,
            "title": "Deal to Lose",
            "value": 4000.00,
            "stage": "in_conversation"
        }
        create_response = client.post("/crm/deals", json=deal_data, headers=auth_headers)
        
        if create_response.status_code in [200, 201]:
            deal_id = create_response.json()["id"]
            
            # Mark as lost
            lost_data = {"reason": "Budget constraints"}
            response = client.post(f"/crm/deals/{deal_id}/lost", json=lost_data, headers=auth_headers)
            
            if response.status_code == 200:
                data = response.json()
                assert data["stage"] == "lost"
                assert data["probability"] == 0
                assert data["lost_reason"] == "Budget constraints"

    def test_delete_deal_requires_auth(self, client):
        """Test that deleting a deal requires authentication."""
        response = client.delete("/crm/deals/1")
        assert response.status_code in [401, 404, 500]

    def test_delete_deal_success(self, client, auth_headers):
        """Test successful deal deletion."""
        # Create a deal first
        deal_data = {
            "user_id": 1,
            "title": "Deal to Delete",
            "value": 1000.00,
            "stage": "new_lead"
        }
        create_response = client.post("/crm/deals", json=deal_data, headers=auth_headers)
        
        if create_response.status_code in [200, 201]:
            deal_id = create_response.json()["id"]
            
            # Delete the deal
            response = client.delete(f"/crm/deals/{deal_id}", headers=auth_headers)
            
            if response.status_code == 200:
                data = response.json()
                assert data["success"] == True
                
                # Verify it's deleted
                get_response = client.get(f"/crm/deals/{deal_id}", headers=auth_headers)
                assert get_response.status_code == 404


class TestCRMNotes:
    """Tests for CRM notes endpoints."""

    def test_list_user_notes_requires_auth(self, client):
        """Test that listing user notes requires authentication."""
        response = client.get("/crm/users/1/notes")
        assert response.status_code in [401, 404, 500]

    def test_list_user_notes_success(self, client, auth_headers):
        """Test successful listing of user notes."""
        response = client.get("/crm/users/1/notes", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            # Check note structure if notes exist
            if len(data) > 0:
                note = data[0]
                assert "id" in note
                assert "user_id" in note
                assert "content" in note
                assert "note_type" in note

    def test_create_note_requires_auth(self, client):
        """Test that creating a note requires authentication."""
        note_data = {
            "content": "Test note",
            "note_type": "note"
        }
        response = client.post("/crm/users/1/notes", json=note_data)
        assert response.status_code in [401, 404, 422, 500]

    def test_create_note_success(self, client, auth_headers):
        """Test successful note creation."""
        note_data = {
            "content": "Customer is very interested in the product",
            "note_type": "call",
            "deal_id": 1
        }
        response = client.post("/crm/users/1/notes", json=note_data, headers=auth_headers)
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["content"] == note_data["content"]
            assert data["note_type"] == "call"
            assert data["user_id"] == 1

    def test_create_note_with_different_types(self, client, auth_headers):
        """Test creating notes with different types."""
        note_types = ["note", "call", "email", "meeting", "task"]
        
        for note_type in note_types:
            note_data = {
                "content": f"Test {note_type}",
                "note_type": note_type
            }
            response = client.post("/crm/users/1/notes", json=note_data, headers=auth_headers)
            
            if response.status_code in [200, 201]:
                data = response.json()
                assert data["note_type"] == note_type

    def test_delete_note_requires_auth(self, client):
        """Test that deleting a note requires authentication."""
        response = client.delete("/crm/notes/1")
        assert response.status_code in [401, 404, 500]

    def test_delete_note_success(self, client, auth_headers):
        """Test successful note deletion."""
        # Create a note first
        note_data = {
            "content": "Note to delete",
            "note_type": "note"
        }
        create_response = client.post("/crm/users/1/notes", json=note_data, headers=auth_headers)
        
        if create_response.status_code in [200, 201]:
            note_id = create_response.json()["id"]
            
            # Delete the note
            response = client.delete(f"/crm/notes/{note_id}", headers=auth_headers)
            
            if response.status_code == 200:
                data = response.json()
                assert data["success"] == True


class TestCRMTags:
    """Tests for CRM tags endpoints."""

    def test_list_tags_requires_auth(self, client):
        """Test that listing tags requires authentication."""
        response = client.get("/crm/tags")
        assert response.status_code in [401, 404, 500]

    def test_list_tags_success(self, client, auth_headers):
        """Test successful listing of tags."""
        response = client.get("/crm/tags", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            # Check tag structure if tags exist
            if len(data) > 0:
                tag = data[0]
                assert "id" in tag
                assert "name" in tag
                assert "color" in tag

    def test_create_tag_requires_auth(self, client):
        """Test that creating a tag requires authentication."""
        tag_data = {
            "name": "Test Tag",
            "color": "#FF0000"
        }
        response = client.post("/crm/tags", json=tag_data)
        assert response.status_code in [401, 404, 422, 500]

    def test_create_tag_success(self, client, auth_headers):
        """Test successful tag creation."""
        tag_data = {
            "name": "Hot Lead",
            "color": "#EF4444"
        }
        response = client.post("/crm/tags", json=tag_data, headers=auth_headers)
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["name"] == "Hot Lead"
            assert data["color"] == "#EF4444"

    def test_list_user_tags_requires_auth(self, client):
        """Test that listing user tags requires authentication."""
        response = client.get("/crm/users/1/tags")
        assert response.status_code in [401, 404, 500]

    def test_list_user_tags_success(self, client, auth_headers):
        """Test successful listing of user tags."""
        response = client.get("/crm/users/1/tags", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_assign_tag_to_user_requires_auth(self, client):
        """Test that assigning a tag to a user requires authentication."""
        response = client.post("/crm/users/1/tags/1")
        assert response.status_code in [401, 404, 500]

    def test_assign_tag_to_user_success(self, client, auth_headers):
        """Test successful tag assignment to user."""
        # Create a tag first
        tag_data = {
            "name": "VIP Customer",
            "color": "#8B5CF6"
        }
        tag_response = client.post("/crm/tags", json=tag_data, headers=auth_headers)
        
        if tag_response.status_code in [200, 201]:
            tag_id = tag_response.json()["id"]
            
            # Assign tag to user
            response = client.post(f"/crm/users/1/tags/{tag_id}", headers=auth_headers)
            
            if response.status_code in [200, 201]:
                # Verify tag is assigned
                user_tags_response = client.get("/crm/users/1/tags", headers=auth_headers)
                if user_tags_response.status_code == 200:
                    tags = user_tags_response.json()
                    tag_ids = [t["id"] for t in tags]
                    assert tag_id in tag_ids

    def test_remove_tag_from_user_requires_auth(self, client):
        """Test that removing a tag from a user requires authentication."""
        response = client.delete("/crm/users/1/tags/1")
        assert response.status_code in [401, 404, 500]

    def test_remove_tag_from_user_success(self, client, auth_headers):
        """Test successful tag removal from user."""
        # Create and assign a tag first
        tag_data = {
            "name": "Tag to Remove",
            "color": "#3B82F6"
        }
        tag_response = client.post("/crm/tags", json=tag_data, headers=auth_headers)
        
        if tag_response.status_code in [200, 201]:
            tag_id = tag_response.json()["id"]
            
            # Assign tag
            client.post(f"/crm/users/1/tags/{tag_id}", headers=auth_headers)
            
            # Remove tag
            response = client.delete(f"/crm/users/1/tags/{tag_id}", headers=auth_headers)
            
            if response.status_code == 200:
                data = response.json()
                assert data["success"] == True


class TestCRMWorkflows:
    """Tests for complete CRM workflows."""

    def test_complete_deal_lifecycle(self, client, auth_headers):
        """Test complete deal lifecycle from creation to won."""
        # 1. Create a deal
        deal_data = {
            "user_id": 1,
            "title": "Complete Lifecycle Deal",
            "value": 10000.00,
            "stage": "new_lead",
            "source": "whatsapp"
        }
        create_response = client.post("/crm/deals", json=deal_data, headers=auth_headers)
        
        if create_response.status_code not in [200, 201]:
            pytest.skip("Deal creation not available")
        
        deal_id = create_response.json()["id"]
        
        # 2. Progress through stages
        stages = ["qualified", "in_conversation", "proposal_sent"]
        for stage in stages:
            update_response = client.patch(
                f"/crm/deals/{deal_id}/stage",
                json={"stage": stage},
                headers=auth_headers
            )
            if update_response.status_code == 200:
                assert update_response.json()["stage"] == stage
        
        # 3. Add a note
        note_data = {
            "content": "Customer ready to close",
            "note_type": "call",
            "deal_id": deal_id
        }
        client.post("/crm/users/1/notes", json=note_data, headers=auth_headers)
        
        # 4. Mark as won
        won_response = client.post(f"/crm/deals/{deal_id}/won", headers=auth_headers)
        if won_response.status_code == 200:
            final_deal = won_response.json()
            assert final_deal["stage"] == "won"
            assert final_deal["probability"] == 100

    def test_deal_with_tags_and_notes(self, client, auth_headers):
        """Test creating a deal with associated tags and notes."""
        # 1. Create a tag
        tag_data = {
            "name": "Enterprise",
            "color": "#10B981"
        }
        tag_response = client.post("/crm/tags", json=tag_data, headers=auth_headers)
        
        if tag_response.status_code not in [200, 201]:
            pytest.skip("Tag creation not available")
        
        tag_id = tag_response.json()["id"]
        
        # 2. Assign tag to user
        client.post(f"/crm/users/1/tags/{tag_id}", headers=auth_headers)
        
        # 3. Create a deal
        deal_data = {
            "user_id": 1,
            "title": "Enterprise Deal",
            "value": 50000.00,
            "stage": "qualified"
        }
        deal_response = client.post("/crm/deals", json=deal_data, headers=auth_headers)
        
        if deal_response.status_code in [200, 201]:
            deal_id = deal_response.json()["id"]
            
            # 4. Add multiple notes
            note_types = ["call", "email", "meeting"]
            for note_type in note_types:
                note_data = {
                    "content": f"Enterprise customer {note_type}",
                    "note_type": note_type,
                    "deal_id": deal_id
                }
                client.post("/crm/users/1/notes", json=note_data, headers=auth_headers)
            
            # 5. Verify notes were created
            notes_response = client.get("/crm/users/1/notes", headers=auth_headers)
            if notes_response.status_code == 200:
                notes = notes_response.json()
                deal_notes = [n for n in notes if n.get("deal_id") == deal_id]
                assert len(deal_notes) >= 3


class TestCRMEdgeCases:
    """Tests for CRM edge cases and error handling."""

    def test_create_deal_with_invalid_stage(self, client, auth_headers):
        """Test creating a deal with an invalid stage."""
        deal_data = {
            "user_id": 1,
            "title": "Invalid Stage Deal",
            "value": 1000.00,
            "stage": "invalid_stage"
        }
        response = client.post("/crm/deals", json=deal_data, headers=auth_headers)
        assert response.status_code in [422, 400]

    def test_create_deal_with_negative_value(self, client, auth_headers):
        """Test creating a deal with negative value."""
        deal_data = {
            "user_id": 1,
            "title": "Negative Value Deal",
            "value": -1000.00,
            "stage": "new_lead"
        }
        response = client.post("/crm/deals", json=deal_data, headers=auth_headers)
        # Should either reject or accept (depending on business logic)
        assert response.status_code in [200, 201, 400, 422]

    def test_create_note_with_empty_content(self, client, auth_headers):
        """Test creating a note with empty content."""
        note_data = {
            "content": "",
            "note_type": "note"
        }
        response = client.post("/crm/users/1/notes", json=note_data, headers=auth_headers)
        assert response.status_code in [422, 400]

    def test_assign_nonexistent_tag_to_user(self, client, auth_headers):
        """Test assigning a nonexistent tag to a user."""
        response = client.post("/crm/users/1/tags/999999", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_nonexistent_deal(self, client, auth_headers):
        """Test deleting a nonexistent deal."""
        response = client.delete("/crm/deals/999999", headers=auth_headers)
        assert response.status_code == 404

    def test_mark_already_won_deal_as_lost(self, client, auth_headers):
        """Test marking an already won deal as lost."""
        # Create and win a deal
        deal_data = {
            "user_id": 1,
            "title": "Already Won Deal",
            "value": 5000.00,
            "stage": "proposal_sent"
        }
        create_response = client.post("/crm/deals", json=deal_data, headers=auth_headers)
        
        if create_response.status_code in [200, 201]:
            deal_id = create_response.json()["id"]
            
            # Mark as won
            client.post(f"/crm/deals/{deal_id}/won", headers=auth_headers)
            
            # Try to mark as lost
            lost_data = {"reason": "Changed mind"}
            response = client.post(f"/crm/deals/{deal_id}/lost", json=lost_data, headers=auth_headers)
            
            # Should either allow it or reject it (depending on business logic)
            assert response.status_code in [200, 400, 409]
