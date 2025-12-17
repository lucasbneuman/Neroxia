-- ============================================================================
-- CONSOLIDATED SUPABASE MIGRATION SCRIPT
-- Date: 2025-12-17
-- Purpose: Apply all pending migrations (002-006) to Supabase production
-- Status: IDEMPOTENT - Safe to run multiple times
-- ============================================================================

-- ============================================================================
-- MIGRATION 002: CRM Tables (deals, notes, tags, user_tags)
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

-- Create function to update updated_at timestamp (if not exists)
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
-- MIGRATION 003: Add manual qualification flag to deals
-- ============================================================================

-- Add manually_qualified column (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'deals' AND column_name = 'manually_qualified'
    ) THEN
        ALTER TABLE deals ADD COLUMN manually_qualified BOOLEAN DEFAULT FALSE NOT NULL;
    END IF;
END $$;

-- Add index for filtering
CREATE INDEX IF NOT EXISTS idx_deals_manually_qualified ON deals(manually_qualified);

-- Add comment for documentation
COMMENT ON COLUMN deals.manually_qualified IS
'True if deal stage was manually edited from CRM, preventing bot auto-updates';

-- Update existing deals to be marked as not manually qualified
UPDATE deals SET manually_qualified = FALSE WHERE manually_qualified IS NULL;

-- ============================================================================
-- MIGRATION 004: Subscription Tables + auth_user_id in users
-- ============================================================================

-- 1. Update users table to link with Supabase Auth
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'auth_user_id'
    ) THEN
        ALTER TABLE users ADD COLUMN auth_user_id UUID;
    END IF;
END $$;
CREATE INDEX IF NOT EXISTS idx_users_auth_user_id ON users(auth_user_id);

-- 2. Create subscription_plans table
CREATE TABLE IF NOT EXISTS subscription_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    billing_period VARCHAR(20) DEFAULT 'monthly',
    features JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. Create user_subscriptions table
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE,
    plan_id INTEGER NOT NULL REFERENCES subscription_plans(id),
    status VARCHAR(20) DEFAULT 'trial',
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    trial_ends_at TIMESTAMP,
    trial_days INTEGER DEFAULT 14,
    canceled_at TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    stripe_customer_id VARCHAR(100),
    stripe_subscription_id VARCHAR(100),
    stripe_price_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_plan_id ON user_subscriptions(plan_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status ON user_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_stripe_customer_id ON user_subscriptions(stripe_customer_id);

-- 4. Create usage_tracking table
CREATE TABLE IF NOT EXISTS usage_tracking (
    id SERIAL PRIMARY KEY,
    subscription_id INTEGER NOT NULL REFERENCES user_subscriptions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    messages_sent INTEGER DEFAULT 0,
    bots_created INTEGER DEFAULT 0,
    rag_documents INTEGER DEFAULT 0,
    rag_storage_mb DECIMAL(10,2) DEFAULT 0.0,
    api_calls INTEGER DEFAULT 0,
    last_reset_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_usage_tracking_subscription_id ON usage_tracking(subscription_id);
CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id ON usage_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_tracking_period ON usage_tracking(period_start, period_end);

-- 5. Create billing_history table
CREATE TABLE IF NOT EXISTS billing_history (
    id SERIAL PRIMARY KEY,
    subscription_id INTEGER NOT NULL REFERENCES user_subscriptions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) NOT NULL,
    description TEXT,
    stripe_invoice_id VARCHAR(100),
    stripe_charge_id VARCHAR(100),
    invoice_url VARCHAR(500),
    invoice_pdf VARCHAR(500),
    billing_date TIMESTAMP NOT NULL,
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_billing_history_subscription_id ON billing_history(subscription_id);
CREATE INDEX IF NOT EXISTS idx_billing_history_user_id ON billing_history(user_id);
CREATE INDEX IF NOT EXISTS idx_billing_history_stripe_invoice_id ON billing_history(stripe_invoice_id);

-- 6. Create user_profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    auth_user_id UUID NOT NULL UNIQUE,
    company_name VARCHAR(200),
    phone VARCHAR(20),
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'es',
    avatar_url VARCHAR(500),
    role VARCHAR(20) DEFAULT 'owner',
    onboarding_completed BOOLEAN DEFAULT FALSE,
    onboarding_step INTEGER DEFAULT 0,
    preferences JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_profiles_auth_user_id ON user_profiles(auth_user_id);

-- 7. Add triggers for updated_at
DROP TRIGGER IF EXISTS update_subscription_plans_updated_at ON subscription_plans;
CREATE TRIGGER update_subscription_plans_updated_at
    BEFORE UPDATE ON subscription_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_subscriptions_updated_at ON user_subscriptions;
CREATE TRIGGER update_user_subscriptions_updated_at
    BEFORE UPDATE ON user_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_usage_tracking_updated_at ON usage_tracking;
CREATE TRIGGER update_usage_tracking_updated_at
    BEFORE UPDATE ON usage_tracking
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- MIGRATION 006: Multi-Channel Support (Instagram/Messenger)
-- ============================================================================

-- Add channel columns to users table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'channel') THEN
        ALTER TABLE users ADD COLUMN channel VARCHAR(20) DEFAULT 'whatsapp' NOT NULL;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'channel_user_id') THEN
        ALTER TABLE users ADD COLUMN channel_user_id VARCHAR(100);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'channel_username') THEN
        ALTER TABLE users ADD COLUMN channel_username VARCHAR(100);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'channel_profile_pic_url') THEN
        ALTER TABLE users ADD COLUMN channel_profile_pic_url TEXT;
    END IF;
