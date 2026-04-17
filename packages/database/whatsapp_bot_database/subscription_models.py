"""Subscription and billing models for SaaS platform."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .models import Base


class SubscriptionPlan(Base):
    """Subscription plans available for users."""

    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # free_trial, professional, enterprise
    display_name = Column(String(100), nullable=False)  # "Professional Plan"
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)  # Monthly price
    currency = Column(String(3), default="USD")
    billing_period = Column(String(20), default="monthly")  # monthly, yearly
    
    # Features and limits (JSON)
    features = Column(JSON, nullable=False)
    # Example:
    # {
    #   "messages_per_month": 5000,
    #   "bots_limit": 3,
    #   "rag_storage_mb": 500,
    #   "api_calls_per_day": 10000,
    #   "team_members": 5,
    #   "integrations": ["hubspot", "twilio"],
    #   "support": "email",
    #   "features": ["rag", "tts", "analytics"]
    # }
    
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0)  # For display ordering
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="plan")

    def __repr__(self) -> str:
        return f"<SubscriptionPlan(id={self.id}, name={self.name}, price={self.price})>"


class UserSubscription(Base):
    """Active subscription for a user."""

    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=False), nullable=False, unique=True, index=True)  # UUID from auth.users
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False, index=True)
    
    # Subscription status
    status = Column(
        String(20), 
        default="trial", 
        nullable=False,
        index=True
    )  # trial, active, past_due, canceled, expired
    
    # Period tracking
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    
    # Trial tracking
    trial_ends_at = Column(DateTime, nullable=True)
    trial_days = Column(Integer, default=14)
    
    # Cancellation
    canceled_at = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    
    # Stripe integration
    stripe_customer_id = Column(String(100), nullable=True, index=True)
    stripe_subscription_id = Column(String(100), nullable=True, index=True)
    stripe_price_id = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    usage_records = relationship("UsageTracking", back_populates="subscription", cascade="all, delete-orphan")
    billing_history = relationship("BillingHistory", back_populates="subscription", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<UserSubscription(id={self.id}, user_id={self.user_id}, status={self.status})>"


class UsageTracking(Base):
    """Track usage metrics for billing and limits."""

    __tablename__ = "usage_tracking"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("user_subscriptions.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=False), nullable=False, index=True)  # Denormalized for faster queries
    
    # Billing period
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)
    
    # Usage metrics
    messages_sent = Column(Integer, default=0, nullable=False)
    bots_created = Column(Integer, default=0, nullable=False)
    rag_documents = Column(Integer, default=0, nullable=False)
    rag_storage_mb = Column(Float, default=0.0, nullable=False)
    api_calls = Column(Integer, default=0, nullable=False)
    
    # Metadata
    last_reset_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    subscription = relationship("UserSubscription", back_populates="usage_records")

    def __repr__(self) -> str:
        return f"<UsageTracking(id={self.id}, user_id={self.user_id}, messages={self.messages_sent})>"


class BillingHistory(Base):
    """Billing and payment history."""

    __tablename__ = "billing_history"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("user_subscriptions.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=False), nullable=False, index=True)  # Denormalized
    
    # Invoice details
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(String(20), nullable=False)  # pending, paid, failed, refunded
    description = Column(Text, nullable=True)
    
    # Stripe integration
    stripe_invoice_id = Column(String(100), nullable=True, index=True)
    stripe_charge_id = Column(String(100), nullable=True)
    invoice_url = Column(String(500), nullable=True)
    invoice_pdf = Column(String(500), nullable=True)
    
    # Timestamps
    billing_date = Column(DateTime, nullable=False)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    subscription = relationship("UserSubscription", back_populates="billing_history")

    def __repr__(self) -> str:
        return f"<BillingHistory(id={self.id}, user_id={self.user_id}, amount={self.amount}, status={self.status})>"


class UserProfile(Base):
    """Extended user profile (complements auth.users from Supabase)."""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    auth_user_id = Column(UUID(as_uuid=False), unique=True, nullable=False, index=True)  # FK to auth.users
    
    # Profile information
    company_name = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="es")  # es, en, pt
    
    # Avatar
    avatar_url = Column(String(500), nullable=True)
    
    # Role and permissions
    role = Column(String(20), default="owner")  # owner, admin, member
    
    # Onboarding
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    onboarding_step = Column(Integer, default=0)  # Current step in onboarding
    
    # Preferences (JSON)
    preferences = Column(JSON, nullable=True)
    # Example:
    # {
    #   "notifications": {"email": true, "push": false},
    #   "theme": "dark",
    #   "date_format": "DD/MM/YYYY"
    # }
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id}, auth_user_id={self.auth_user_id}, company={self.company_name})>"
