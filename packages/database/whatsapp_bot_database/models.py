"""SQLAlchemy models for sales bot database."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User/Customer model representing contacts from WhatsApp, Instagram, and Messenger."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)  # Nullable for Instagram/Messenger users
    name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)

    # Link to authenticated user (Supabase auth.users)
    auth_user_id = Column(UUID(as_uuid=False), nullable=True, index=True)  # UUID from auth.users

    # Multi-channel support
    channel = Column(String(20), default="whatsapp", nullable=False, index=True)  # whatsapp, instagram, messenger
    channel_user_id = Column(String(100), nullable=True, index=True)  # PSID for Instagram/Messenger
    channel_username = Column(String(100), nullable=True)  # @username for Instagram
    channel_profile_pic_url = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Conversation tracking
    intent_score = Column(Float, default=0.0)  # 0-1 scale
    sentiment = Column(String(20), default="neutral")  # positive/neutral/negative
    stage = Column(String(50), default="welcome")  # welcome/qualifying/nurturing/closing/sold/follow_up
    conversation_mode = Column(String(20), default="AUTO")  # AUTO/MANUAL/NEEDS_ATTENTION
    conversation_summary = Column(Text, nullable=True)  # AI-generated summary of conversation

    # HubSpot Integration
    hubspot_contact_id = Column(String(50), nullable=True, index=True)  # HubSpot contact ID
    hubspot_lifecyclestage = Column(String(50), nullable=True)  # lead, marketingqualifiedlead, salesqualifiedlead, opportunity, customer, evangelist, other
    hubspot_synced_at = Column(DateTime, nullable=True)  # Last sync timestamp

    # Twilio Integration - Data collected automatically from webhooks
    whatsapp_profile_name = Column(String(100), nullable=True)  # WhatsApp profile name from Twilio
    country_code = Column(String(5), nullable=True)  # Country code extracted from phone
    phone_formatted = Column(String(20), nullable=True)  # Phone formatted by Twilio
    first_contact_timestamp = Column(DateTime, nullable=True)  # First message timestamp
    media_count = Column(Integer, default=0)  # Count of media files sent
    location_shared = Column(Boolean, default=False)  # Whether user shared location
    last_twilio_message_sid = Column(String(50), nullable=True)  # Last Twilio message SID

    # Activity tracking
    total_messages = Column(Integer, default=0)
    last_message_at = Column(DateTime, nullable=True)

    # Relationships
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    follow_ups = relationship("FollowUp", back_populates="user", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="user_tags", back_populates="users")

    __table_args__ = (
        Index('idx_users_channel_user_id', 'channel', 'channel_user_id',
              unique=True,
              postgresql_where=text('channel_user_id IS NOT NULL')),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, channel={self.channel}, phone={self.phone}, name={self.name})>"


class Message(Base):
    """Message model for storing conversation history across all channels."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message_text = Column(Text, nullable=False)
    sender = Column(String(10), nullable=False)  # 'user' or 'bot'
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    message_metadata = Column(JSON, nullable=True)  # Store intent, sentiment at that moment

    # Multi-channel support
    channel = Column(String(20), default="whatsapp", nullable=False, index=True)  # whatsapp, instagram, messenger
    channel_message_id = Column(String(100), nullable=True)  # Meta message ID for Instagram/Messenger

    # Relationships
    user = relationship("User", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, user_id={self.user_id}, channel={self.channel}, sender={self.sender})>"


class FollowUp(Base):
    """Follow-up scheduling model."""

    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    scheduled_time = Column(DateTime, nullable=False, index=True)
    message = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending/sent/cancelled
    follow_up_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    job_id = Column(String(100), nullable=True)  # APScheduler job ID

    # Relationships
    user = relationship("User", back_populates="follow_ups")

    def __repr__(self) -> str:
        return f"<FollowUp(id={self.id}, user_id={self.user_id}, status={self.status})>"


class Config(Base):
    """Configuration storage model - Multi-tenant support."""

    __tablename__ = "configs"
    
    # Composite unique constraint (user_id, key) defined in __table_args__
    __table_args__ = (
        UniqueConstraint('user_id', 'key', name='configs_user_key_unique'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=False), nullable=False, index=True)  # UUID from auth.users
    key = Column(String(100), nullable=False, index=True)
    value = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Config(user_id={self.user_id}, key={self.key})>"


class Deal(Base):
    """Deal/Opportunity model for CRM pipeline."""

    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    value = Column(Float, default=0.0)  # Monetary value
    currency = Column(String(3), default="USD")
    stage = Column(String(50), default="new_lead", index=True)  # Pipeline stage
    probability = Column(Integer, default=10)  # 0-100%
    source = Column(String(50), default="whatsapp")  # Lead source
    expected_close_date = Column(Date, nullable=True)
    won_date = Column(Date, nullable=True)
    lost_date = Column(Date, nullable=True)
    lost_reason = Column(Text, nullable=True)
    manually_qualified = Column(Boolean, default=False, nullable=False)  # Prevents bot auto-updates
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="deals")
    notes = relationship("Note", back_populates="deal", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Deal(id={self.id}, user_id={self.user_id}, title={self.title}, stage={self.stage})>"


class Note(Base):
    """Note/Activity model for tracking interactions."""

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True, index=True)
    content = Column(Text, nullable=False)
    note_type = Column(String(50), default="note")  # note, call, email, meeting, task
    created_by = Column(UUID(as_uuid=False), nullable=False)  # UUID from auth.users
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="notes")
    deal = relationship("Deal", back_populates="notes")

    def __repr__(self) -> str:
        return f"<Note(id={self.id}, user_id={self.user_id}, type={self.note_type})>"


class Tag(Base):
    """Tag model for customer segmentation."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    color = Column(String(7), default="#6B7280")  # Hex color
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    users = relationship("User", secondary="user_tags", back_populates="tags")

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name={self.name})>"


class UserTag(Base):
    """Many-to-many relationship between Users and Tags."""

    __tablename__ = "user_tags"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<UserTag(user_id={self.user_id}, tag_id={self.tag_id})>"


class ChannelIntegration(Base):
    """
    Stores per-tenant channel integration credentials for Instagram and Messenger.
    Each SaaS tenant can connect their own Facebook Pages.
    """
    __tablename__ = "channel_integrations"

    id = Column(Integer, primary_key=True, index=True)
    auth_user_id = Column(UUID(as_uuid=False), nullable=False, index=True)  # UUID from auth.users
    channel = Column(String(20), nullable=False, index=True)  # 'instagram' or 'messenger'
    page_id = Column(String(50), nullable=True)
    page_access_token = Column(Text, nullable=False)  # Long-lived Page Access Token
    page_name = Column(String(200), nullable=True)
    instagram_account_id = Column(String(50), nullable=True)  # For Instagram only
    is_active = Column(Boolean, default=True, index=True)
    webhook_verify_token = Column(String(100), nullable=True)  # Custom token for webhook verification
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint('auth_user_id', 'channel', 'page_id', name='uq_user_channel_page'),
    )

    def __repr__(self) -> str:
        return f"<ChannelIntegration(id={self.id}, auth_user_id={self.auth_user_id}, channel={self.channel}, page_id={self.page_id})>"
