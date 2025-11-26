-- ============================================================================
-- FIX RAG SETUP: Recreate documents table with UUID and user_id
-- ============================================================================
-- The previous table had 'id' as BIGINT, but LangChain sends UUIDs.
-- We also need 'user_id' to associate documents with users.
-- ============================================================================

-- 1. Drop existing table and function to start fresh
DROP TABLE IF EXISTS documents CASCADE;
DROP FUNCTION IF EXISTS match_documents;

-- 2. Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 3. Create documents table with UUID primary key
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding VECTOR(1536),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Create indexes
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX ON documents USING GIN (metadata);
CREATE INDEX ON documents (user_id);

-- 5. Create match_documents function with user_id support
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

-- 6. Create a trigger to automatically populate user_id from metadata
-- This allows LangChain (which only sends metadata) to populate the user_id column
CREATE OR REPLACE FUNCTION documents_set_user_id()
RETURNS TRIGGER AS $$
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
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_user_id_from_metadata
    BEFORE INSERT ON documents
    FOR EACH ROW
    EXECUTE FUNCTION documents_set_user_id();

-- 7. Enable RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 8. Create RLS policies
-- Allow users to insert their own documents
CREATE POLICY "Users can insert their own documents" ON documents
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Allow users to select their own documents
CREATE POLICY "Users can select their own documents" ON documents
    FOR SELECT USING (auth.uid() = user_id);

-- Allow users to delete their own documents
CREATE POLICY "Users can delete their own documents" ON documents
    FOR DELETE USING (auth.uid() = user_id);

-- (Optional) Allow service role full access
CREATE POLICY "Service role has full access" ON documents
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Success message
SELECT '✅ Table recreated with UUID id and user_id column' as status;
