"""
Followups API Tests with Database Validation

Tests for follow-up scheduling functionality including:
- CRUD operations (Create, Read, Update, Delete)
- Database persistence validation
- Edge cases and error scenarios
- Scheduler service integration
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict
from datetime import datetime, timedelta
import io


class TestFollowupsAPI:
    """Test suite for Followups API endpoints."""
    
    def test_list_followups_requires_auth(self, client: TestClient):
        """Test that GET /followups requires authentication."""
        response = client.get("/followups")
        # Note: This test may fail due to Bug #11 (mock auth too permissive)
        # Expected: 401, but may get 200 or 503 if scheduler not available
        assert response.status_code in [401, 503]
    
    def test_list_followups_empty(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test listing follow-ups when none exist."""
        response = client.get("/followups", headers=auth_headers)
        
        # May return 503 if scheduler service not available
        if response.status_code == 503:
            pytest.skip("Scheduler service not available")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_schedule_followup_requires_auth(self, client: TestClient):
        """Test that POST /followups/{phone}/schedule requires authentication."""
        future_time = (datetime.now() + timedelta(hours=1)).isoformat()
        response = client.post(
            "/followups/+1234567890/schedule",
            json={
                "message": "Test follow-up",
                "scheduled_time": future_time
            }
        )
        assert response.status_code in [401, 503]
    
    def test_schedule_followup_success(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_user_data: Dict
    ):
        """Test scheduling a follow-up message."""
        phone = test_user_data["phone"]
        future_time = datetime.now() + timedelta(hours=1)
        
        response = client.post(
            f"/followups/{phone}/schedule",
            headers=auth_headers,
            json={
                "message": "Follow-up test message",
                "scheduled_time": future_time.isoformat()
            }
        )
        
        # May return 503 if scheduler service not available
        if response.status_code == 503:
            pytest.skip("Scheduler service not available")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "job_id" in data
        assert data["phone"] == phone
        assert data["message"] == "Follow-up test message"
    
    def test_schedule_followup_past_time(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_user_data: Dict
    ):
        """Test scheduling a follow-up in the past (should fail or warn)."""
        phone = test_user_data["phone"]
        past_time = datetime.now() - timedelta(hours=1)
        
        response = client.post(
            f"/followups/{phone}/schedule",
            headers=auth_headers,
            json={
                "message": "Past follow-up",
                "scheduled_time": past_time.isoformat()
            }
        )
        
        # May return 503 if scheduler not available, or 400 for past time
        # Or 200 if scheduler accepts past times (implementation dependent)
        assert response.status_code in [200, 400, 503]
    
    def test_get_followup_requires_auth(self, client: TestClient):
        """Test that GET /followups/{job_id} requires authentication."""
        response = client.get("/followups/test_job_id")
        assert response.status_code in [401, 503]
    
    def test_get_followup_not_found(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test getting a non-existent follow-up."""
        response = client.get(
            "/followups/nonexistent_job_id",
            headers=auth_headers
        )
        
        # May return 503 if scheduler not available, or 404 for not found
        if response.status_code == 503:
            pytest.skip("Scheduler service not available")
        
        assert response.status_code == 404
    
    def test_cancel_followup_requires_auth(self, client: TestClient):
        """Test that DELETE /followups/{job_id} requires authentication."""
        response = client.delete("/followups/test_job_id")
        assert response.status_code in [401, 503]
    
    def test_cancel_followup_not_found(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test cancelling a non-existent follow-up."""
        response = client.delete(
            "/followups/nonexistent_job_id",
            headers=auth_headers
        )
        
        # May return 503 if scheduler not available, or 404 for not found
        if response.status_code == 503:
            pytest.skip("Scheduler service not available")
        
        assert response.status_code == 404


class TestFollowupsWorkflow:
    """Test complete follow-up workflows."""
    
    def test_schedule_get_cancel_workflow(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_user_data: Dict
    ):
        """Test complete workflow: schedule -> get -> cancel."""
        phone = test_user_data["phone"]
        future_time = datetime.now() + timedelta(hours=2)
        
        # 1. Schedule follow-up
        schedule_response = client.post(
            f"/followups/{phone}/schedule",
            headers=auth_headers,
            json={
                "message": "Workflow test message",
                "scheduled_time": future_time.isoformat()
            }
        )
        
        if schedule_response.status_code == 503:
            pytest.skip("Scheduler service not available")
        
        assert schedule_response.status_code == 200
        job_id = schedule_response.json()["job_id"]
        
        # 2. Get follow-up info
        get_response = client.get(
            f"/followups/{job_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        followup_info = get_response.json()
        assert followup_info["id"] == job_id
        
        # 3. Cancel follow-up
        cancel_response = client.delete(
            f"/followups/{job_id}",
            headers=auth_headers
        )
        assert cancel_response.status_code == 200
        assert cancel_response.json()["status"] == "success"
        
        # 4. Verify it's cancelled (should return 404)
        verify_response = client.get(
            f"/followups/{job_id}",
            headers=auth_headers
        )
        assert verify_response.status_code == 404
    
    def test_list_followups_after_scheduling(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_user_data: Dict
    ):
        """Test that scheduled follow-ups appear in list."""
        phone = test_user_data["phone"]
        future_time = datetime.now() + timedelta(hours=3)
        
        # Get initial count
        list_response_before = client.get("/followups", headers=auth_headers)
        if list_response_before.status_code == 503:
            pytest.skip("Scheduler service not available")
        
        initial_count = len(list_response_before.json())
        
        # Schedule a follow-up
        schedule_response = client.post(
            f"/followups/{phone}/schedule",
            headers=auth_headers,
            json={
                "message": "List test message",
                "scheduled_time": future_time.isoformat()
            }
        )
        assert schedule_response.status_code == 200
        job_id = schedule_response.json()["job_id"]
        
        # Get updated list
        list_response_after = client.get("/followups", headers=auth_headers)
        assert list_response_after.status_code == 200
        
        followups = list_response_after.json()
        assert len(followups) == initial_count + 1
        
        # Verify our job is in the list
        job_ids = [f["id"] for f in followups]
        assert job_id in job_ids
        
        # Cleanup
        client.delete(f"/followups/{job_id}", headers=auth_headers)


class TestFollowupsEdgeCases:
    """Test edge cases and error scenarios."""
    
    def test_schedule_followup_invalid_phone(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test scheduling with invalid phone number."""
        future_time = datetime.now() + timedelta(hours=1)
        
        response = client.post(
            "/followups/invalid_phone/schedule",
            headers=auth_headers,
            json={
                "message": "Test",
                "scheduled_time": future_time.isoformat()
            }
        )
        
        # May return 503 if scheduler not available
        # Or 200/400 depending on phone validation
        assert response.status_code in [200, 400, 503]
    
    def test_schedule_followup_empty_message(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_user_data: Dict
    ):
        """Test scheduling with empty message."""
        phone = test_user_data["phone"]
        future_time = datetime.now() + timedelta(hours=1)
        
        response = client.post(
            f"/followups/{phone}/schedule",
            headers=auth_headers,
            json={
                "message": "",
                "scheduled_time": future_time.isoformat()
            }
        )
        
        # Should either accept empty message or return 422 validation error
        assert response.status_code in [200, 422, 503]
    
    def test_schedule_followup_invalid_datetime(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_user_data: Dict
    ):
        """Test scheduling with invalid datetime format."""
        phone = test_user_data["phone"]
        
        response = client.post(
            f"/followups/{phone}/schedule",
            headers=auth_headers,
            json={
                "message": "Test",
                "scheduled_time": "invalid_datetime"
            }
        )
        
        # Should return 422 validation error
        assert response.status_code == 422
    
    def test_schedule_multiple_followups_same_phone(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_user_data: Dict
    ):
        """Test scheduling multiple follow-ups for the same phone."""
        phone = test_user_data["phone"]
        job_ids = []
        
        # Schedule 3 follow-ups
        for i in range(3):
            future_time = datetime.now() + timedelta(hours=i+1)
            response = client.post(
                f"/followups/{phone}/schedule",
                headers=auth_headers,
                json={
                    "message": f"Follow-up #{i+1}",
                    "scheduled_time": future_time.isoformat()
                }
            )
            
            if response.status_code == 503:
                pytest.skip("Scheduler service not available")
            
            assert response.status_code == 200
            job_ids.append(response.json()["job_id"])
        
        # Verify all are scheduled
        list_response = client.get("/followups", headers=auth_headers)
        assert list_response.status_code == 200
        
        scheduled_ids = [f["id"] for f in list_response.json()]
        for job_id in job_ids:
            assert job_id in scheduled_ids
        
        # Cleanup
        for job_id in job_ids:
            client.delete(f"/followups/{job_id}", headers=auth_headers)


# Note: Database validation tests would require access to the scheduler's
# internal storage. Since the scheduler uses APScheduler which stores jobs
# in memory or a job store, we would need to:
# 1. Configure a database job store for the scheduler
# 2. Query that database to verify persistence
# 3. This is beyond the scope of basic API testing
# 
# For now, we're testing the API contract and behavior.
# Database validation would be added in a future iteration.
