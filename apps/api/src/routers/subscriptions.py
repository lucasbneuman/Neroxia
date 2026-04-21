"""Subscription management router - plans, billing, and usage tracking."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..routers.auth import get_current_user
from ..database import get_db as get_db_session, AsyncSessionLocal
from neroxia_database.subscription_crud import (
    get_all_subscription_plans,
    get_current_usage,
    get_user_billing_history,
    get_user_subscription,
    update_user_subscription,
    cancel_user_subscription,
)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


# ============================================================================
# Pydantic Models
# ============================================================================


class SubscriptionPlanResponse(BaseModel):
    """Subscription plan response model."""

    id: int
    name: str
    display_name: str
    description: Optional[str]
    price: float
    currency: str
    billing_period: str
    features: dict
    is_active: bool
    sort_order: int


class UserSubscriptionResponse(BaseModel):
    """User subscription response model."""

    id: int
    user_id: str
    plan: SubscriptionPlanResponse
    status: str
    current_period_start: str
    current_period_end: str
    trial_ends_at: Optional[str]
    canceled_at: Optional[str]
    cancel_at_period_end: bool


class UsageResponse(BaseModel):
    """Usage tracking response model."""

    messages_sent: int
    messages_limit: int
    bots_created: int
    bots_limit: int
    rag_storage_mb: float
    rag_storage_limit_mb: int
    api_calls: int
    api_calls_limit: int
    period_start: str
    period_end: str


class BillingHistoryResponse(BaseModel):
    """Billing history item response model."""

    id: int
    amount: float
    currency: str
    status: str
    description: Optional[str]
    invoice_url: Optional[str]
    billing_date: str
    paid_at: Optional[str]


# ============================================================================
# Helper Functions
# ============================================================================


async def get_db():
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session


def check_usage_limit(current: int | float, limit: int | float) -> bool:
    """Check if usage is within limit. Returns True if within limit."""
    if limit == -1:  # Unlimited
        return True
    return current < limit


# ============================================================================
# Endpoints
# ============================================================================


@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_subscription_plans(db=Depends(get_db)):
    """
    Get all available subscription plans.

    Returns list of active subscription plans with features and pricing.
    """
    plans = await get_all_subscription_plans(db, active_only=True)

    return [
        {
            "id": plan.id,
            "name": plan.name,
            "display_name": plan.display_name,
            "description": plan.description,
            "price": plan.price,
            "currency": plan.currency,
            "billing_period": plan.billing_period,
            "features": plan.features,
            "is_active": plan.is_active,
            "sort_order": plan.sort_order,
        }
        for plan in plans
    ]


@router.get("/current", response_model=UserSubscriptionResponse)
async def get_current_subscription(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get current user's subscription.

    Returns subscription details including plan, status, and billing period.
    If no subscription exists, creates one with free_trial plan (lazy creation).
    """
    user_id = current_user["id"]

    subscription = await get_user_subscription(db, user_id)

    # Lazy creation: create free_trial subscription if none exists
    if not subscription:
        from neroxia_database.subscription_crud import (
            create_user_subscription,
            get_subscription_plan_by_name,
        )
        from datetime import datetime, timedelta

        # Get free_trial plan
        trial_plan = await get_subscription_plan_by_name(db, "free_trial")
        if not trial_plan:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Free trial plan not configured. Please contact support.",
            )

        # Create trial subscription
        now = datetime.utcnow()
        trial_days = 14
        subscription = await create_user_subscription(
            db=db,
            user_id=user_id,
            plan_id=trial_plan.id,
            status="trial",
            trial_days=trial_days,
        )

    return {
        "id": subscription.id,
        "user_id": subscription.user_id,
        "plan": {
            "id": subscription.plan.id,
            "name": subscription.plan.name,
            "display_name": subscription.plan.display_name,
            "description": subscription.plan.description,
            "price": subscription.plan.price,
            "currency": subscription.plan.currency,
            "billing_period": subscription.plan.billing_period,
            "features": subscription.plan.features,
            "is_active": subscription.plan.is_active,
            "sort_order": subscription.plan.sort_order,
        },
        "status": subscription.status,
        "current_period_start": subscription.current_period_start.isoformat(),
        "current_period_end": subscription.current_period_end.isoformat(),
        "trial_ends_at": subscription.trial_ends_at.isoformat() if subscription.trial_ends_at else None,
        "canceled_at": subscription.canceled_at.isoformat() if subscription.canceled_at else None,
        "cancel_at_period_end": subscription.cancel_at_period_end,
    }