END $$;

-- Make phone nullable for Instagram/Messenger users
ALTER TABLE users ALTER COLUMN phone DROP NOT NULL;

-- Create composite unique index for channel + channel_user_id
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_channel_user_id
ON users(channel, channel_user_id)
WHERE channel_user_id IS NOT NULL;

-- Create index for channel filtering
CREATE INDEX IF NOT EXISTS idx_users_channel ON users(channel);

-- Add channel metadata to messages table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'messages' AND column_name = 'channel') THEN
        ALTER TABLE messages ADD COLUMN channel VARCHAR(20) DEFAULT 'whatsapp' NOT NULL;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'messages' AND column_name = 'channel_message_id') THEN
        ALTER TABLE messages ADD COLUMN channel_message_id VARCHAR(100);
    END IF;
END $$;

-- Create index for message channel filtering
CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel);

-- Create channel_integrations table
CREATE TABLE IF NOT EXISTS channel_integrations (
    id SERIAL PRIMARY KEY,
    auth_user_id UUID NOT NULL,
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('instagram', 'messenger')),
    page_id VARCHAR(50),
    page_access_token TEXT NOT NULL,
    page_name VARCHAR(200),
    instagram_account_id VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    webhook_verify_token VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_user_channel_page UNIQUE (auth_user_id, channel, page_id)
);

CREATE INDEX IF NOT EXISTS idx_channel_integrations_user ON channel_integrations(auth_user_id);
CREATE INDEX IF NOT EXISTS idx_channel_integrations_channel ON channel_integrations(channel);
CREATE INDEX IF NOT EXISTS idx_channel_integrations_active ON channel_integrations(is_active) WHERE is_active = TRUE;

-- Backfill existing data
UPDATE users SET channel = 'whatsapp' WHERE channel IS NULL OR channel = '';
UPDATE messages SET channel = 'whatsapp' WHERE channel IS NULL OR channel = '';

-- ============================================================================
-- ADDITIONAL COLUMNS (Twilio + HubSpot integration fields)
-- ============================================================================

-- Add HubSpot integration columns to users
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'hubspot_contact_id') THEN
        ALTER TABLE users ADD COLUMN hubspot_contact_id VARCHAR(50);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'hubspot_lifecyclestage') THEN
        ALTER TABLE users ADD COLUMN hubspot_lifecyclestage VARCHAR(50);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'hubspot_synced_at') THEN
        ALTER TABLE users ADD COLUMN hubspot_synced_at TIMESTAMP;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_users_hubspot_contact_id ON users(hubspot_contact_id);

-- Add Twilio webhook auto-populated fields to users
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'whatsapp_profile_name') THEN
        ALTER TABLE users ADD COLUMN whatsapp_profile_name VARCHAR(100);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'country_code') THEN
        ALTER TABLE users ADD COLUMN country_code VARCHAR(5);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'phone_formatted') THEN
        ALTER TABLE users ADD COLUMN phone_formatted VARCHAR(20);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'first_contact_timestamp') THEN
        ALTER TABLE users ADD COLUMN first_contact_timestamp TIMESTAMP;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'media_count') THEN
        ALTER TABLE users ADD COLUMN media_count INTEGER DEFAULT 0;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'location_shared') THEN
        ALTER TABLE users ADD COLUMN location_shared BOOLEAN DEFAULT FALSE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'last_twilio_message_sid') THEN
        ALTER TABLE users ADD COLUMN last_twilio_message_sid VARCHAR(50);
    END IF;
END $$;

-- ============================================================================
-- VERIFICATION SUMMARY
-- ============================================================================
-- After running this script, execute verify_supabase_schema.sql to confirm
-- all tables, columns, and indexes were created successfully.
-- ============================================================================
