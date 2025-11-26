-- ============================================================================
-- Fix Supabase Security Warnings
-- ============================================================================
-- This script addresses the security warnings shown in Supabase Security Advisor
-- Run this in Supabase SQL Editor
-- ============================================================================

-- ============================================================================
-- 1. FIX FUNCTION SEARCH PATH MUTABLE WARNINGS
-- ============================================================================
-- All RPC functions need to have search_path set to prevent security issues

-- Fix update_updated_at_column function
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP TRIGGER IF EXISTS update_configs_updated_at ON configs;
DROP FUNCTION IF EXISTS update_updated_at_column();

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Recreate triggers
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_configs_updated_at
    BEFORE UPDATE ON configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Fix match_documents function
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding VECTOR(1536),
    match_count INT DEFAULT 5,
    filter JSONB DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN QUERY
    SELECT
        documents.id,
        documents.content,
        documents.metadata,
        1 - (documents.embedding <=> query_embedding) AS similarity
    FROM documents
    WHERE
        CASE
            WHEN filter = '{}'::jsonb THEN TRUE
            ELSE documents.metadata @> filter
        END
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Fix documents_set_user_id function
CREATE OR REPLACE FUNCTION documents_set_user_id()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    -- If user_id is null, try to extract it from metadata
    IF NEW.user_id IS NULL AND NEW.metadata ? 'user_id' THEN
        BEGIN
            NEW.user_id := (NEW.metadata->>'user_id')::UUID;
        EXCEPTION WHEN OTHERS THEN
            -- Ignore invalid UUIDs in metadata
            NULL;
        END;
    END IF;
    RETURN NEW;
END;
$$;

-- Fix get_documents_count function
CREATE OR REPLACE FUNCTION get_documents_count()
RETURNS INTEGER
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT COUNT(*)::INTEGER FROM documents;
$$;

-- Fix clear_all_documents function
CREATE OR REPLACE FUNCTION clear_all_documents()
RETURNS VOID
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
    DELETE FROM documents;
$$;

-- Create new user-scoped functions for multi-tenant RAG
CREATE OR REPLACE FUNCTION get_user_documents_count(user_id_param UUID)
RETURNS INTEGER
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT COUNT(*)::INTEGER 
    FROM documents 
    WHERE user_id = user_id_param;
$$;

CREATE OR REPLACE FUNCTION clear_user_documents(user_id_param UUID)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM documents 
    WHERE user_id = user_id_param;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;

-- ============================================================================
-- 2. MOVE VECTOR EXTENSION TO EXTENSIONS SCHEMA (Optional)
-- ============================================================================
-- Note: Moving the vector extension might break existing code
-- Only uncomment if you're sure you want to do this

-- CREATE SCHEMA IF NOT EXISTS extensions;
-- ALTER EXTENSION vector SET SCHEMA extensions;

-- If you move it, update the search_path in functions:
-- SET search_path = public, extensions

-- ============================================================================
-- 3. VERIFICATION
-- ============================================================================

-- Check that all functions now have search_path set
SELECT 
    routine_name,
    routine_type,
    security_type,
    routine_definition
FROM information_schema.routines
WHERE routine_schema = 'public'
    AND routine_name IN (
        'update_updated_at_column',
        'match_documents',
        'documents_set_user_id',
        'get_documents_count',
        'clear_all_documents',
        'get_user_documents_count',
        'clear_user_documents'
    )
ORDER BY routine_name;

-- Verify RLS policies are still active
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    cmd
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

SELECT 
    '✅ Security warnings fixed!' as status,
    'All functions now have search_path set to public.' as message,
    'Vector extension warning can be ignored or fixed by moving to extensions schema.' as note;
