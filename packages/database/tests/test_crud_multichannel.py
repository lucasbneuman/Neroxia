"""Unit tests for multi-channel CRUD operations."""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from neroxia_database.models import Base, User, Deal, ChannelIntegration
from neroxia_database import crud


# Mark all tests as anyio
pytestmark = pytest.mark.anyio


# Test database setup
@pytest.fixture
async def db_session():
    """Create test database session."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


# ============================================================================
# USER OPERATIONS TESTS
# ============================================================================


async def test_create_user_whatsapp(db_session):
    """Test creating a WhatsApp user."""
    user = await crud.create_user(
        db_session,
        phone="+1234567890",
        name="John Doe",
        channel="whatsapp",
        auth_user_id=None
    )

    assert user.id is not None
    assert user.phone == "+1234567890"
    assert user.name == "John Doe"
    assert user.channel == "whatsapp"
    assert user.auth_user_id == "tenant-1"
    assert user.channel_user_id is None


async def test_create_user_instagram(db_session):
    """Test creating an Instagram user."""
    user = await crud.create_user(
        db_session,
        phone=None,
        name="Jane Smith",
        channel="instagram",
        channel_user_id="123456789",
        channel_username="janesmith",
        channel_profile_pic_url="https://instagram.com/profile.jpg",
        auth_user_id=None
    )

    assert user.id is not None
    assert user.phone is None
    assert user.name == "Jane Smith"
    assert user.channel == "instagram"
    assert user.channel_user_id == "123456789"
    assert user.channel_username == "janesmith"
    assert user.channel_profile_pic_url == "https://instagram.com/profile.jpg"
    assert user.auth_user_id == "tenant-1"


async def test_create_user_messenger(db_session):
    """Test creating a Messenger user."""
    user = await crud.create_user(
        db_session,
        phone=None,
        name="Bob Johnson",
        channel="messenger",
        channel_user_id="987654321",
        auth_user_id=None
    )

    assert user.id is not None
    assert user.phone is None
    assert user.name == "Bob Johnson"
    assert user.channel == "messenger"
    assert user.channel_user_id == "987654321"
    assert user.auth_user_id == "tenant-2"


async def test_get_user_by_identifier_whatsapp(db_session):
    """Test getting WhatsApp user by phone."""
    # Create user
    await crud.create_user(
        db_session,
        phone="+1234567890",
        name="John Doe",
        channel="whatsapp",
        auth_user_id=None
    )

    # Lookup by phone
    user = await crud.get_user_by_identifier(
        db_session,
        identifier="+1234567890",
        channel="whatsapp",
        auth_user_id=None
    )

    assert user is not None
    assert user.phone == "+1234567890"
    assert user.channel == "whatsapp"


async def test_get_user_by_identifier_instagram(db_session):
    """Test getting Instagram user by PSID."""
    # Create user
    await crud.create_user(
        db_session,
        phone=None,
        name="Jane Smith",
        channel="instagram",
        channel_user_id="123456789",
        auth_user_id=None
    )

    # Lookup by PSID
    user = await crud.get_user_by_identifier(
        db_session,
        identifier="123456789",
        channel="instagram",
        auth_user_id=None
    )

    assert user is not None
    assert user.channel_user_id == "123456789"
    assert user.channel == "instagram"


async def test_get_user_by_identifier_multi_tenant(db_session):
    """Test multi-tenant isolation in user lookup."""
    # Create users for different tenants
    await crud.create_user(
        db_session,
        phone=None,
        name="Tenant 1 User",
        channel="instagram",
        channel_user_id="123456789",
        auth_user_id=None
    )

    await crud.create_user(
        db_session,
        phone=None,
        name="Tenant 2 User",
        channel="instagram",
        channel_user_id="123456789",
        auth_user_id=None
    )

    # Lookup for tenant-1
    user1 = await crud.get_user_by_identifier(
        db_session,
        identifier="123456789",
        channel="instagram",
        auth_user_id=None
    )

    assert user1 is not None
    assert user1.name == "Tenant 1 User"
    assert user1.auth_user_id == "tenant-1"

    # Lookup for tenant-2
    user2 = await crud.get_user_by_identifier(
        db_session,
        identifier="123456789",
        channel="instagram",
        auth_user_id=None
    )

    assert user2 is not None
    assert user2.name == "Tenant 2 User"
    assert user2.auth_user_id == "tenant-2"


async def test_get_all_active_users_with_channel_filter(db_session):
    """Test filtering active users by channel."""
    # Create users on different channels
    user1 = await crud.create_user(
        db_session,
        phone="+1111111111",
        name="WhatsApp User",
        channel="whatsapp",
        auth_user_id=None
    )

    user2 = await crud.create_user(
        db_session,
        phone=None,
        name="Instagram User",
        channel="instagram",
        channel_user_id="123456",
        auth_user_id=None
    )

    user3 = await crud.create_user(
        db_session,
        phone=None,
        name="Messenger User",
        channel="messenger",
        channel_user_id="789012",
        auth_user_id=None
    )

    # Give users messages
    user1.total_messages = 5
    user2.total_messages = 3
    user3.total_messages = 2
    await db_session.commit()

    # Get all active users
    all_users = await crud.get_all_active_users(db_session, auth_user_id="00000000-0000-0000-0000-000000000001")
    assert len(all_users) == 3

    # Filter by WhatsApp
    whatsapp_users = await crud.get_all_active_users(
        db_session,
        auth_user_id=None,
        channel="whatsapp"
    )
    assert len(whatsapp_users) == 1
    assert whatsapp_users[0].channel == "whatsapp"

    # Filter by Instagram
    instagram_users = await crud.get_all_active_users(
        db_session,
        auth_user_id=None,
        channel="instagram"
    )
    assert len(instagram_users) == 1
    assert instagram_users[0].channel == "instagram"


# ============================================================================
# CHANNEL INTEGRATION TESTS
# ============================================================================


async def test_create_channel_integration(db_session):
    """Test creating a channel integration."""
    integration = await crud.create_channel_integration(
        db_session,
        auth_user_id=None,
        channel="instagram",
        page_id="page123",
        page_access_token="token123",
        page_name="Test Page",
        instagram_account_id="ig123",
        webhook_verify_token="verify123"
    )

    assert integration.id is not None
    assert integration.auth_user_id == "tenant-1"
    assert integration.channel == "instagram"
    assert integration.page_id == "page123"
    assert integration.page_access_token == "token123"
    assert integration.page_name == "Test Page"
    assert integration.instagram_account_id == "ig123"
    assert integration.webhook_verify_token == "verify123"
    assert integration.is_active is True


async def test_get_channel_integration(db_session):
    """Test getting channel integration by tenant and channel."""
    # Create integration
    await crud.create_channel_integration(
        db_session,
        auth_user_id=None,
        channel="instagram",
        page_id="page123",
        page_access_token="token123"
    )

    # Retrieve it
    integration = await crud.get_channel_integration(
        db_session,
        auth_user_id=None,
        channel="instagram"
    )

    assert integration is not None
    assert integration.auth_user_id == "tenant-1"
    assert integration.channel == "instagram"


async def test_get_channel_integration_by_page(db_session):
    """Test getting integration by page ID (for webhooks)."""
    # Create integration
    await crud.create_channel_integration(
        db_session,
        auth_user_id=None,
        channel="instagram",
        page_id="page123",
        page_access_token="token123"
    )

    # Retrieve by page_id
    integration = await crud.get_channel_integration_by_page(
        db_session,
        page_id="page123",
        channel="instagram"
    )

    assert integration is not None
    assert integration.page_id == "page123"
    assert integration.auth_user_id == "tenant-1"


async def test_update_channel_integration(db_session):
    """Test updating channel integration."""
    # Create integration
    integration = await crud.create_channel_integration(
        db_session,
        auth_user_id=None,
        channel="instagram",
        page_id="page123",
        page_access_token="token123"
    )

    # Update it
    updated = await crud.update_channel_integration(
        db_session,
        integration_id=integration.id,
        page_access_token="new_token",
        page_name="Updated Page"
    )

    assert updated.page_access_token == "new_token"
    assert updated.page_name == "Updated Page"


async def test_deactivate_channel_integration(db_session):
    """Test deactivating channel integration."""
    # Create integration
    integration = await crud.create_channel_integration(
        db_session,
        auth_user_id=None,
        channel="instagram",
        page_id="page123",
        page_access_token="token123"
    )

    assert integration.is_active is True

    # Deactivate it
    deactivated = await crud.deactivate_channel_integration(
        db_session,
        integration_id=integration.id
    )

    assert deactivated.is_active is False

    # Verify it's not returned by get_channel_integration
    result = await crud.get_channel_integration(
        db_session,
        auth_user_id=None,
        channel="instagram"
    )
    assert result is None


async def test_update_channel_integration_not_found(db_session):
    """Test updating non-existent integration raises error."""
    with pytest.raises(ValueError, match="Integration 999 not found"):
        await crud.update_channel_integration(
            db_session,
            integration_id=999,
            page_name="Test"
        )


# ============================================================================
# DEAL OPERATIONS TESTS
# ============================================================================


async def test_create_deal_with_valid_sources(db_session):
    """Test creating deals with valid sources."""
    # Create user
    user = await crud.create_user(
        db_session,
        phone="+1234567890",
        name="Test User",
        channel="whatsapp"
    )

    # Test all valid sources
    sources = ["whatsapp", "instagram", "messenger", "test"]
    for source in sources:
        deal = await crud.create_deal(
            db_session,
            user_id=user.id,
            title=f"Deal from {source}",
            source=source
        )
        assert deal.source == source


async def test_create_deal_with_invalid_source(db_session):
    """Test creating deal with invalid source raises error."""
    # Create user
    user = await crud.create_user(
        db_session,
        phone="+1234567890",
        name="Test User",
        channel="whatsapp"
    )

    # Try invalid source
    with pytest.raises(ValueError, match="Invalid source"):
        await crud.create_deal(
            db_session,
            user_id=user.id,
            title="Test Deal",
            source="invalid_channel"
        )


async def test_create_deal_instagram_source(db_session):
    """Test creating deal from Instagram."""
    # Create Instagram user
    user = await crud.create_user(
        db_session,
        phone=None,
        name="Instagram User",
        channel="instagram",
        channel_user_id="123456"
    )

    # Create deal
    deal = await crud.create_deal(
        db_session,
        user_id=user.id,
        title="Instagram Lead",
        source="instagram"
    )

    assert deal.source == "instagram"
    assert deal.user_id == user.id


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


async def test_multi_channel_end_to_end(db_session):
    """Test complete multi-channel workflow."""
    # Setup: Create channel integration
    integration = await crud.create_channel_integration(
        db_session,
        auth_user_id=None,
        channel="instagram",
        page_id="page123",
        page_access_token="token123"
    )

    # User sends Instagram message (simulated)
    user = await crud.create_user(
        db_session,
        phone=None,
        name="Instagram User",
        channel="instagram",
        channel_user_id="psid123",
        channel_username="instauser",
        auth_user_id=None
    )

    # Create message
    message = await crud.create_message(
        db_session,
        user_id=user.id,
        message_text="Hello from Instagram",
        sender="user",
        metadata={"channel": "instagram", "psid": "psid123"}
    )

    # Create deal
    deal = await crud.create_deal(
        db_session,
        user_id=user.id,
        title="Instagram Lead",
        source="instagram"
    )

    # Assertions
    assert user.channel == "instagram"
    assert user.total_messages == 1
    assert message.message_text == "Hello from Instagram"
    assert deal.source == "instagram"

    # Lookup user by identifier
    found_user = await crud.get_user_by_identifier(
        db_session,
        identifier="psid123",
        channel="instagram",
        auth_user_id=None
    )

    assert found_user.id == user.id

    # Lookup integration
    found_integration = await crud.get_channel_integration_by_page(
        db_session,
        page_id="page123",
        channel="instagram"
    )

    assert found_integration.id == integration.id
