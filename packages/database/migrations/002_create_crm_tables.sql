-- ============================================================================
-- CRM Module Database Migration
-- ============================================================================
-- This script creates the necessary tables for the CRM module:
-- - deals: Sales opportunities/pipeline
-- - notes: Activities and notes per contact
-- tags: Customer segmentation labels
-- - user_tags: Many-to-many relationship between users and tags
-- ============================================================================

-- Create deals table
CREATE TABLE IF NOT EXISTS deals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    value DECIMAL(10,2) DEFAULT 0.0,
    currency VARCHAR(3) DEFAULT 'USD',
    stage VARCHAR(50) DEFAULT 'new_lead',
    probability INTEGER DEFAULT 10,
    source VARCHAR(50) DEFAULT 'whatsapp',
    expected_close_date DATE,
    won_date DATE,
    lost_date DATE,
    lost_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for deals
CREATE INDEX IF NOT EXISTS idx_deals_user_id ON deals(user_id);
CREATE INDEX IF NOT EXISTS idx_deals_stage ON deals(stage);
CREATE INDEX IF NOT EXISTS idx_deals_created_at ON deals(created_at);

-- Create notes table
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    deal_id INTEGER REFERENCES deals(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    note_type VARCHAR(50) DEFAULT 'note',
    created_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for notes
CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);
CREATE INDEX IF NOT EXISTS idx_notes_deal_id ON notes(deal_id);
CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at);

-- Create tags table
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(7) DEFAULT '#6B7280',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create user_tags junction table
CREATE TABLE IF NOT EXISTS user_tags (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, tag_id)
);

-- Create indexes for user_tags
CREATE INDEX IF NOT EXISTS idx_user_tags_user_id ON user_tags(user_id);
CREATE INDEX IF NOT EXISTS idx_user_tags_tag_id ON user_tags(tag_id);

-- Insert default tags
INSERT INTO tags (name, color) VALUES
    ('VIP', '#EF4444'),
    ('Interesado', '#10B981'),
    ('Seguimiento', '#F59E0B'),
    ('Frío', '#6B7280'),
    ('Caliente', '#F97316')
ON CONFLICT (name) DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for deals table
DROP TRIGGER IF EXISTS update_deals_updated_at ON deals;
CREATE TRIGGER update_deals_updated_at
    BEFORE UPDATE ON deals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Verification Queries
-- ============================================================================
-- Run these to verify the migration was successful:

-- Check tables were created
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' AND table_name IN ('deals', 'notes', 'tags', 'user_tags');

-- Check indexes were created
-- SELECT indexname FROM pg_indexes 
-- WHERE tablename IN ('deals', 'notes', 'tags', 'user_tags');

-- Check default tags were inserted
-- SELECT * FROM tags;

-- ============================================================================
-- Rollback Script (if needed)
-- ============================================================================
-- DROP TABLE IF EXISTS user_tags CASCADE;
-- DROP TABLE IF EXISTS notes CASCADE;
-- DROP TABLE IF EXISTS deals CASCADE;
-- DROP TABLE IF EXISTS tags CASCADE;
-- DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;
