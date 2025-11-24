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
    
    For tests, we use a mock token since Supabase auth may not be available
    in test environment.
    
    Args:
        client: FastAPI test client
        
    Returns:
        str: JWT authentication token (mock for tests)
    """
    # For now, return a mock token
    # TODO: Implement proper test authentication when Supabase test environment is ready
    # The actual tests will mock the auth dependency, so this token just needs to exist
    return "mock_test_token_for_api_tests"


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


# Mock the get_current_user dependency for tests
@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    """
    Mock dependencies for all tests.
    This allows tests to run without real Supabase authentication or database.
    """
    from src.routers.auth import get_current_user
    from src.database import get_db
    from unittest.mock import AsyncMock
    
    async def mock_get_current_user():
        """Mock user for testing."""
        return {
            "id": "test-user-id-123",
            "email": "test@example.com",
            "user_metadata": {"name": "Test User"},
            "created_at": "2024-01-01T00:00:00Z"
        }
    
    async def mock_get_db():
        """Mock database session for testing."""
        # Create a mock database session
        db = AsyncMock()
        try:
            yield db
        finally:
            pass
    
    # Replace the dependencies in the app
    from src.main import app
    
    # Override auth dependency
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    # Override database dependency
    app.dependency_overrides[get_db] = mock_get_db
    
    yield
    
    # Clean up
    app.dependency_overrides.clear()


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


# ============================================================================
# DATABASE VALIDATION FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
async def db_session():
    """
    Provide a real database session for integration tests with database validation.
    
    This fixture creates a real database connection and automatically rolls back
    all changes after the test completes, ensuring test isolation.
    
    Yields:
        AsyncSession: SQLAlchemy async session
    """
    from src.database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession
    
    # Get a real database session
    async for session in get_db():
        try:
            yield session
        finally:
            # Rollback any changes made during the test
            await session.rollback()
            await session.close()


@pytest.fixture(scope="function")
async def clean_db(db_session):
    """
    Clean database before test and provide session.
    
    This fixture deletes all test data before running the test,
    ensuring a clean slate for database validation tests.
    
    Args:
        db_session: Database session from db_session fixture
        
    Yields:
        AsyncSession: Clean database session
    """
    from sqlalchemy import text
    
    # Delete test data (phone numbers starting with '+test')
    try:
        await db_session.execute(text("DELETE FROM messages WHERE phone LIKE '+test%'"))
        await db_session.execute(text("DELETE FROM conversations WHERE phone LIKE '+test%'"))
        await db_session.execute(text("DELETE FROM users WHERE phone LIKE '+test%'"))
        await db_session.execute(text("DELETE FROM followups WHERE phone LIKE '+test%'"))
        await db_session.execute(text("DELETE FROM handoffs WHERE phone LIKE '+test%'"))
        await db_session.commit()
    except Exception as e:
        # If tables don't exist or other error, just continue
        await db_session.rollback()
    
    yield db_session


@pytest.fixture(scope="function")
def test_user_data() -> Dict:
    """
    Provide test user data for database validation.
    
    Returns:
        Dict: Test user data
    """
    return {
        "phone": "+test1234567890",
        "name": "Test User",
        "email": "test@example.com",
        "stage": "initial_contact"
    }


@pytest.fixture(scope="function")
def test_conversation_data(test_user_data: Dict) -> Dict:
    """
    Provide test conversation data for database validation.
    
    Args:
        test_user_data: Test user data fixture
        
    Returns:
        Dict: Test conversation data
    """
    return {
        "phone": test_user_data["phone"],
        "status": "active",
        "manual_control": False
    }


@pytest.fixture(scope="function")
def test_message_data(test_user_data: Dict) -> Dict:
    """
    Provide test message data for database validation.
    
    Args:
        test_user_data: Test user data fixture
        
    Returns:
        Dict: Test message data
    """
    return {
        "phone": test_user_data["phone"],
        "message": "Hello, this is a test message",
        "sender": "user",
        "timestamp": "2024-01-01T00:00:00Z"
    }


@pytest.fixture(scope="function")
def test_followup_data(test_user_data: Dict) -> Dict:
    """
    Provide test follow-up data for database validation.
    
    Args:
        test_user_data: Test user data fixture
        
    Returns:
        Dict: Test follow-up data
    """
    return {
        "phone": test_user_data["phone"],
        "scheduled_time": "2024-12-31T23:59:59Z",
        "message": "Follow-up test message",
        "status": "pending"
    }


@pytest.fixture(scope="function")
def test_handoff_data(test_user_data: Dict) -> Dict:
    """
    Provide test handoff data for database validation.
    
    Args:
        test_user_data: Test user data fixture
        
    Returns:
        Dict: Test handoff data
    """
    return {
        "phone": test_user_data["phone"],
        "reason": "Customer requested human agent",
        "status": "pending",
        "assigned_agent": None
    }

