-- ============================================================================
-- WhatsApp Sales Bot - Database Schema for Supabase
-- ============================================================================
-- Run this script in Supabase SQL Editor to create all required tables
-- Dashboard > SQL Editor > New Query > Paste this script > Run
-- ============================================================================

-- Drop existing tables if they exist (careful in production!)
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS follow_ups CASCADE;
DROP TABLE IF EXISTS configs CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Conversation tracking
    intent_score FLOAT DEFAULT 0.0,
    sentiment VARCHAR(20) DEFAULT 'neutral',
    stage VARCHAR(50) DEFAULT 'welcome',
    conversation_mode VARCHAR(20) DEFAULT 'AUTO',
    conversation_summary TEXT,
    
    -- HubSpot Integration
    hubspot_contact_id VARCHAR(50),
    hubspot_lifecyclestage VARCHAR(50),
    hubspot_synced_at TIMESTAMP,
    
    -- Activity tracking
    total_messages INTEGER DEFAULT 0,
    last_message_at TIMESTAMP
);

-- Create indexes for users table
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_hubspot_contact_id ON users(hubspot_contact_id);

-- ============================================================================
-- MESSAGES TABLE
-- ============================================================================
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    sender VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    message_metadata JSONB
);

-- Create indexes for messages table
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);

-- ============================================================================
-- FOLLOW_UPS TABLE
-- ============================================================================
CREATE TABLE follow_ups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scheduled_time TIMESTAMP NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    follow_up_count INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    job_id VARCHAR(100)
);

-- Create indexes for follow_ups table
CREATE INDEX idx_follow_ups_user_id ON follow_ups(user_id);
CREATE INDEX idx_follow_ups_scheduled_time ON follow_ups(scheduled_time);

-- ============================================================================
-- CONFIGS TABLE
-- ============================================================================
CREATE TABLE configs (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create index for configs table
CREATE INDEX idx_configs_key ON configs(key);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for configs table
CREATE TRIGGER update_configs_updated_at
    BEFORE UPDATE ON configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INSERT DEFAULT CONFIGURATIONS
-- ============================================================================

INSERT INTO configs (key, value) VALUES
    ('system_prompt', '"You are a friendly and professional sales assistant. Your goal is to help customers find the right product and complete their purchase smoothly."'),
    ('welcome_message', '"Hello! 👋 How can I help you today?"'),
    ('payment_link', '"https://example.com/pay"'),
    ('response_delay_minutes', '0.5'),
    ('text_audio_ratio', '0'),
    ('use_emojis', 'true'),
    ('tts_voice', '"nova"'),
    ('multi_part_messages', 'false'),
    ('max_words_per_response', '100'),
    ('product_name', '""'),
    ('product_description', '""'),
    ('product_features', '""'),
    ('product_benefits', '""'),
    ('product_price', '""'),
    ('product_target_audience', '""'),
    ('welcome_prompt', '""'),
    ('intent_prompt', '""'),
    ('sentiment_prompt', '""'),
    ('data_extraction_prompt', '""'),
    ('closing_prompt', '""')
ON CONFLICT (key) DO NOTHING;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check that all tables were created
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN ('users', 'messages', 'follow_ups', 'configs')
ORDER BY tablename;

-- Check row counts
SELECT 
    'users' as table_name, COUNT(*) as row_count FROM users
UNION ALL
SELECT 'messages', COUNT(*) FROM messages
UNION ALL
SELECT 'follow_ups', COUNT(*) FROM follow_ups
UNION ALL
SELECT 'configs', COUNT(*) FROM configs;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT '✅ Database schema created successfully!' as status,
       'All tables, indexes, and triggers are in place.' as message,
       NOW() as created_at;
