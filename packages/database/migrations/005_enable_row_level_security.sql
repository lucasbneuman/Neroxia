-- Migration 005: Enable Row Level Security (RLS)
-- Multi-tenant data isolation for SaaS platform

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE deals ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE follow_ups ENABLE ROW LEVEL SECURITY;
ALTER TABLE configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscription_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- USERS table (auth_user_id UUID links to auth.users)
DROP POLICY IF EXISTS "Users can view own record" ON users;
CREATE POLICY "Users can view own record" ON users FOR SELECT USING (auth_user_id = auth.uid());

DROP POLICY IF EXISTS "Users can update own record" ON users;
CREATE POLICY "Users can update own record" ON users FOR UPDATE USING (auth_user_id = auth.uid());

DROP POLICY IF EXISTS "Service role full access to users" ON users;
CREATE POLICY "Service role full access to users" ON users FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- MESSAGES table (user_id INTEGER FK to users.id)
DROP POLICY IF EXISTS "Users can view own messages" ON messages;
CREATE POLICY "Users can view own messages" ON messages FOR SELECT USING (
  user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid())
);

DROP POLICY IF EXISTS "Users can insert own messages" ON messages;
CREATE POLICY "Users can insert own messages" ON messages FOR INSERT WITH CHECK (
  user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid())
);

DROP POLICY IF EXISTS "Service role full access to messages" ON messages;
CREATE POLICY "Service role full access to messages" ON messages FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- DEALS table (user_id INTEGER FK to users.id)
DROP POLICY IF EXISTS "Users can view own deals" ON deals;
CREATE POLICY "Users can view own deals" ON deals FOR SELECT USING (
  user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid())
);

DROP POLICY IF EXISTS "Users can update own deals" ON deals;
CREATE POLICY "Users can update own deals" ON deals FOR UPDATE USING (
  user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid())
);

DROP POLICY IF EXISTS "Service role full access to deals" ON deals;
CREATE POLICY "Service role full access to deals" ON deals FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- NOTES table (user_id INTEGER FK to users.id)
DROP POLICY IF EXISTS "Users can view own notes" ON notes;
CREATE POLICY "Users can view own notes" ON notes FOR SELECT USING (
  user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid())
  OR deal_id IN (SELECT id FROM deals WHERE user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()))
);

DROP POLICY IF EXISTS "Users can create own notes" ON notes;
CREATE POLICY "Users can create own notes" ON notes FOR INSERT WITH CHECK (
  user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid())
  OR deal_id IN (SELECT id FROM deals WHERE user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()))
);

DROP POLICY IF EXISTS "Service role full access to notes" ON notes;
CREATE POLICY "Service role full access to notes" ON notes FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- TAGS table (shared resource)
DROP POLICY IF EXISTS "Authenticated users can view tags" ON tags;
CREATE POLICY "Authenticated users can view tags" ON tags FOR SELECT USING (auth.role() = 'authenticated');

DROP POLICY IF EXISTS "Service role full access to tags" ON tags;
CREATE POLICY "Service role full access to tags" ON tags FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- USER_TAGS table (user_id INTEGER FK to users.id)
DROP POLICY IF EXISTS "Users can view own tag assignments" ON user_tags;
CREATE POLICY "Users can view own tag assignments" ON user_tags FOR SELECT USING (
  user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid())
);

DROP POLICY IF EXISTS "Service role full access to user_tags" ON user_tags;
CREATE POLICY "Service role full access to user_tags" ON user_tags FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- FOLLOW_UPS table (user_id INTEGER FK to users.id)
DROP POLICY IF EXISTS "Users can view own follow_ups" ON follow_ups;
CREATE POLICY "Users can view own follow_ups" ON follow_ups FOR SELECT USING (
  user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid())
);

DROP POLICY IF EXISTS "Service role full access to follow_ups" ON follow_ups;
CREATE POLICY "Service role full access to follow_ups" ON follow_ups FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- CONFIGS table (user_id UUID FK to auth.users.id)
DROP POLICY IF EXISTS "Users can view own configs" ON configs;
CREATE POLICY "Users can view own configs" ON configs FOR SELECT USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can update own configs" ON configs;
CREATE POLICY "Users can update own configs" ON configs FOR UPDATE USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can insert own configs" ON configs;
CREATE POLICY "Users can insert own configs" ON configs FOR INSERT WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can delete own configs" ON configs;
CREATE POLICY "Users can delete own configs" ON configs FOR DELETE USING (user_id = auth.uid());

-- SUBSCRIPTION_PLANS table (shared resource)
DROP POLICY IF EXISTS "Authenticated users can view subscription plans" ON subscription_plans;
CREATE POLICY "Authenticated users can view subscription plans" ON subscription_plans FOR SELECT USING (
  is_active = true AND auth.role() = 'authenticated'
);

DROP POLICY IF EXISTS "Service role full access to subscription_plans" ON subscription_plans;
CREATE POLICY "Service role full access to subscription_plans" ON subscription_plans FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- USER_SUBSCRIPTIONS table (user_id UUID FK to auth.users.id)
DROP POLICY IF EXISTS "Users can view own subscriptions" ON user_subscriptions;
CREATE POLICY "Users can view own subscriptions" ON user_subscriptions FOR SELECT USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Service role full access to user_subscriptions" ON user_subscriptions;
CREATE POLICY "Service role full access to user_subscriptions" ON user_subscriptions FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- USAGE_TRACKING table (user_id UUID)
DROP POLICY IF EXISTS "Users can view own usage tracking" ON usage_tracking;
CREATE POLICY "Users can view own usage tracking" ON usage_tracking FOR SELECT USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Service role full access to usage_tracking" ON usage_tracking;
CREATE POLICY "Service role full access to usage_tracking" ON usage_tracking FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- BILLING_HISTORY table (user_id UUID)
DROP POLICY IF EXISTS "Users can view own billing history" ON billing_history;
CREATE POLICY "Users can view own billing history" ON billing_history FOR SELECT USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Service role full access to billing_history" ON billing_history;
CREATE POLICY "Service role full access to billing_history" ON billing_history FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- USER_PROFILES table (auth_user_id UUID FK to auth.users.id)
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth_user_id = auth.uid());

DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth_user_id = auth.uid());

DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;
CREATE POLICY "Users can insert own profile" ON user_profiles FOR INSERT WITH CHECK (auth_user_id = auth.uid());

DROP POLICY IF EXISTS "Service role full access to user_profiles" ON user_profiles;
CREATE POLICY "Service role full access to user_profiles" ON user_profiles FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO service_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO service_role;
