-- ============================================================================
-- SUPABASE SCHEMA VERIFICATION SCRIPT
-- Date: 2025-12-17
-- Purpose: Verify all migrations were applied correctly
-- ============================================================================

-- ============================================================================
-- 1. VERIFY ALL TABLES EXIST
-- ============================================================================
SELECT
    table_name,
    CASE
        WHEN table_name IN ('users', 'messages', 'follow_ups', 'configs', 'deals', 'notes',
                           'tags', 'user_tags', 'subscription_plans', 'user_subscriptions',
                           'usage_tracking', 'billing_history', 'user_profiles', 'channel_integrations')
        THEN '✅ EXISTS'
        ELSE '❌ UNEXPECTED'
    END AS status
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- ============================================================================
-- 2. VERIFY USERS TABLE COLUMNS (Most Critical)
-- ============================================================================
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default,
    CASE
        WHEN column_name IN ('id', 'phone', 'name', 'email', 'auth_user_id', 'channel',
                             'channel_user_id', 'channel_username', 'channel_profile_pic_url',
                             'created_at', 'updated_at', 'intent_score', 'sentiment', 'stage',
                             'conversation_mode', 'conversation_summary', 'hubspot_contact_id',
                             'hubspot_lifecyclestage', 'hubspot_synced_at', 'whatsapp_profile_name',
                             'country_code', 'phone_formatted', 'first_contact_timestamp',
                             'media_count', 'location_shared', 'last_twilio_message_sid',
                             'total_messages', 'last_message_at')
        THEN '✅ EXPECTED'
        ELSE '❌ UNEXPECTED'
    END AS status
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- ============================================================================
-- 3. VERIFY CRITICAL COLUMN EXISTS (Fix for original error)
-- ============================================================================
SELECT
    CASE
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'channel'
        ) THEN '✅ users.channel EXISTS'
        ELSE '❌ users.channel MISSING - CRITICAL ERROR'
    END AS channel_column_check;

-- ============================================================================
-- 4. VERIFY INDEXES ON USERS TABLE
-- ============================================================================
SELECT
    indexname,
    indexdef,
    CASE
        WHEN indexname IN ('idx_users_channel', 'idx_users_channel_user_id',
                          'idx_users_auth_user_id', 'idx_users_hubspot_contact_id')
        THEN '✅ EXPECTED'
        ELSE 'ℹ️ OTHER'
    END AS status
FROM pg_indexes
WHERE tablename = 'users'
ORDER BY indexname;

-- ============================================================================
-- 5. VERIFY MESSAGES TABLE COLUMNS
-- ============================================================================
SELECT
    column_name,
    data_type,
    is_nullable,
    CASE
        WHEN column_name IN ('id', 'user_id', 'message_text', 'sender', 'timestamp',
                             'message_metadata', 'channel', 'channel_message_id')
        THEN '✅ EXPECTED'
        ELSE '❌ UNEXPECTED'
    END AS status
FROM information_schema.columns
WHERE table_name = 'messages'
ORDER BY ordinal_position;

-- ============================================================================
-- 6. VERIFY DEALS TABLE COLUMNS
-- ============================================================================
SELECT
    column_name,
    data_type,
    is_nullable,
    CASE
        WHEN column_name IN ('id', 'user_id', 'title', 'value', 'currency', 'stage',
                             'probability', 'source', 'expected_close_date', 'won_date',
                             'lost_date', 'lost_reason', 'manually_qualified', 'created_at', 'updated_at')
        THEN '✅ EXPECTED'
        ELSE '❌ UNEXPECTED'
    END AS status
FROM information_schema.columns
WHERE table_name = 'deals'
ORDER BY ordinal_position;

-- ============================================================================
-- 7. VERIFY SUBSCRIPTION TABLES EXIST
-- ============================================================================
SELECT
    'subscription_plans' AS table_name,
    COUNT(*) AS column_count,
    CASE
        WHEN COUNT(*) >= 10 THEN '✅ TABLE EXISTS'
        ELSE '❌ MISSING COLUMNS'
    END AS status
FROM information_schema.columns
WHERE table_name = 'subscription_plans'