@router.get("/usage", response_model=UsageResponse)
async def get_usage_metrics(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get current usage metrics vs limits.

    Returns usage for messages, bots, storage, and API calls.
    If no subscription exists, creates one with free_trial plan (lazy creation).
    """
    user_id = current_user["id"]

    # Get subscription to get limits
    subscription = await get_user_subscription(db, user_id)

    # Lazy creation: create free_trial subscription if none exists
    if not subscription:
        from neroxia_database.subscription_crud import (
            create_user_subscription,
            get_subscription_plan_by_name,
        )
        from datetime import datetime, timedelta

        # Get free_trial plan
        trial_plan = await get_subscription_plan_by_name(db, "free_trial")
        if not trial_plan:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Free trial plan not configured. Please contact support.",
            )

        # Create trial subscription
        now = datetime.utcnow()
        trial_days = 14
        subscription = await create_user_subscription(
            db=db,
            user_id=user_id,
            plan_id=trial_plan.id,
            status="trial",
            trial_days=trial_days,
        )

    # Get current usage
    usage = await get_current_usage(db, user_id)
    if not usage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usage tracking not found",
        )

    features = subscription.plan.features

    return {
        "messages_sent": usage.messages_sent,
        "messages_limit": features.get("messages_per_month", 0),
        "bots_created": usage.bots_created,
        "bots_limit": features.get("bots_limit", 1),
        "rag_storage_mb": usage.rag_storage_mb,
        "rag_storage_limit_mb": features.get("rag_storage_mb", 50),
        "api_calls": usage.api_calls,
        "api_calls_limit": features.get("api_calls_per_day", 1000),
        "period_start": usage.period_start.isoformat(),
        "period_end": usage.period_end.isoformat(),
    }


@router.get("/billing-history", response_model=List[BillingHistoryResponse])
async def get_billing_history(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
    limit: int = 50,
):
    """
    Get billing history.

    Returns list of past invoices and payments.
    """
    user_id = current_user["id"]

    history = await get_user_billing_history(db, user_id, limit=limit)

    return [
        {
            "id": item.id,
            "amount": item.amount,
            "currency": item.currency,
            "status": item.status,
            "description": item.description,
            "invoice_url": item.invoice_url,
            "billing_date": item.billing_date.isoformat(),
            "paid_at": item.paid_at.isoformat() if item.paid_at else None,
        }
        for item in history
    ]


@router.post("/cancel")
async def cancel_subscription(
    cancel_at_period_end: bool = True,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Cancel subscription.

    If cancel_at_period_end is True, subscription remains active until end of billing period.
    If False, subscription is canceled immediately.
    """
    user_id = current_user["id"]

    subscription = await cancel_user_subscription(db, user_id, cancel_at_period_end)

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found",
        )

    return {
        "status": "success",
        "message": "Subscription canceled" if not cancel_at_period_end else "Subscription will cancel at period end",
        "canceled_at": subscription.canceled_at.isoformat() if subscription.canceled_at else None,
        "cancel_at_period_end": subscription.cancel_at_period_end,
    }


# ============================================================================
# Usage Limit Checking (for use in other routers)
# ============================================================================


async def check_message_limit(user_id: str, db) -> bool:
    """Check if user has reached message limit."""
    subscription = await get_user_subscription(db, user_id)
    if not subscription:
        return False

    usage = await get_current_usage(db, user_id)
    if not usage:
        return False

    limit = subscription.plan.features.get("messages_per_month", 0)
    return check_usage_limit(usage.messages_sent, limit)


async def check_bot_limit(user_id: str, db) -> bool:
    """Check if user has reached bot creation limit."""
    subscription = await get_user_subscription(db, user_id)
    if not subscription:
        return False

    usage = await get_current_usage(db, user_id)
    if not usage:
        return False

    limit = subscription.plan.features.get("bots_limit", 1)
    return check_usage_limit(usage.bots_created, limit)


async def check_rag_storage_limit(user_id: str, db, additional_mb: float = 0) -> bool:
    """Check if user has reached RAG storage limit."""
    subscription = await get_user_subscription(db, user_id)
    if not subscription:
        return False

    usage = await get_current_usage(db, user_id)
    if not usage:
        return False

    limit = subscription.plan.features.get("rag_storage_mb", 50)
    return check_usage_limit(usage.rag_storage_mb + additional_mb, limit)
