-- ============================================================================
-- Multi-Tenant Config System Migration
-- ============================================================================
-- This script migrates the configs table to support multi-tenant architecture
-- Each user will have their own independent configuration
--
-- Run this in Supabase SQL Editor
-- ============================================================================

-- ============================================================================
-- STEP 1: Add user_id column to configs table
-- ============================================================================

-- Add user_id column (nullable initially for migration)
ALTER TABLE configs 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_configs_user_id ON configs(user_id);

-- ============================================================================
-- STEP 2: Migrate existing data (assign to first user or admin)
-- ============================================================================

-- Option 1: Assign all existing configs to the first user in auth.users
-- Uncomment and modify if you want to keep existing configs for a specific user
/*
UPDATE configs 
SET user_id = (SELECT id FROM auth.users ORDER BY created_at LIMIT 1)
WHERE user_id IS NULL;
*/

-- Option 2: Delete existing configs (users will create their own)
-- This is cleaner for a fresh multi-tenant start
DELETE FROM configs WHERE user_id IS NULL;

-- ============================================================================
-- STEP 3: Make user_id NOT NULL and update constraints
-- ============================================================================

-- Make user_id required
ALTER TABLE configs 
ALTER COLUMN user_id SET NOT NULL;

-- Drop old unique constraint on key
ALTER TABLE configs 
DROP CONSTRAINT IF EXISTS configs_key_key;

-- Create new composite unique constraint (user_id + key)
-- This allows each user to have their own "system_prompt", "product_name", etc.
ALTER TABLE configs 
ADD CONSTRAINT configs_user_key_unique UNIQUE (user_id, key);

-- ============================================================================
-- STEP 4: Enable Row Level Security (RLS)
-- ============================================================================

-- Enable RLS on configs table
ALTER TABLE configs ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own configs" ON configs;
DROP POLICY IF EXISTS "Users can insert own configs" ON configs;
DROP POLICY IF EXISTS "Users can update own configs" ON configs;
DROP POLICY IF EXISTS "Users can delete own configs" ON configs;

-- Policy for SELECT: Users can only view their own configs
CREATE POLICY "Users can view own configs"
ON configs FOR SELECT
USING (auth.uid() = user_id);

-- Policy for INSERT: Users can only create configs with their own user_id
CREATE POLICY "Users can insert own configs"
ON configs FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Policy for UPDATE: Users can only update their own configs
CREATE POLICY "Users can update own configs"
ON configs FOR UPDATE
USING (auth.uid() = user_id);

-- Policy for DELETE: Users can only delete their own configs
CREATE POLICY "Users can delete own configs"
ON configs FOR DELETE
USING (auth.uid() = user_id);

-- ============================================================================
-- STEP 5: Helper Functions (Optional)
-- ============================================================================

-- Function to get all configs for a specific user
CREATE OR REPLACE FUNCTION get_user_configs(user_id_param UUID)
RETURNS TABLE (
    id INTEGER,
    key VARCHAR,
    value JSONB,
    updated_at TIMESTAMP
)
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT id, key, value, updated_at
    FROM configs
    WHERE user_id = user_id_param
    ORDER BY key;
$$;

-- Function to initialize default configs for a new user
CREATE OR REPLACE FUNCTION initialize_user_defaults(user_id_param UUID)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    inserted_count INTEGER := 0;
BEGIN
    -- Check if user already has configs
    IF EXISTS (SELECT 1 FROM configs WHERE user_id = user_id_param) THEN
        RETURN 0;
    END IF;
    
    -- Insert default configs (empty values - user must configure)
    INSERT INTO configs (user_id, key, value) VALUES
        (user_id_param, 'system_prompt', '""'::jsonb),
        (user_id_param, 'welcome_message', '""'::jsonb),
        (user_id_param, 'payment_link', '""'::jsonb),
        (user_id_param, 'response_delay_minutes', '0.5'::jsonb),
        (user_id_param, 'text_audio_ratio', '0'::jsonb),
        (user_id_param, 'use_emojis', 'true'::jsonb),
        (user_id_param, 'tts_voice', '"nova"'::jsonb),
        (user_id_param, 'multi_part_messages', 'false'::jsonb),
        (user_id_param, 'max_words_per_response', '100'::jsonb),
        (user_id_param, 'product_name', '""'::jsonb),
        (user_id_param, 'product_description', '""'::jsonb),
        (user_id_param, 'product_features', '""'::jsonb),
        (user_id_param, 'product_benefits', '""'::jsonb),
        (user_id_param, 'product_price', '""'::jsonb),
        (user_id_param, 'product_target_audience', '""'::jsonb)
    ON CONFLICT (user_id, key) DO NOTHING;
    
    GET DIAGNOSTICS inserted_count = ROW_COUNT;
    RETURN inserted_count;
END;
$$;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check that user_id column exists and is NOT NULL
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'configs'
    AND column_name = 'user_id';

-- Check unique constraint
SELECT
    conname as constraint_name,
    contype as constraint_type
FROM pg_constraint
WHERE conname LIKE '%configs%'
    AND conrelid = 'configs'::regclass;

-- Check RLS is enabled
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE tablename = 'configs';

-- Check RLS policies
SELECT 
    policyname,
    cmd
FROM pg_policies
WHERE tablename = 'configs'
ORDER BY policyname;

-- Check helper functions exist
SELECT routine_name
FROM information_schema.routines
WHERE routine_name IN ('get_user_configs', 'initialize_user_defaults')
ORDER BY routine_name;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT 
    '✅ Multi-tenant config system configured successfully!' as status,
    'Each user now has independent configuration.' as message,
    NOW() as created_at;

-- ============================================================================
-- NOTES
-- ============================================================================
-- 
-- After running this migration:
-- 1. Each user will have their own configs (system_prompt, product_name, etc.)
-- 2. RLS ensures users cannot see/modify other users' configs
-- 3. The unique constraint (user_id, key) allows duplicate keys across users
-- 4. Backend code must pass user_id when loading/saving configs
--
-- Next steps:
-- 1. Update config_manager.py to accept user_id parameter
-- 2. Update config.py router to extract user_id from JWT
-- 3. Test with multiple users
--
-- ============================================================================