UNION ALL

SELECT
    'user_subscriptions' AS table_name,
    COUNT(*) AS column_count,
    CASE
        WHEN COUNT(*) >= 15 THEN '✅ TABLE EXISTS'
        ELSE '❌ MISSING COLUMNS'
    END AS status
FROM information_schema.columns
WHERE table_name = 'user_subscriptions'

UNION ALL

SELECT
    'usage_tracking' AS table_name,
    COUNT(*) AS column_count,
    CASE
        WHEN COUNT(*) >= 11 THEN '✅ TABLE EXISTS'
        ELSE '❌ MISSING COLUMNS'
    END AS status
FROM information_schema.columns
WHERE table_name = 'usage_tracking';

-- ============================================================================
-- 8. VERIFY CHANNEL_INTEGRATIONS TABLE
-- ============================================================================
SELECT
    column_name,
    data_type,
    is_nullable,
    CASE
        WHEN column_name IN ('id', 'auth_user_id', 'channel', 'page_id', 'page_access_token',
                             'page_name', 'instagram_account_id', 'is_active',
                             'webhook_verify_token', 'created_at', 'updated_at')
        THEN '✅ EXPECTED'
        ELSE '❌ UNEXPECTED'
    END AS status
FROM information_schema.columns
WHERE table_name = 'channel_integrations'
ORDER BY ordinal_position;

-- ============================================================================
-- 9. VERIFY FOREIGN KEY CONSTRAINTS
-- ============================================================================
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    '✅ CONSTRAINT EXISTS' AS status
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
ORDER BY tc.table_name, tc.constraint_name;

-- ============================================================================
-- 10. VERIFY UNIQUE CONSTRAINTS
-- ============================================================================
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    '✅ UNIQUE CONSTRAINT EXISTS' AS status
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'UNIQUE'
    AND tc.table_schema = 'public'
ORDER BY tc.table_name, tc.constraint_name;

-- ============================================================================
-- 11. VERIFY TRIGGERS EXIST
-- ============================================================================
SELECT
    trigger_name,
    event_object_table AS table_name,
    action_statement,
    '✅ TRIGGER EXISTS' AS status
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;

-- ============================================================================
-- 12. COUNT ROWS IN EACH TABLE
-- ============================================================================
-- Note: These queries will show actual data counts

SELECT 'users' AS table_name, COUNT(*) AS row_count FROM users
UNION ALL
SELECT 'messages', COUNT(*) FROM messages
UNION ALL
SELECT 'deals', COUNT(*) FROM deals
UNION ALL
SELECT 'notes', COUNT(*) FROM notes
UNION ALL
SELECT 'tags', COUNT(*) FROM tags
UNION ALL
SELECT 'user_tags', COUNT(*) FROM user_tags
UNION ALL
SELECT 'subscription_plans', COUNT(*) FROM subscription_plans
UNION ALL
SELECT 'user_subscriptions', COUNT(*) FROM user_subscriptions
UNION ALL
SELECT 'usage_tracking', COUNT(*) FROM usage_tracking
UNION ALL
SELECT 'user_profiles', COUNT(*) FROM user_profiles
UNION ALL
SELECT 'channel_integrations', COUNT(*) FROM channel_integrations;

-- ============================================================================
-- 13. FINAL HEALTH CHECK
-- ============================================================================
SELECT
    'SCHEMA HEALTH CHECK' AS check_type,
    CASE
        WHEN (
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('users', 'messages', 'deals', 'notes', 'tags',
                              'user_tags', 'subscription_plans', 'user_subscriptions',
                              'usage_tracking', 'user_profiles', 'channel_integrations')
        ) = 11
        AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'channel')
        AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'deals' AND column_name = 'manually_qualified')
        THEN '✅ ALL CRITICAL MIGRATIONS APPLIED'
        ELSE '❌ MISSING CRITICAL TABLES/COLUMNS'
    END AS result;

-- ============================================================================
-- END OF VERIFICATION SCRIPT
-- ============================================================================
-- Expected result: All checks should show ✅ status
-- If any check shows ❌, review the migration script and re-apply
-- ============================================================================
