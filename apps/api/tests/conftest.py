"""
Pytest configuration and fixtures for API testing.

This module provides shared fixtures for all test files including:
- Test client setup
- Authentication tokens
- Database cleanup
- Test data factories
"""

import os
import sys
from pathlib import Path
from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient

# Force test-safe configuration before importing the app and DB modules.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SUPABASE_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "test-anon-key")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-service-key")

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

database_dir = project_root / "packages" / "database"
if str(database_dir) not in sys.path:
    sys.path.insert(0, str(database_dir))

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
    from datetime import datetime, timezone
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, MagicMock
    from whatsapp_bot_database import crud
    from fastapi import Header, HTTPException, Request, status
    from src.routers import rag as rag_router
    from src.routers import followups as followups_router
    
    # Create a mock user object with proper attributes
    class MockUser:
        def __init__(self, phone="+1234567890"):
            self.id = "test-user-id-123"
            self.email = "test@example.com"
            self.username = "test@example.com"
            self.user_metadata = {}
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
    
    mock_current_user = MockUser()

    async def mock_get_current_user(
        request: Request,
        authorization: str = Header(None),
    ):
        """
        Mock user for testing - returns object with attributes.
        Allows unauthenticated access only for the bot test-processing endpoint.
        """
        anonymous_allowed_paths = {
            "/bot/process",
            "/integrations/facebook/connect",
            "/integrations/facebook/disconnect",
            "/integrations/list",
        }

        if not authorization:
            if request.url.path == "/integrations/facebook/connect":
                return {"id": "user_123"}
            if request.url.path in anonymous_allowed_paths:
                return mock_current_user
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header",
            )

        if authorization != "Bearer mock_test_token_for_api_tests":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        return mock_current_user
    
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

    mock_db_state = {
        "users": {},
        "messages": {},
        "configs": {
            "system_prompt": "You are a helpful assistant",
            "product_name": "Test Product",
            "welcome_message": "Welcome!",
            "use_emojis": True,
            "text_audio_ratio": 50
        },
        "deals": {},
        "notes": {},
        "tags": {},
        "user_tags": {},
        "followups": {},
        "integrations": [],
        "counters": {
            "user": 1,
            "message": 1,
            "deal": 1,
            "note": 1,
            "tag": 1,
            "followup": 1,
        },
    }

    def _now():
        return datetime.now(timezone.utc)

    def _ensure_user(phone: str, **overrides):
        if phone not in mock_db_state["users"]:
            user_id = mock_db_state["counters"]["user"]
            mock_db_state["counters"]["user"] += 1
            mock_db_state["users"][phone] = SimpleNamespace(
                id=user_id,
                auth_user_id=mock_current_user.id,
                phone=phone,
                name=overrides.get("name", "Test User"),
                email=overrides.get("email"),
                stage=overrides.get("stage", "initial_contact"),
                sentiment=overrides.get("sentiment", "neutral"),
                intent_score=overrides.get("intent_score", 0.5),
                conversation_mode=overrides.get("conversation_mode", "AUTO"),
                conversation_summary=overrides.get("conversation_summary", "Test conversation summary"),
                last_message_at=overrides.get("last_message_at"),
                created_at=_now(),
                updated_at=_now(),
                total_messages=0,
                whatsapp_profile_name=None,
                twilio_profile_name=None,
            )
            mock_db_state["messages"][user_id] = []
        return mock_db_state["users"][phone]

    def _deal_to_dict(deal):
        return {
            "id": deal.id,
            "user_id": deal.user_id,
            "title": deal.title,
            "value": deal.value,
            "currency": deal.currency,
            "stage": deal.stage,
            "probability": deal.probability,
            "source": deal.source,
            "manually_qualified": deal.manually_qualified,
            "expected_close_date": deal.expected_close_date.isoformat() if deal.expected_close_date else None,
            "won_date": deal.won_date.isoformat() if deal.won_date else None,
            "lost_date": deal.lost_date.isoformat() if deal.lost_date else None,
            "lost_reason": deal.lost_reason,
            "created_at": deal.created_at.isoformat(),
            "updated_at": deal.updated_at.isoformat(),
            "user": {
                "id": deal.user.id,
                "phone": deal.user.phone,
                "name": deal.user.name,
                "email": deal.user.email,
            } if getattr(deal, "user", None) else None,
        }

    async def mock_get_user_by_phone(db, phone, auth_user_id=None):
        return mock_db_state["users"].get(phone)

    async def mock_create_user(db, phone, auth_user_id=None, **kwargs):
        return _ensure_user(phone, **kwargs)

    async def mock_get_or_create_user(db, identifier, channel="whatsapp", auth_user_id=None, defaults=None):
        user = mock_db_state["users"].get(identifier)
        if user:
            return user, False
        defaults = defaults or {}
        return _ensure_user(identifier, **defaults), True

    async def mock_get_user_messages(db, user_id, limit=20):
        return list(mock_db_state["messages"].get(user_id, []))[-limit:]

    async def mock_create_message(db, user_id, message_text, sender, metadata=None):
        message_id = mock_db_state["counters"]["message"]
        mock_db_state["counters"]["message"] += 1
        message = SimpleNamespace(
            id=message_id,
            user_id=user_id,
            message_text=message_text,
            sender=sender,
            timestamp=_now(),
            message_metadata=metadata or {},
        )
        mock_db_state["messages"].setdefault(user_id, []).append(message)
        for user in mock_db_state["users"].values():
            if user.id == user_id:
                user.last_message_at = message.timestamp
                user.total_messages = len(mock_db_state["messages"][user_id])
                user.updated_at = _now()
                break
        return message

    async def mock_update_user(db, user_id, **kwargs):
        for user in mock_db_state["users"].values():
            if user.id == user_id:
                for key, value in kwargs.items():
                    if value is not None:
                        setattr(user, key, value)
                user.updated_at = _now()
                return user
        return None

    async def mock_get_all_active_users(db, limit=100, auth_user_id=None):
        return list(mock_db_state["users"].values())[:limit]

    async def mock_get_recent_messages(db, user_id, count=1):
        return list(mock_db_state["messages"].get(user_id, []))[-count:]

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

    async def mock_get_crm_metrics(db):
        deals = list(mock_db_state["deals"].values())
        active_deals = [d for d in deals if d.stage not in {"won", "lost"}]
        won_deals = [d for d in deals if d.stage == "won"]
        total_revenue = sum(d.value for d in won_deals)
        conversion_rate = round((len(won_deals) / len(deals) * 100), 2) if deals else 0
        return {
            "total_active_deals": len(active_deals),
            "total_won_deals": len(won_deals),
            "total_revenue": total_revenue,
            "conversion_rate": conversion_rate,
        }

    async def mock_create_deal(db, user_id, title, value=0.0, stage="new_lead", source="whatsapp", probability=10, expected_close_date=None):
        if stage not in {"new_lead", "qualified", "in_conversation", "proposal_sent", "won", "lost"}:
            raise HTTPException(status_code=400, detail="Invalid stage")
        deal_id = mock_db_state["counters"]["deal"]
        mock_db_state["counters"]["deal"] += 1
        user = next((u for u in mock_db_state["users"].values() if u.id == user_id), None) or _ensure_user("+10000000000")
        deal = SimpleNamespace(
            id=deal_id,
            user_id=user_id,
            title=title,
            value=value,
            currency="USD",
            stage=stage,
            probability=probability,
            source=source,
            manually_qualified=False,
            expected_close_date=expected_close_date,
            won_date=None,
            lost_date=None,
            lost_reason=None,
            created_at=_now(),
            updated_at=_now(),
            user=user,
        )
        mock_db_state["deals"][deal_id] = deal
        return _deal_to_dict(deal)

    async def mock_get_all_deals(db, stage=None, limit=100, offset=0):
        deals = [_deal_to_dict(d) for d in mock_db_state["deals"].values()]
        if stage:
            deals = [d for d in deals if d["stage"] == stage]
        return deals[offset:offset + limit]

    async def mock_get_deal_by_id(db, deal_id):
        deal = mock_db_state["deals"].get(deal_id)
        return _deal_to_dict(deal) if deal else None

    async def mock_update_deal(db, deal_id, **kwargs):
        deal = mock_db_state["deals"].get(deal_id)
        if not deal:
            return None
        if "stage" in kwargs and kwargs["stage"] not in {"new_lead", "qualified", "in_conversation", "proposal_sent", "won", "lost"}:
            raise HTTPException(status_code=400, detail="Invalid stage")
        for key, value in kwargs.items():
            setattr(deal, key, value)
        if "stage" in kwargs:
            deal.manually_qualified = True
        deal.updated_at = _now()
        return _deal_to_dict(deal)

    async def mock_mark_deal_won(db, deal_id):
        deal = mock_db_state["deals"].get(deal_id)
        if not deal:
            return None
        deal.stage = "won"
        deal.probability = 100
        deal.won_date = _now()
        deal.updated_at = _now()
        return _deal_to_dict(deal)

    async def mock_mark_deal_lost(db, deal_id, reason):
        deal = mock_db_state["deals"].get(deal_id)
        if not deal:
            return None
        deal.stage = "lost"
        deal.probability = 0
        deal.lost_reason = reason
        deal.lost_date = _now()
        deal.updated_at = _now()
        return _deal_to_dict(deal)

    async def mock_delete_deal(db, deal_id):
        return mock_db_state["deals"].pop(deal_id, None) is not None

    async def mock_get_user_deals(db, user_id):
        return [d for d in mock_db_state["deals"].values() if d.user_id == user_id]

    async def mock_get_user_active_deal(db, user_id):
        return next((d for d in mock_db_state["deals"].values() if d.user_id == user_id and d.stage not in {"won", "lost"}), None)

    async def mock_create_note(db, user_id, content, created_by, deal_id=None, note_type="note"):
        note_id = mock_db_state["counters"]["note"]
        mock_db_state["counters"]["note"] += 1
        note = {
            "id": note_id,
            "user_id": user_id,
            "deal_id": deal_id,
            "content": content,
            "note_type": note_type,
            "created_by": created_by,
            "created_at": _now().isoformat(),
        }
        mock_db_state["notes"][note_id] = note
        return note

    async def mock_get_user_notes(db, user_id):
        return [n for n in mock_db_state["notes"].values() if n["user_id"] == user_id]

    async def mock_delete_note(db, note_id):
        return mock_db_state["notes"].pop(note_id, None) is not None

    async def mock_create_tag(db, name, color="#6B7280"):
        tag_id = mock_db_state["counters"]["tag"]
        mock_db_state["counters"]["tag"] += 1
        tag = {"id": tag_id, "name": name, "color": color, "created_at": _now().isoformat()}
        mock_db_state["tags"][tag_id] = tag
        return tag

    async def mock_get_all_tags(db):
        return list(mock_db_state["tags"].values())

    async def mock_get_user_tags(db, user_id):
        tag_ids = mock_db_state["user_tags"].get(user_id, set())
        return [mock_db_state["tags"][tag_id] for tag_id in tag_ids if tag_id in mock_db_state["tags"]]

    async def mock_add_tag_to_user(db, user_id, tag_id):
        if tag_id not in mock_db_state["tags"]:
            raise HTTPException(status_code=404, detail="Tag not found")
        mock_db_state["user_tags"].setdefault(user_id, set()).add(tag_id)
        return {"status": "success"}

    async def mock_remove_tag_from_user(db, user_id, tag_id):
        tags = mock_db_state["user_tags"].setdefault(user_id, set())
        if tag_id not in tags:
            return False
        tags.remove(tag_id)
        return True

    async def mock_create_follow_up(db, user_id, scheduled_time, message, job_id=None):
        followup_id = mock_db_state["counters"]["followup"]
        mock_db_state["counters"]["followup"] += 1
        followup = SimpleNamespace(
            id=followup_id,
            user_id=user_id,
            scheduled_time=scheduled_time,
            message=message,
            status="pending",
            job_id=job_id,
        )
        mock_db_state["followups"][job_id or str(followup_id)] = followup
        return followup

    async def mock_get_tenant_follow_ups(db, auth_user_id):
        return list(mock_db_state["followups"].values())

    async def mock_create_channel_integration(db, auth_user_id, channel, page_id, page_access_token, page_name, instagram_account_id=None):
        integration = SimpleNamespace(
            auth_user_id=auth_user_id,
            channel=channel,
            page_id=page_id,
            page_access_token=page_access_token,
            page_name=page_name,
            instagram_account_id=instagram_account_id,
            is_active=True,
        )
        mock_db_state["integrations"].append(integration)
        return integration

    async def mock_get_channel_integrations_by_user(db, user_id):
        return [i for i in mock_db_state["integrations"] if i.auth_user_id == user_id]
    
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
            "conversation_mode": "AUTO",
            "channel": "whatsapp",
            "user_identifier": user_phone,
        }
    
    # Patch CRUD operations
    monkeypatch.setattr(crud, "get_user_by_phone", mock_get_user_by_phone)
    monkeypatch.setattr(crud, "create_user", mock_create_user)
    monkeypatch.setattr(crud, "get_or_create_user", mock_get_or_create_user)
    monkeypatch.setattr(crud, "get_user_messages", mock_get_user_messages)
    monkeypatch.setattr(crud, "create_message", mock_create_message)
    monkeypatch.setattr(crud, "update_user", mock_update_user)
    monkeypatch.setattr(crud, "get_all_configs", mock_get_all_configs)
    monkeypatch.setattr(crud, "get_all_active_users", mock_get_all_active_users)
    monkeypatch.setattr(crud, "get_recent_messages", mock_get_recent_messages)
    monkeypatch.setattr(crud, "get_crm_metrics", mock_get_crm_metrics)
    monkeypatch.setattr(crud, "create_deal", mock_create_deal)
    monkeypatch.setattr(crud, "get_all_deals", mock_get_all_deals)
    monkeypatch.setattr(crud, "get_deal_by_id", mock_get_deal_by_id)
    monkeypatch.setattr(crud, "update_deal", mock_update_deal)
    monkeypatch.setattr(crud, "mark_deal_won", mock_mark_deal_won)
    monkeypatch.setattr(crud, "mark_deal_lost", mock_mark_deal_lost)
    monkeypatch.setattr(crud, "delete_deal", mock_delete_deal)
    monkeypatch.setattr(crud, "get_user_deals", mock_get_user_deals)
    monkeypatch.setattr(crud, "get_user_active_deal", mock_get_user_active_deal)
    monkeypatch.setattr(crud, "create_note", mock_create_note)
    monkeypatch.setattr(crud, "get_user_notes", mock_get_user_notes)
    monkeypatch.setattr(crud, "delete_note", mock_delete_note)
    monkeypatch.setattr(crud, "create_tag", mock_create_tag)
    monkeypatch.setattr(crud, "get_all_tags", mock_get_all_tags)
    monkeypatch.setattr(crud, "get_user_tags", mock_get_user_tags)
    monkeypatch.setattr(crud, "add_tag_to_user", mock_add_tag_to_user)
    monkeypatch.setattr(crud, "remove_tag_from_user", mock_remove_tag_from_user)
    monkeypatch.setattr(crud, "create_follow_up", mock_create_follow_up)
    monkeypatch.setattr(crud, "get_tenant_follow_ups", mock_get_tenant_follow_ups)
    monkeypatch.setattr(crud, "create_channel_integration", mock_create_channel_integration)
    monkeypatch.setattr(crud, "get_channel_integrations_by_user", mock_get_channel_integrations_by_user)
    
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
    
    # Patch get_rag_service in the router
    monkeypatch.setattr(rag_router, "get_rag_service", lambda: mock_rag_service)

    class MockSchedulerService:
        def __init__(self):
            self.jobs = {}

        async def add_follow_up_job(self, job_id, phone, message, scheduled_time, send_function):
            self.jobs[job_id] = {
                "id": job_id,
                "phone": phone,
                "message": message,
                "next_run_time": scheduled_time,
                "trigger": "date",
            }

        def cancel_follow_up_job(self, job_id):
            return self.jobs.pop(job_id, None) is not None or job_id in mock_db_state["followups"]

        def get_job_info(self, job_id):
            return self.jobs.get(job_id)

    scheduler_service = MockSchedulerService()
    monkeypatch.setattr(followups_router, "SCHEDULER_AVAILABLE", True)
    monkeypatch.setattr(followups_router, "get_scheduler_service", lambda: scheduler_service)

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

