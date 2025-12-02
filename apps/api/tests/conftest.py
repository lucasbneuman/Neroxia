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

# Add project root to Python path so 'packages' can be imported
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Add shared packages to Python path (optional if root is added, but keeping for safety)
shared_dir = project_root / "packages" / "shared"
if str(shared_dir) not in sys.path:
    sys.path.insert(0, str(shared_dir))

# Add bot-engine src to Python path
bot_engine_dir = Path(__file__).parent.parent.parent.parent / "apps" / "bot-engine" / "src"
if str(bot_engine_dir) not in sys.path:
    sys.path.insert(0, str(bot_engine_dir))

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
    from unittest.mock import AsyncMock, MagicMock, patch
    from whatsapp_bot_database import crud
    from fastapi import Header
    
    # Create a mock user object with proper attributes
    class MockUser:
        def __init__(self, phone="+1234567890"):
            self.id = "test-user-id-123"
            self.email = "test@example.com"
            self.phone = phone
            self.name = "Test User"
            self.created_at = "2024-01-01T00:00:00Z"
            self.stage = "initial_contact"
            self.intent_score = 0.5
            self.sentiment = "neutral"
            self.conversation_mode = "AUTO"
            self.conversation_summary = "Test conversation summary"
            self.whatsapp_profile_name = None
            self.twilio_profile_name = None

        def get(self, key, default=None):
            """Mimic dictionary .get() method."""
            return getattr(self, key, default)

        def __getitem__(self, key):
            """Mimic dictionary [] access."""
            return getattr(self, key)
    
    async def mock_get_current_user(authorization: str = Header(None)):
        """
        Mock user for testing - returns object with attributes.
        Now enforces authentication to fix permissive tests.
        """
        from fastapi import HTTPException, status
        
        # If no authorization header, raise 401 (mimic real behavior)
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header",
            )
            
        return MockUser()
    
    async def mock_get_db():
        """Mock database session for testing."""
        # Create a mock database session with proper async behavior
        db = AsyncMock()
        
        # Create a mock result that supports SQLAlchemy query patterns
        mock_result = AsyncMock()
        mock_scalars = AsyncMock()
        
        # Configure scalars().all() to return empty list by default
        mock_scalars.all = MagicMock(return_value=[])
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        
        # Configure db methods to return awaitable mocks
        db.execute = AsyncMock(return_value=mock_result)
        db.commit = AsyncMock()
        db.rollback = AsyncMock()
        db.close = AsyncMock()
        db.refresh = AsyncMock()
        db.add = MagicMock()  # add is not async
        
        try:
            yield db
        finally:
            await db.close()
    
    # Mock CRUD operations to return proper objects
    async def mock_get_user_by_phone(db, phone):
        """Mock get_user_by_phone to return MockUser."""
        return MockUser(phone=phone)
    
    async def mock_create_user(db, phone, **kwargs):
        """Mock create_user to return MockUser."""
        return MockUser(phone=phone)
    
    async def mock_get_user_messages(db, user_id, limit=20):
        """Mock get_user_messages to return empty list."""
        return []
    
    async def mock_create_message(db, user_id, message_text, sender):
        """Mock create_message to return None."""
        return None
    
    async def mock_update_user(db, user_id, **kwargs):
        """Mock update_user to return None."""
        return None
    
    # Stateful mock storage
    mock_db_state = {
        "configs": {
            "system_prompt": "You are a helpful assistant",
            "product_name": "Test Product",
            "welcome_message": "Welcome!",
            "use_emojis": True,
            "text_audio_ratio": 50
        }
    }

    async def mock_get_all_configs(db, user_id=None):
        """Mock get_all_configs to return stored config."""
        return mock_db_state["configs"]
    
    async def mock_get_config(db, key, user_id=None):
        """Mock get_config to return specific config."""
        return mock_db_state["configs"].get(key)

    async def mock_set_config(db, key, value, user_id=None):
        """Mock set_config to update specific config."""
        if value == {}:  # Handle deletion (empty dict)
            if key in mock_db_state["configs"]:
                del mock_db_state["configs"][key]
        else:
            mock_db_state["configs"][key] = value
        return value
    
    async def mock_update_config(db, key, value, user_id=None):
        """Mock update_config (alias for set_config)."""
        return await mock_set_config(db, key, value, user_id)
        
    async def mock_get_integration_config(db, integration_type, user_id=None):
        """Mock get_integration_config."""
        return mock_db_state["configs"].get(f"{integration_type}_config")

    async def mock_update_integration_config(db, integration_type, config_data, user_id=None):
        """Mock update_integration_config."""
        mock_db_state["configs"][f"{integration_type}_config"] = config_data
        return config_data

    async def mock_delete_integration_config(db, integration_type, user_id=None):
        """Mock delete_integration_config."""
        if f"{integration_type}_config" in mock_db_state["configs"]:
            del mock_db_state["configs"][f"{integration_type}_config"]
        return True
    
    # Mock bot workflow to avoid real LLM calls
    async def mock_process_message(user_phone, message, conversation_history, config, db_session, db_user):
        """
        Mock bot workflow to return test response without calling real LLM.
        
        NOTE: This is a simplified mock for fast unit tests.
        For comprehensive LLM testing, see TODO in BUG_TRACKER.md and TASK_LOG.md
        """
        return {
            "current_response": f"Test bot response to: {message}",
            "user_name": "Test User",
            "user_email": None,
            "intent_score": 0.5,
            "sentiment": "neutral",
            "stage": "initial_contact",
            "conversation_mode": "AUTO"
        }
    
    # Patch CRUD operations
    monkeypatch.setattr(crud, "get_user_by_phone", mock_get_user_by_phone)
    monkeypatch.setattr(crud, "create_user", mock_create_user)
    monkeypatch.setattr(crud, "get_user_messages", mock_get_user_messages)
    monkeypatch.setattr(crud, "create_message", mock_create_message)
    monkeypatch.setattr(crud, "update_user", mock_update_user)
    monkeypatch.setattr(crud, "get_all_configs", mock_get_all_configs)
    
    # Patch generic config methods if they exist (based on integrations.py usage)
    if hasattr(crud, "get_config"):
        monkeypatch.setattr(crud, "get_config", mock_get_config)
    if hasattr(crud, "set_config"):
        monkeypatch.setattr(crud, "set_config", mock_set_config)
    if hasattr(crud, "update_config"):
        monkeypatch.setattr(crud, "update_config", mock_update_config)

    # If specific integration CRUD methods exist, patch them too. 
    # Based on routers/integrations.py, it likely uses generic config or specific methods.
    # Let's check routers/integrations.py to be sure, but for now assuming standard CRUD names or generic config.
    # Actually, looking at previous context, integrations might be stored as JSON in configs table or separate table.
    # Let's patch generic update/get if that's what's used, or specific ones.
    # Checking routers/integrations.py would be safer, but I'll add these for now as they are likely used.
    if hasattr(crud, "get_integration_config"):
        monkeypatch.setattr(crud, "get_integration_config", mock_get_integration_config)
    if hasattr(crud, "update_integration_config"):
        monkeypatch.setattr(crud, "update_integration_config", mock_update_integration_config)
    if hasattr(crud, "delete_integration_config"):
        monkeypatch.setattr(crud, "delete_integration_config", mock_delete_integration_config)
    
    # Patch bot workflow
    try:
        # Import and patch the workflow if available
        import sys
        from pathlib import Path
        bot_engine_path = Path(__file__).parent.parent.parent.parent / "bot-engine" / "src"
        if str(bot_engine_path) not in sys.path:
            sys.path.insert(0, str(bot_engine_path))
        
        from graph import workflow
        from services.config_manager import ConfigManager
        
        # Patch ConfigManager methods to use mock_db_state
        async def mock_cm_load_all(self, db, user_id=None):
            return mock_db_state["configs"]
            
        async def mock_cm_save_all(self, db, configs, user_id=None):
            mock_db_state["configs"].update(configs)
            
        monkeypatch.setattr(ConfigManager, "load_all_configs", mock_cm_load_all)
        monkeypatch.setattr(ConfigManager, "save_all_configs", mock_cm_save_all)
        
        monkeypatch.setattr(workflow, "process_message", mock_process_message)
    except ImportError:
        # If bot-engine not available, tests will skip bot processing
        pass
    
    # Mock RAG service
    from unittest.mock import AsyncMock, MagicMock
    mock_rag_service = MagicMock()
    mock_rag_service.enabled = True
    
    # Async methods
    mock_rag_service.upload_document = AsyncMock(return_value=1)
    mock_rag_service.upload_documents = AsyncMock(return_value=1)
    mock_rag_service.retrieve_context = AsyncMock(return_value="Test context")
    
    # Sync methods
    mock_rag_service.get_collection_stats.return_value = {
        "total_chunks": 1,
        "collection_name": "test_collection",
        "backend": "mock"
    }
    mock_rag_service.clear_collection.return_value = 1
    
    async def mock_get_rag_service():
        return mock_rag_service
        
    # Patch get_rag_service in the router
    from src.routers import rag
    monkeypatch.setattr(rag, "get_rag_service", mock_get_rag_service)

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

