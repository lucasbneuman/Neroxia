-- =====================================================
-- Supabase Database Schema for WhatsApp Sales Bot
-- =====================================================
-- This script creates all necessary tables, indexes, and
-- Row Level Security (RLS) policies for the application.
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- USERS TABLE
-- =====================================================
-- Stores WhatsApp contacts and their conversation state
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Conversation tracking
    intent_score FLOAT DEFAULT 0.0 CHECK (intent_score >= 0 AND intent_score <= 1),
    sentiment VARCHAR(20) DEFAULT 'neutral' CHECK (sentiment IN ('positive', 'neutral', 'negative')),
    stage VARCHAR(50) DEFAULT 'welcome' CHECK (stage IN ('welcome', 'qualifying', 'nurturing', 'closing', 'sold', 'follow_up')),
    conversation_mode VARCHAR(20) DEFAULT 'AUTO' CHECK (conversation_mode IN ('AUTO', 'MANUAL', 'NEEDS_ATTENTION')),
    conversation_summary TEXT,
    
    -- HubSpot Integration
    hubspot_contact_id VARCHAR(50),
    hubspot_lifecyclestage VARCHAR(50),
    hubspot_synced_at TIMESTAMP WITH TIME ZONE,
    
    -- Activity tracking
    total_messages INTEGER DEFAULT 0,
    last_message_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_hubspot_contact_id ON users(hubspot_contact_id);
CREATE INDEX IF NOT EXISTS idx_users_stage ON users(stage);
CREATE INDEX IF NOT EXISTS idx_users_conversation_mode ON users(conversation_mode);

-- =====================================================
-- MESSAGES TABLE
-- =====================================================
-- Stores conversation history
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    sender VARCHAR(10) NOT NULL CHECK (sender IN ('user', 'bot')),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    message_metadata JSONB,
    
    CONSTRAINT fk_messages_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for messages table
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender);

-- =====================================================
-- CONFIGS TABLE
-- =====================================================
-- Stores application configuration as key-value pairs
CREATE TABLE IF NOT EXISTS configs (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create index for configs table
CREATE INDEX IF NOT EXISTS idx_configs_key ON configs(key);

-- =====================================================
-- FOLLOW_UPS TABLE
-- =====================================================
-- Stores scheduled follow-up messages
CREATE TABLE IF NOT EXISTS follow_ups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'cancelled')),
    follow_up_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    job_id VARCHAR(100),
    
    CONSTRAINT fk_followups_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for follow_ups table
CREATE INDEX IF NOT EXISTS idx_followups_user_id ON follow_ups(user_id);
CREATE INDEX IF NOT EXISTS idx_followups_scheduled_time ON follow_ups(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_followups_status ON follow_ups(status);

-- =====================================================
-- TRIGGERS
-- =====================================================
-- Auto-update updated_at timestamp

-- Function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users table
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for configs table
DROP TRIGGER IF EXISTS update_configs_updated_at ON configs;
CREATE TRIGGER update_configs_updated_at
    BEFORE UPDATE ON configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================
-- Enable RLS on all tables

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE follow_ups ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- RLS POLICIES
-- =====================================================
-- These policies allow authenticated users to access data
-- Adjust based on your specific security requirements

-- Users table policies
CREATE POLICY "Allow authenticated users to read users"
    ON users FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to insert users"
    ON users FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated users to update users"
    ON users FOR UPDATE
    TO authenticated
    USING (true);

-- Messages table policies
CREATE POLICY "Allow authenticated users to read messages"
    ON messages FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to insert messages"
    ON messages FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Configs table policies
CREATE POLICY "Allow authenticated users to read configs"
    ON configs FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to insert configs"
    ON configs FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated users to update configs"
    ON configs FOR UPDATE
    TO authenticated
    USING (true);

-- Follow-ups table policies
CREATE POLICY "Allow authenticated users to read follow_ups"
    ON follow_ups FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to insert follow_ups"
    ON follow_ups FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated users to update follow_ups"
    ON follow_ups FOR UPDATE
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to delete follow_ups"
    ON follow_ups FOR DELETE
    TO authenticated
    USING (true);

-- =====================================================
-- INITIAL DATA (Optional)
-- =====================================================
-- Insert default configuration if needed

INSERT INTO configs (key, value) VALUES
    ('bot_name', '"Sales Assistant"'::jsonb),
    ('welcome_message', '"¡Hola! Soy tu asistente de ventas. ¿En qué puedo ayudarte hoy?"'::jsonb),
    ('business_hours', '{"start": "09:00", "end": "18:00", "timezone": "America/Argentina/Buenos_Aires"}'::jsonb)
ON CONFLICT (key) DO NOTHING;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Run these to verify the schema was created correctly

-- Check all tables
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- Check all indexes
-- SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public';

-- Check RLS policies
-- SELECT tablename, policyname FROM pg_policies WHERE schemaname = 'public';
