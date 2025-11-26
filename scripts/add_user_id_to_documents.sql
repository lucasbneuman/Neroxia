-- ============================================================================
-- Add user_id column to documents table
-- ============================================================================
-- This allows associating RAG documents with the Supabase Auth user who uploaded them
-- Run this in Supabase SQL Editor
-- ============================================================================

-- Add user_id column (UUID type to match Supabase Auth users)
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS user_id UUID;

-- Create index for user_id queries
CREATE INDEX IF NOT EXISTS documents_user_id_idx 
ON documents (user_id);

-- Add foreign key constraint to auth.users (optional, for data integrity)
-- Note: This references Supabase's built-in auth.users table
ALTER TABLE documents
ADD CONSTRAINT documents_user_id_fkey 
FOREIGN KEY (user_id) 
REFERENCES auth.users(id) 
ON DELETE CASCADE;

-- Update the match_documents function to support user filtering
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding VECTOR(1536),
    match_count INT DEFAULT 5,
    filter JSONB DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    id BIGINT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT,
    user_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        documents.id,
        documents.content,
        documents.metadata,
        1 - (documents.embedding <=> query_embedding) AS similarity,
        documents.user_id
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
-- VERIFICATION
-- ============================================================================

-- Check that user_id column was added
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name = 'documents'
    AND column_name = 'user_id';

-- Check that index was created
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename = 'documents'
    AND indexname = 'documents_user_id_idx';

-- Check foreign key constraint
SELECT
    conname as constraint_name,
    contype as constraint_type
FROM pg_constraint
WHERE conname = 'documents_user_id_fkey';

SELECT 
    '✅ user_id column added successfully!' as status,
    'Documents can now be associated with Supabase Auth users.' as message;
