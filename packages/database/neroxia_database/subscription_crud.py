"""CRUD operations for subscription and user profile management."""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .subscription_models import (
    BillingHistory,
    SubscriptionPlan,
    UserProfile,
    UserSubscription,
    UsageTracking,
)


# ============================================================================
# Subscription Plan Operations
# ============================================================================

async def get_all_subscription_plans(
    db: AsyncSession, 
    active_only: bool = True
) -> List[SubscriptionPlan]:
    """Get all subscription plans."""
    query = select(SubscriptionPlan)
    if active_only:
        query = query.where(SubscriptionPlan.is_active == True)
    query = query.order_by(SubscriptionPlan.sort_order)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_subscription_plan_by_name(
    db: AsyncSession, 
    name: str
) -> Optional[SubscriptionPlan]:
    """Get subscription plan by name."""
    query = select(SubscriptionPlan).where(SubscriptionPlan.name == name)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_subscription_plan_by_id(
    db: AsyncSession, 
    plan_id: int
) -> Optional[SubscriptionPlan]:
    """Get subscription plan by ID."""
    query = select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_subscription_plan(
    db: AsyncSession,
    name: str,
    display_name: str,
    price: float,
    features: dict,
    description: Optional[str] = None,
    currency: str = "USD",
    billing_period: str = "monthly",
    sort_order: int = 0,
) -> SubscriptionPlan:
    """Create a new subscription plan."""
    plan = SubscriptionPlan(
        name=name,
        display_name=display_name,
        description=description,
        price=price,
        currency=currency,
        billing_period=billing_period,
        features=features,
        sort_order=sort_order,
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


# ============================================================================
# User Subscription Operations
# ============================================================================

async def get_user_subscription(
    db: AsyncSession, 
    user_id: str
) -> Optional[UserSubscription]:
    """Get user's current subscription."""
    query = (
        select(UserSubscription)
        .where(UserSubscription.user_id == user_id)
        .options(selectinload(UserSubscription.plan))
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_user_subscription(
    db: AsyncSession,
    user_id: str,
    plan_id: int,
    status: str = "trial",
    trial_days: int = 14,
    stripe_customer_id: Optional[str] = None,
    stripe_subscription_id: Optional[str] = None,
) -> UserSubscription:
    """Create a new user subscription (typically trial on signup)."""
    now = datetime.utcnow()
    trial_end = now + timedelta(days=trial_days)
    
    subscription = UserSubscription(
        user_id=user_id,
        plan_id=plan_id,
        status=status,
        current_period_start=now,
        current_period_end=trial_end if status == "trial" else now + timedelta(days=30),
        trial_ends_at=trial_end if status == "trial" else None,
        trial_days=trial_days,
        stripe_customer_id=stripe_customer_id,
        stripe_subscription_id=stripe_subscription_id,
    )
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    
    # Create initial usage tracking record
    await create_usage_tracking(db, subscription.id, user_id, now, subscription.current_period_end)
    
    return subscription


async def update_user_subscription(
    db: AsyncSession,
    user_id: str,
    **kwargs
) -> Optional[UserSubscription]:
    """Update user subscription."""
    query = select(UserSubscription).where(UserSubscription.user_id == user_id)
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        return None
    
    for key, value in kwargs.items():
        if hasattr(subscription, key):
            setattr(subscription, key, value)
    
    subscription.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(subscription)
    return subscription


async def cancel_user_subscription(
    db: AsyncSession,
    user_id: str,
    cancel_at_period_end: bool = True
) -> Optional[UserSubscription]:
    """Cancel user subscription."""
    now = datetime.utcnow()
    
    update_data = {
        "canceled_at": now,
        "cancel_at_period_end": cancel_at_period_end,
    }
    
    if not cancel_at_period_end:
        update_data["status"] = "canceled"
    
    return await update_user_subscription(db, user_id, **update_data)


# ============================================================================
# Usage Tracking Operations
# ============================================================================

async def get_current_usage(
    db: AsyncSession, 
    user_id: str
) -> Optional[UsageTracking]:
    """Get current billing period usage for a user."""
    now = datetime.utcnow()
    query = (
        select(UsageTracking)
        .where(
            and_(
                UsageTracking.user_id == user_id,
                UsageTracking.period_start <= now,
                UsageTracking.period_end >= now,
            )
        )
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_usage_tracking(
    db: AsyncSession,
    subscription_id: int,
    user_id: str,
    period_start: datetime,
    period_end: datetime,
) -> UsageTracking:
    """Create a new usage tracking record."""
    usage = UsageTracking(
        subscription_id=subscription_id,
        user_id=user_id,
        period_start=period_start,
        period_end=period_end,
    )
    db.add(usage)
    await db.commit()
    await db.refresh(usage)
    return usage


async def increment_usage(
    db: AsyncSession,
    user_id: str,
    metric: str,
    amount: int | float = 1,
) -> Optional[UsageTracking]:
    """Increment a usage metric for the current period."""
    usage = await get_current_usage(db, user_id)
    
    if not usage:
        return None
    
    if hasattr(usage, metric):
        current_value = getattr(usage, metric)
        setattr(usage, metric, current_value + amount)
        usage.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(usage)
    
    return usage


async def reset_usage_for_new_period(
    db: AsyncSession,
    user_id: str,
    subscription_id: int,
    period_start: datetime,
    period_end: datetime,
) -> UsageTracking:
    """Reset usage tracking for a new billing period."""
    # Mark old usage as reset
    old_usage = await get_current_usage(db, user_id)
    if old_usage:
        old_usage.last_reset_at = datetime.utcnow()
        await db.commit()
    
    # Create new usage record
    return await create_usage_tracking(db, subscription_id, user_id, period_start, period_end)


# ============================================================================
# User Profile Operations
# ============================================================================

async def get_user_profile(
    db: AsyncSession, 
    auth_user_id: str
) -> Optional[UserProfile]:
    """Get user profile by auth user ID."""
    query = select(UserProfile).where(UserProfile.auth_user_id == auth_user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_user_profile(
    db: AsyncSession,
    auth_user_id: str,
    company_name: Optional[str] = None,
    phone: Optional[str] = None,
    timezone: str = "UTC",
    language: str = "es",
    role: str = "owner",
) -> UserProfile:
    """Create a new user profile."""
    profile = UserProfile(
        auth_user_id=auth_user_id,
        company_name=company_name,
        phone=phone,
        timezone=timezone,
        language=language,
        role=role,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def update_user_profile(
    db: AsyncSession,
    auth_user_id: str,
    **kwargs
) -> Optional[UserProfile]:
    """Update user profile."""
    query = select(UserProfile).where(UserProfile.auth_user_id == auth_user_id)
    result = await db.execute(query)
    profile = result.scalar_one_or_none()
    
    if not profile:
        return None
    
    for key, value in kwargs.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
    
    profile.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(profile)
    return profile


async def delete_user_profile(
    db: AsyncSession,
    auth_user_id: str
) -> bool:
    """Delete user profile."""
    query = select(UserProfile).where(UserProfile.auth_user_id == auth_user_id)
    result = await db.execute(query)
    profile = result.scalar_one_or_none()
    
    if not profile:
        return False
    
    await db.delete(profile)
    await db.commit()
    return True


# ============================================================================
# Billing History Operations
# ============================================================================

async def get_user_billing_history(
    db: AsyncSession,
    user_id: str,
    limit: int = 50,
) -> List[BillingHistory]:
    """Get billing history for a user."""
    query = (
        select(BillingHistory)
        .where(BillingHistory.user_id == user_id)
        .order_by(BillingHistory.billing_date.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_billing_record(
    db: AsyncSession,
    subscription_id: int,
    user_id: str,
    amount: float,
    currency: str,
    status: str,
    description: Optional[str] = None,
    stripe_invoice_id: Optional[str] = None,
    stripe_charge_id: Optional[str] = None,
    invoice_url: Optional[str] = None,
    invoice_pdf: Optional[str] = None,
) -> BillingHistory:
    """Create a billing history record."""
    billing = BillingHistory(
        subscription_id=subscription_id,
        user_id=user_id,
        amount=amount,
        currency=currency,
        status=status,
        description=description,
        stripe_invoice_id=stripe_invoice_id,
        stripe_charge_id=stripe_charge_id,
        invoice_url=invoice_url,
        invoice_pdf=invoice_pdf,
        billing_date=datetime.utcnow(),
    )
    db.add(billing)
    await db.commit()
    await db.refresh(billing)
    return billing


async def update_billing_record(
    db: AsyncSession,
    billing_id: int,
    **kwargs
) -> Optional[BillingHistory]:
    """Update billing record."""
    query = select(BillingHistory).where(BillingHistory.id == billing_id)
    result = await db.execute(query)
    billing = result.scalar_one_or_none()
    
    if not billing:
        return None
    
    for key, value in kwargs.items():
        if hasattr(billing, key):
            setattr(billing, key, value)
    
    await db.commit()
    await db.refresh(billing)
    return billing
