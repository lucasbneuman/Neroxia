-- ============================================================================
-- Supabase pgvector Functions for EXISTING documents table
-- ============================================================================
-- This script adds the missing functions to work with your existing documents table
-- Run this in Supabase SQL Editor
-- ============================================================================

-- ============================================================================
-- SIMILARITY SEARCH FUNCTION (for LangChain SupabaseVectorStore)
-- ============================================================================
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

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to get total document count
CREATE OR REPLACE FUNCTION get_documents_count()
RETURNS INTEGER
LANGUAGE sql
AS $$
    SELECT COUNT(*)::INTEGER FROM documents;
$$;

-- Function to clear all documents (useful for testing)
CREATE OR REPLACE FUNCTION clear_all_documents()
RETURNS VOID
LANGUAGE sql
AS $$
    DELETE FROM documents;
$$;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check that match_documents function exists
SELECT
    routine_name,
    routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
    AND routine_name = 'match_documents';

-- Check that helper functions exist
SELECT
    routine_name,
    routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
    AND routine_name IN ('get_documents_count', 'clear_all_documents')
ORDER BY routine_name;

-- Get current document count
SELECT get_documents_count() as total_documents;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT 
    '✅ RAG functions created successfully!' as status,
    'Your documents table is now ready for RAG operations.' as message,
    NOW() as created_at;

-- ============================================================================
-- NOTES
-- ============================================================================
-- Your documents table schema:
-- - id: UUID (not BIGINT)
-- - content: TEXT
-- - metadata: JSONB
-- - embedding: VECTOR(1536)
-- - user_id: UUID (references auth.users)
-- - created_at: TIMESTAMP WITH TIME ZONE
--
-- The match_documents function is compatible with LangChain's SupabaseVectorStore
-- ============================================================================
