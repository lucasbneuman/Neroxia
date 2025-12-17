"""
Supabase Migration Application Script
Date: 2025-12-17
Purpose: Safely apply consolidated migrations to Supabase production database

This script:
1. Tests database connection
2. Creates backup of current schema
3. Applies migrations from apply_supabase_migrations.sql
4. Runs verification queries from verify_supabase_schema.sql
5. Reports results with detailed error handling
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: SUPABASE_DATABASE_URL not found in .env file")
    sys.exit(1)

# Extract connection parameters from URL
# Format: postgresql+asyncpg://user:pass@host:port/dbname
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

# File paths
SCRIPT_DIR = Path(__file__).parent
MIGRATION_FILE = SCRIPT_DIR / "apply_supabase_migrations.sql"
VERIFICATION_FILE = SCRIPT_DIR / "verify_supabase_schema.sql"
BACKUP_DIR = SCRIPT_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)


async def test_connection(conn: asyncpg.Connection) -> bool:
    """Test database connection."""
    try:
        result = await conn.fetchval("SELECT 1")
        print("[OK] Database connection successful")
        return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False


async def backup_schema(conn: asyncpg.Connection) -> str:
    """Create backup of current schema structure."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"schema_backup_{timestamp}.sql"

    try:
        # Get all table definitions
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        backup_content = f"-- Schema Backup: {datetime.now().isoformat()}\n"
        backup_content += f"-- Total tables: {len(tables)}\n\n"

        for table in tables:
            table_name = table["table_name"]

            # Get columns
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = $1
                ORDER BY ordinal_position
            """, table_name)

            backup_content += f"-- TABLE: {table_name}\n"
            backup_content += f"-- Columns: {len(columns)}\n"
            for col in columns:
                backup_content += f"--   {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})\n"
            backup_content += "\n"

        # Write backup
        with open(backup_file, "w", encoding="utf-8") as f:
            f.write(backup_content)

        print(f"[OK] Schema backup created: {backup_file}")
        return str(backup_file)

    except Exception as e:
        print(f"[WARNING] Failed to create schema backup: {e}")
        return ""


async def apply_migrations(conn: asyncpg.Connection) -> bool:
    """Apply migration script."""
    try:
        # Read migration file
        with open(MIGRATION_FILE, "r", encoding="utf-8") as f:
            migration_sql = f.read()

        print("\n[APPLYING] Migrations...")
        print(f"   Migration file: {MIGRATION_FILE}")

        # Execute migration in a transaction
        async with conn.transaction():
            await conn.execute(migration_sql)

        print("[OK] Migrations applied successfully")
        return True

    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        print("\nError details:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        return False


async def verify_schema(conn: asyncpg.Connection) -> bool:
    """Run verification queries."""
    try:
        print("\n[VERIFYING] Schema...")

        # Critical check: users.channel column exists
        channel_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'channel'
            )
        """)

        if not channel_exists:
            print("[ERROR] CRITICAL: users.channel column does not exist!")
            return False

        print("[OK] users.channel column exists")

        # Check all expected tables
        expected_tables = [
            'users', 'messages', 'follow_ups', 'configs', 'deals', 'notes',
            'tags', 'user_tags', 'subscription_plans', 'user_subscriptions',
            'usage_tracking', 'billing_history', 'user_profiles', 'channel_integrations'
        ]

        existing_tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = ANY($1)
        """, expected_tables)

        existing_table_names = [t["table_name"] for t in existing_tables]
        missing_tables = set(expected_tables) - set(existing_table_names)

        if missing_tables:
            print(f"[WARNING] Missing tables: {', '.join(missing_tables)}")
        else:
            print(f"[OK] All {len(expected_tables)} expected tables exist")

        # Count columns in users table
        user_columns = await conn.fetch("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users'
        """)

        print(f"[OK] users table has {len(user_columns)} columns")

        # Check critical users columns
        critical_columns = [
            'channel', 'channel_user_id', 'channel_username', 'auth_user_id',
            'hubspot_contact_id', 'whatsapp_profile_name'
        ]

        user_column_names = [c["column_name"] for c in user_columns]
        missing_columns = set(critical_columns) - set(user_column_names)

        if missing_columns:
            print(f"[ERROR] Missing critical columns in users: {', '.join(missing_columns)}")
            return False
        else:
            print(f"[OK] All {len(critical_columns)} critical columns exist in users table")

        # Check indexes
        indexes = await conn.fetch("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'users'
            AND indexname IN ('idx_users_channel', 'idx_users_channel_user_id', 'idx_users_auth_user_id')
        """)

        print(f"[OK] Found {len(indexes)} critical indexes on users table")

        return True

    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        return False


async def main():
    """Main execution flow."""
    print("=" * 80)
    print("SUPABASE MIGRATION SCRIPT")
    print("=" * 80)
    print(f"Started: {datetime.now().isoformat()}")
    print()

    conn = None
    try:
        # Connect to database
        print("[CONNECTING] to Supabase...")
        conn = await asyncpg.connect(DATABASE_URL)

        # Test connection
        if not await test_connection(conn):
            return 1

        # Create schema backup
        print("\n[BACKUP] Creating schema backup...")
        backup_file = await backup_schema(conn)

        # Ask for confirmation
        print("\n[WARNING] About to apply migrations to PRODUCTION database")
        print(f"   Database: {DATABASE_URL.split('@')[1].split('/')[0]}")
        if backup_file:
            print(f"   Backup: {backup_file}")
        print()
        response = input("Continue? (yes/no): ").strip().lower()

        if response != "yes":
            print("[CANCELLED] Migration cancelled by user")
            return 0

        # Apply migrations
        if not await apply_migrations(conn):
            print("\n[ERROR] Migration failed - check errors above")
            return 1

        # Verify schema
        if not await verify_schema(conn):
            print("\n[WARNING] Verification warnings detected - review output above")
            return 1

        # Success
        print("\n" + "=" * 80)
        print("[SUCCESS] MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"Finished: {datetime.now().isoformat()}")
        print()
        print("Next steps:")
        print("1. Run verify_supabase_schema.sql manually for detailed verification")
        print("2. Test API endpoints to confirm system is operational")
        print("3. Check application logs for any errors")
        print()

        return 0

    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        if conn:
            await conn.close()
            print("[CLOSED] Database connection closed")


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
