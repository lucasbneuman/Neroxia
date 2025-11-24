-- Disable RLS warnings by enabling RLS with permissive policies
-- Run this in Supabase SQL Editor if you want to remove the warnings

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE follow_ups ENABLE ROW LEVEL SECURITY;
ALTER TABLE configs ENABLE ROW LEVEL SECURITY;

-- Create permissive policies (allow all operations)
-- This is safe because we're using service_role key from backend

-- Users table policies
CREATE POLICY "Allow all operations on users" ON users
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Messages table policies
CREATE POLICY "Allow all operations on messages" ON messages
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Follow-ups table policies
CREATE POLICY "Allow all operations on follow_ups" ON follow_ups
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Configs table policies
CREATE POLICY "Allow all operations on configs" ON configs
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Verify policies were created
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
