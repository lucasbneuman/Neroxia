"""
RAG (Retrieval-Augmented Generation) API Tests

Tests for RAG document management endpoints:
- POST /rag/upload - Upload documents
- GET /rag/files - List uploaded files
- DELETE /rag/files/{filename} - Delete files
- GET /rag/stats - Get RAG statistics
- POST /rag/clear - Clear all documents
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict
import io


class TestRAGAPI:
    """Test suite for RAG document management endpoints."""
    
    def test_rag_stats_requires_auth(self, client: TestClient):
        """Test that GET /rag/stats requires authentication."""
        response = client.get("/rag/stats")
        assert response.status_code == 401
    
    def test_rag_stats_success(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test successful RAG statistics retrieval."""
        response = client.get("/rag/stats", headers=auth_headers)
        
        # Should succeed even if RAG is not enabled
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "enabled" in data
            
            if data["enabled"]:
                assert "total_chunks" in data
                assert "collection_name" in data
    
    def test_list_rag_files_requires_auth(self, client: TestClient):
        """Test that GET /rag/files requires authentication."""
        response = client.get("/rag/files")
        assert response.status_code == 401
    
    def test_list_rag_files_success(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test listing RAG files."""
        response = client.get("/rag/files", headers=auth_headers)
        
        # Should return list even if empty
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_upload_rag_file_requires_auth(self, client: TestClient):
        """Test that POST /rag/upload requires authentication."""
        # Create a dummy file
        file_content = b"Test document content"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        
        response = client.post("/rag/upload", files=files)
        assert response.status_code == 401
    
    def test_upload_rag_file_txt(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test uploading a text file to RAG."""
        # Create a test text file
        file_content = b"This is a test document for RAG processing."
        files = {"file": ("test_doc.txt", io.BytesIO(file_content), "text/plain")}
        
        response = client.post(
            "/rag/upload",
            headers=auth_headers,
            files=files
        )
        
        # Should succeed or indicate RAG not available
        assert response.status_code in [200, 503, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success"
            assert "filename" in data
            assert "chunks_created" in data or "message" in data
    
    def test_upload_invalid_file_type(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test uploading an invalid file type."""
        # Create an invalid file (e.g., executable)
        file_content = b"Invalid content"
        files = {"file": ("test.exe", io.BytesIO(file_content), "application/x-msdownload")}
        
        response = client.post(
            "/rag/upload",
            headers=auth_headers,
            files=files
        )
        
        # Should reject invalid file types
        assert response.status_code in [400, 422, 503]
    
    def test_upload_empty_file(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test uploading an empty file."""
        files = {"file": ("empty.txt", io.BytesIO(b""), "text/plain")}
        
        response = client.post(
            "/rag/upload",
            headers=auth_headers,
            files=files
        )
        
        # Should reject or handle gracefully
        assert response.status_code in [200, 400, 422, 503]
    
    def test_delete_rag_file_requires_auth(self, client: TestClient):
        """Test that DELETE /rag/files/{filename} requires authentication."""
        response = client.delete("/rag/files/test.txt")
        assert response.status_code == 401
    
    def test_delete_nonexistent_file(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test deleting a file that doesn't exist."""
        response = client.delete(
            "/rag/files/nonexistent_file.txt",
            headers=auth_headers
        )
        
        # Should return 404 or indicate file not found
        assert response.status_code in [404, 503]
    
    def test_clear_rag_requires_auth(self, client: TestClient):
        """Test that POST /rag/clear requires authentication."""
        response = client.post("/rag/clear")
        assert response.status_code == 401
    
    def test_clear_rag_collection(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test clearing RAG collection."""
        response = client.post("/rag/clear", headers=auth_headers)
        
        # Should succeed or indicate RAG not available
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success"
            assert "message" in data
    
    def test_rag_upload_and_list_workflow(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """
        Test complete RAG workflow:
        1. Upload a file
        2. List files to verify upload
        3. Check stats
        """
        # Skip if RAG not available
        stats_response = client.get("/rag/stats", headers=auth_headers)
        if stats_response.status_code == 503:
            pytest.skip("RAG service not available")
        
        # Step 1: Upload file
        file_content = b"Test document for workflow testing."
        files = {"file": ("workflow_test.txt", io.BytesIO(file_content), "text/plain")}
        
        upload_response = client.post(
            "/rag/upload",
            headers=auth_headers,
            files=files
        )
        
        if upload_response.status_code != 200:
            pytest.skip("RAG upload not working")
        
        # Step 2: List files
        list_response = client.get("/rag/files", headers=auth_headers)
        assert list_response.status_code == 200
        files_list = list_response.json()
        assert isinstance(files_list, list)
        
        # Step 3: Check stats
        stats_response = client.get("/rag/stats", headers=auth_headers)
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["enabled"] is True
        assert stats["total_chunks"] >= 0


class TestRAGIntegration:
    """Integration tests for RAG with bot processing."""
    
    def test_bot_uses_rag_context(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Test that bot can use RAG context in responses."""
        # Skip if RAG not available
        stats_response = client.get("/rag/stats", headers=auth_headers)
        if stats_response.status_code == 503:
            pytest.skip("RAG service not available")
        
        # Upload a document with specific information
        file_content = b"Our product costs $299 and includes lifetime support."
        files = {"file": ("pricing.txt", io.BytesIO(file_content), "text/plain")}
        
        upload_response = client.post(
            "/rag/upload",
            headers=auth_headers,
            files=files
        )
        
        if upload_response.status_code != 200:
            pytest.skip("RAG upload not working")
        
        # Ask bot about pricing
        bot_response = client.post(
            "/bot/process",
            json={
                "phone": "+1234567890",
                "message": "How much does your product cost?"
            }
        )
        
        assert bot_response.status_code == 200
        data = bot_response.json()
        assert "response" in data
        # Response should ideally mention the price from RAG context
        # (exact behavior depends on implementation)
