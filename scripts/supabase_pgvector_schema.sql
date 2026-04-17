-- ============================================================================
-- Supabase pgvector Setup for RAG System
-- ============================================================================
-- Run this script in Supabase SQL Editor to enable vector search
-- Dashboard > SQL Editor > New Query > Paste this script > Run
-- ============================================================================

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- DOCUMENTS TABLE (Vector Store)
-- ============================================================================
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding VECTOR(1536),  -- OpenAI text-embedding-3-small produces 1536 dimensions
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for vector similarity search (using cosine distance)
CREATE INDEX IF NOT EXISTS documents_embedding_idx 
ON documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index for metadata queries
CREATE INDEX IF NOT EXISTS documents_metadata_idx 
ON documents 
USING GIN (metadata);

-- ============================================================================
-- SIMILARITY SEARCH FUNCTION
-- ============================================================================
-- This function is used by LangChain's SupabaseVectorStore
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding VECTOR(1536),
    match_count INT DEFAULT 5,
    filter JSONB DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    id BIGINT,
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
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================
-- Enable RLS on documents table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create permissive policy (safe because backend uses service_role key)
CREATE POLICY "Allow all operations on documents" ON documents
    FOR ALL
    USING (true)
    WITH CHECK (true);

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

-- Check that pgvector extension is enabled
SELECT 
    extname,
    extversion
FROM pg_extension
WHERE extname = 'vector';

-- Check that documents table was created
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename = 'documents';

-- Check that indexes were created
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename = 'documents'
ORDER BY indexname;

-- Check that match_documents function exists
SELECT
    routine_name,
    routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
    AND routine_name = 'match_documents';

-- Check RLS policies
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    cmd
FROM pg_policies
WHERE schemaname = 'public'
    AND tablename = 'documents';

-- Get current document count
SELECT get_documents_count() as total_documents;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT 
    '✅ pgvector setup completed successfully!' as status,
    'You can now use Supabase for RAG vector search.' as message,
    NOW() as created_at;

-- ============================================================================
-- NEXT STEPS
-- ============================================================================
-- 1. Add SUPABASE_SERVICE_KEY to your .env file
-- 2. Restart your API server
-- 3. Upload a test document via /rag/upload endpoint
-- 4. Verify documents appear in this table
-- ============================================================================
