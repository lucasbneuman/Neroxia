"""
Pytest configuration and fixtures for API testing.

This module provides shared fixtures for all test files including:
- Test client setup
- Authentication tokens
- Database cleanup
- Test data factories
"""

import pytest
from fastapi.testclient import TestClient
from typing import Generator, Dict
import sys
from pathlib import Path

# Add parent directory (apps/api) to Python path so 'src' can be imported as a package
api_dir = Path(__file__).parent.parent
if str(api_dir) not in sys.path:
    sys.path.insert(0, str(api_dir))

# Now import from src package
from src.main import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """
    Create a test client for the FastAPI application.
    
    Yields:
        TestClient: FastAPI test client instance
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def auth_token(client: TestClient) -> str:
    """
    Obtain an authentication token for protected endpoints.
    
    Args:
        client: FastAPI test client
        
    Returns:
        str: JWT authentication token
    """
    # Login with real test credentials from Supabase
    response = client.post(
        "/auth/login",
        json={
            "email": "automationinnova640@gmail.com",
            "password": "automation.innova$864."
        }
    )
    
    assert response.status_code == 200, f"Login failed: {response.text}"
    
    data = response.json()
    token = data.get("access_token")
    assert token is not None, "No access token in response"
    
    return token


@pytest.fixture(scope="session")
def auth_headers(auth_token: str) -> Dict[str, str]:
    """
    Create authorization headers with Bearer token.
    
    Args:
        auth_token: JWT authentication token
        
    Returns:
        Dict[str, str]: Headers dictionary with Authorization
    """
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def test_phone() -> str:
    """
    Provide a consistent test phone number.
    
    Returns:
        str: Test phone number with country code
    """
    return "+1234567890"


@pytest.fixture(scope="function")
def test_config() -> Dict:
    """
    Provide test configuration data.
    
    Returns:
        Dict: Test configuration settings
    """
    return {
        "system_prompt": "You are a test sales assistant",
        "welcome_message": "Test welcome message",
        "product_name": "Test Product",
        "product_price": "$99",
        "use_emojis": True,
        "text_audio_ratio": 0,
        "response_delay_minutes": 0.5,
        "max_words_per_response": 100
    }


@pytest.fixture(scope="function")
def test_message() -> str:
    """
    Provide a test message for bot processing.
    
    Returns:
        str: Test message text
    """
    return "Hello, I'm interested in your product"


@pytest.fixture(autouse=True, scope="function")
def cleanup_test_data(client: TestClient, auth_headers: Dict[str, str]):
    """
    Cleanup test data after each test.
    
    This fixture runs automatically after each test to ensure clean state.
    """
    yield
    # Cleanup logic can be added here if needed
    # For example: reset config, clear test conversations, etc.
