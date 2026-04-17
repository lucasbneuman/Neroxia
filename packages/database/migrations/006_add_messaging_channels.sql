-- ================================================
-- Migration 006: Multi-Channel Messaging Support
-- Date: 2025-12-04
-- Purpose: Add Instagram and Facebook Messenger support
-- ================================================

-- Add channel support to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS channel VARCHAR(20) DEFAULT 'whatsapp' NOT NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS channel_user_id VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS channel_username VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS channel_profile_pic_url TEXT;

-- Modify phone to be nullable (Instagram/Messenger users may not have phone initially)
-- SQLite doesn't support ALTER COLUMN directly, so we need to check if this is needed
-- For PostgreSQL:
-- ALTER TABLE users ALTER COLUMN phone DROP NOT NULL;

-- Add composite unique constraint for channel + channel_user_id
-- Note: SQLite doesn't support WHERE clause in unique constraints, so we use a regular unique index
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_channel_user_id
ON users(channel, channel_user_id);

-- Keep existing phone unique constraint (already allows NULL)
-- ALTER TABLE users ADD CONSTRAINT users_phone_key UNIQUE (phone);

-- Add index for efficient channel filtering
CREATE INDEX IF NOT EXISTS idx_users_channel ON users(channel);

-- Update deals table source to accommodate new channels
-- SQLite doesn't support ALTER COLUMN TYPE, this is for PostgreSQL
-- ALTER TABLE deals ALTER COLUMN source TYPE VARCHAR(50);

-- Add channel metadata to messages table
ALTER TABLE messages ADD COLUMN IF NOT EXISTS channel VARCHAR(20) DEFAULT 'whatsapp' NOT NULL;
ALTER TABLE messages ADD COLUMN IF NOT EXISTS channel_message_id VARCHAR(100);

-- Create index for message channel filtering
CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel);

-- ================================================
-- New Table: Channel Integrations (Multi-tenant)
-- ================================================

CREATE TABLE IF NOT EXISTS channel_integrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    auth_user_id TEXT NOT NULL,
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('instagram', 'messenger')),
    page_id VARCHAR(50),
    page_access_token TEXT NOT NULL,
    page_name VARCHAR(200),
    instagram_account_id VARCHAR(50),
    is_active BOOLEAN DEFAULT 1,
    webhook_verify_token VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- One integration per tenant per channel per page
    UNIQUE(auth_user_id, channel, page_id)
);

CREATE INDEX IF NOT EXISTS idx_channel_integrations_user ON channel_integrations(auth_user_id);
CREATE INDEX IF NOT EXISTS idx_channel_integrations_channel ON channel_integrations(channel);
CREATE INDEX IF NOT EXISTS idx_channel_integrations_active ON channel_integrations(is_active) WHERE is_active = 1;

-- ================================================
-- Backfill existing data
-- ================================================

-- Ensure all existing users have channel set to 'whatsapp'
UPDATE users SET channel = 'whatsapp' WHERE channel IS NULL OR channel = '';

-- Ensure all existing messages have channel set to 'whatsapp'
UPDATE messages SET channel = 'whatsapp' WHERE channel IS NULL OR channel = '';

-- ================================================
-- Verification Queries (commented out - run manually if needed)
-- ================================================

-- Verify indexes
-- SELECT * FROM sqlite_master WHERE type='index' AND (tbl_name IN ('users', 'messages', 'channel_integrations'));

-- Verify table structure
-- PRAGMA table_info(users);
-- PRAGMA table_info(messages);
-- PRAGMA table_info(channel_integrations);

-- Verify data backfill
-- SELECT COUNT(*) as whatsapp_users FROM users WHERE channel = 'whatsapp';
-- SELECT COUNT(*) as whatsapp_messages FROM messages WHERE channel = 'whatsapp';
