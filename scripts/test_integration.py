"""
Integration test for WhatsApp Sales Bot SaaS Platform.

Tests that all packages work together:
- Shared utilities
- Database operations
- Bot-engine workflow
"""

import asyncio
import sys
from pathlib import Path

# Add packages to Python path
root_dir = Path(__file__).parent.parent
packages_dir = root_dir / "packages"
bot_engine_dir = root_dir / "apps" / "bot-engine" / "src"

sys.path.insert(0, str(packages_dir / "shared" / "src"))
sys.path.insert(0, str(packages_dir / "database" / "src"))
sys.path.insert(0, str(bot_engine_dir))


async def test_shared_package():
    """Test shared package imports."""
    print("\n" + "=" * 60)
    print("TEST 1: Shared Package")
    print("=" * 60)

    try:
        from whatsapp_bot_shared import get_logger, format_phone_number

        # Test logger
        logger = get_logger("test")
        logger.info(" Logger initialized successfully")

        # Test phone formatter
        phone = format_phone_number("1234567890")
        print(f" Phone formatter works: {phone}")

        print(" Shared package test PASSED")
        return True
    except Exception as e:
        print(f"L Shared package test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_database_package():
    """Test database package imports."""
    print("\n" + "=" * 60)
    print("TEST 2: Database Package")
    print("=" * 60)

    try:
        from whatsapp_bot_database import Base, User, Message, Config, crud
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker

        print(" Database models imported successfully")
        print(f"   - Base: {Base}")
        print(f"   - User: {User}")
        print(f"   - Message: {Message}")
        print(f"   - Config: {Config}")
        print(f"   - CRUD: {crud}")

        # Test database connection
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print(" Database tables created successfully")

        # Test CRUD operations
        async with async_session() as session:
            # Create user
            user = await crud.create_user(session, phone="+1234567890")
            print(f" User created: {user.phone}")

            # Get user
            retrieved = await crud.get_user_by_phone(session, "+1234567890")
            print(f" User retrieved: {retrieved.phone}")

            # Create message
            message = await crud.create_message(
                session,
                user_id=user.id,
                message_text="Hello, bot!",
                sender="user"
            )
            print(f" Message created: {message.message_text}")

        print(" Database package test PASSED")
        return True

    except Exception as e:
        print(f"L Database package test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_bot_engine():
    """Test bot-engine workflow."""
    print("\n" + "=" * 60)
    print("TEST 3: Bot-Engine Workflow")
    print("=" * 60)

    try:
        from graph.workflow import process_message, get_sales_graph
        from whatsapp_bot_database import Base, crud
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker

        print(" Bot-engine imports successful")

        # Check graph compilation
        graph = get_sales_graph()
        print(f" Sales graph compiled: {type(graph)}")

        # Setup test database
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Test message processing
        async with async_session() as session:
            # Create test user
            user = await crud.create_user(session, phone="+5491234567890")

            # Set test configuration
            test_config = {
                "system_prompt": "You are a helpful sales assistant.",
                "welcome_message": "Hello! How can I help you today?",
                "product_name": "Test Product",
                "use_emojis": False,
                "payment_link": "https://example.com/pay"
            }

            # Process test message
            print("\n=è Processing test message: 'Hola'")
            result = await process_message(
                user_phone="+5491234567890",
                message="Hola",
                conversation_history=[],
                config=test_config,
                db_session=session,
                db_user=user
            )

            print("\n=é Bot Response:")
            print(f"   Response: {result.get('current_response', 'No response')}")
            print(f"   Stage: {result.get('stage', 'unknown')}")
            print(f"   Intent Score: {result.get('intent_score', 0.0)}")
            print(f"   Sentiment: {result.get('sentiment', 'neutral')}")

            print("\n Bot-engine workflow test PASSED")
            return True

    except Exception as e:
        print(f"L Bot-engine test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("WhatsApp Sales Bot - Integration Test Suite")
    print("=" * 60)

    results = []

    # Run tests
    results.append(await test_shared_package())
    results.append(await test_database_package())
    results.append(await test_bot_engine())

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n ALL TESTS PASSED!")
        return 0
    else:
        print(f"\nL {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
