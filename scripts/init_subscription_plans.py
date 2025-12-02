"""Initialize default subscription plans in the database."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from packages.database.whatsapp_bot_database import AsyncSessionLocal
from packages.database.whatsapp_bot_database.subscription_crud import (
    create_subscription_plan,
    get_subscription_plan_by_name,
)


async def init_subscription_plans():
    """Initialize default subscription plans."""
    async with AsyncSessionLocal() as db:
        # Free Trial Plan
        trial_plan = await get_subscription_plan_by_name(db, "free_trial")
        if not trial_plan:
            print("Creating Free Trial plan...")
            await create_subscription_plan(
                db=db,
                name="free_trial",
                display_name="Free Trial",
                description="14-day free trial with limited features",
                price=0.0,
                currency="USD",
                billing_period="trial",
                features={
                    "messages_per_month": 100,
                    "bots_limit": 1,
                    "rag_storage_mb": 50,
                    "api_calls_per_day": 1000,
                    "team_members": 1,
                    "integrations": ["twilio"],
                    "support": "community",
                    "features": ["basic_bot", "manual_handoff"],
                },
                sort_order=0,
            )
            print("✓ Free Trial plan created")
        else:
            print("✓ Free Trial plan already exists")

        # Professional Plan
        pro_plan = await get_subscription_plan_by_name(db, "professional")
        if not pro_plan:
            print("Creating Professional plan...")
            await create_subscription_plan(
                db=db,
                name="professional",
                display_name="Professional",
                description="Perfect for growing businesses",
                price=49.0,
                currency="USD",
                billing_period="monthly",
                features={
                    "messages_per_month": 5000,
                    "bots_limit": 3,
                    "rag_storage_mb": 500,
                    "api_calls_per_day": 10000,
                    "team_members": 5,
                    "integrations": ["twilio", "hubspot"],
                    "support": "email",
                    "features": [
                        "advanced_bot",
                        "rag",
                        "tts",
                        "manual_handoff",
                        "analytics",
                        "crm",
                    ],
                },
                sort_order=1,
            )
            print("✓ Professional plan created")
        else:
            print("✓ Professional plan already exists")

        # Enterprise Plan
        enterprise_plan = await get_subscription_plan_by_name(db, "enterprise")
        if not enterprise_plan:
            print("Creating Enterprise plan...")
            await create_subscription_plan(
                db=db,
                name="enterprise",
                display_name="Enterprise",
                description="Unlimited power for large organizations",
                price=199.0,
                currency="USD",
                billing_period="monthly",
                features={
                    "messages_per_month": -1,  # Unlimited
                    "bots_limit": -1,  # Unlimited
                    "rag_storage_mb": 5000,
                    "api_calls_per_day": -1,  # Unlimited
                    "team_members": -1,  # Unlimited
                    "integrations": ["twilio", "hubspot", "custom"],
                    "support": "priority",
                    "features": [
                        "advanced_bot",
                        "rag",
                        "tts",
                        "manual_handoff",
                        "analytics",
                        "crm",
                        "custom_integrations",
                        "dedicated_support",
                        "sla",
                    ],
                },
                sort_order=2,
            )
            print("✓ Enterprise plan created")
        else:
            print("✓ Enterprise plan already exists")

        print("\n✅ All subscription plans initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_subscription_plans())
