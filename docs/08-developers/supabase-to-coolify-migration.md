# Supabase to Coolify Migration Guide

**Status:** Future Plan - Documentation for when Coolify production is ready
**Date Created:** 2025-12-17
**Last Updated:** 2025-12-17

---

## Overview

This document outlines the strategy for migrating from Supabase PostgreSQL to self-hosted PostgreSQL on Coolify when production infrastructure is ready.

## Current State (As of 2025-12-17)

### Database Configuration

**Supabase Production:**
- Host: `aws-0-us-west-2.pooler.supabase.com`
- Port: `5432`
- Database: `postgres`
- User: `postgres.oveixhmndwrtymuymdxm`
- Connection String: `postgresql+asyncpg://postgres.oveixhmndwrtymuymdxm:5vNAztJpXzbt3@aws-0-us-west-2.pooler.supabase.com:5432/postgres`

**Schema Status:**
- ✅ All migrations applied (002-006)
- ✅ 14 tables total
- ✅ 63 columns in users table
- ✅ All critical columns exist: `channel`, `channel_user_id`, `auth_user_id`, `hubspot_contact_id`, etc.
- ✅ All indexes created

**Authentication:**
- Using: Supabase Auth
- Users table linked via `auth_user_id` (UUID from Supabase `auth.users`)
- Multi-tenant support enabled

---

## Migration Strategy

### Phase 1: Pre-Migration Preparation

#### 1.1 Coolify Infrastructure Setup
- [ ] Deploy PostgreSQL 15+ container in Coolify
- [ ] Configure persistent storage volumes
- [ ] Setup automated backups (daily snapshots)
- [ ] Configure firewall rules (allow only application IPs)
- [ ] Setup monitoring (disk space, connection count, query performance)

#### 1.2 Database User Setup
```sql
-- Create application user with limited privileges
CREATE USER salesbot_app WITH PASSWORD 'secure_random_password_here';

-- Create database
CREATE DATABASE sales_bot_production OWNER salesbot_app;

-- Grant privileges
GRANT CONNECT ON DATABASE sales_bot_production TO salesbot_app;
GRANT USAGE ON SCHEMA public TO salesbot_app;
GRANT CREATE ON SCHEMA public TO salesbot_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO salesbot_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO salesbot_app;

-- Enable extensions
\c sales_bot_production
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
```

#### 1.3 Backup Current Supabase Data
```bash
# Export full database dump from Supabase
pg_dump "postgresql://postgres.oveixhmndwrtymuymdxm:5vNAztJpXzbt3@aws-0-us-west-2.pooler.supabase.com:5432/postgres" \
  --format=custom \
  --file=supabase_backup_$(date +%Y%m%d_%H%M%S).dump \
  --verbose

# Export schema only (for verification)
pg_dump "postgresql://..." \
  --schema-only \
  --file=supabase_schema_$(date +%Y%m%d_%H%M%S).sql

# Export data only (CSV for specific tables if needed)
psql "postgresql://..." -c "\COPY users TO 'users_backup.csv' CSV HEADER"
psql "postgresql://..." -c "\COPY messages TO 'messages_backup.csv' CSV HEADER"
```

### Phase 2: Schema Migration

#### 2.1 Apply Schema to Coolify PostgreSQL
```bash
# Option 1: Use consolidated migration script (recommended)
psql "postgresql://salesbot_app:PASSWORD@coolify-postgres-host:5432/sales_bot_production" \
  -f <one-time migration SQL script>

# Option 2: Restore from dump (includes data)
pg_restore --dbname="postgresql://salesbot_app:PASSWORD@coolify-postgres-host:5432/sales_bot_production" \
  --verbose \
  supabase_backup.dump
```

#### 2.2 Verify Schema Migration
```bash
# Run verification script
psql "postgresql://salesbot_app:PASSWORD@coolify-postgres-host:5432/sales_bot_production" \
  -f <one-time verification SQL script>
```

### Phase 3: Data Migration

#### 3.1 Zero-Downtime Migration Approach

**Option A: Blue-Green Deployment (Recommended)**
1. Setup new Coolify environment (green)
2. Migrate all data to Coolify PostgreSQL
3. Run application in dual-write mode (writes to both databases)
4. Verify data consistency
5. Switch DNS/load balancer to Coolify (green becomes production)
6. Monitor for 24 hours
7. Decommission Supabase (blue)

**Option B: Maintenance Window**
1. Schedule 2-hour maintenance window
2. Set application to read-only mode
3. Export final data from Supabase
4. Import to Coolify PostgreSQL
5. Update environment variables
6. Restart application
7. Verify all endpoints work
8. Re-enable write access

#### 3.2 Data Export Commands
```bash
# Export all tables with data
tables=("users" "messages" "deals" "notes" "tags" "user_tags" "subscription_plans"
        "user_subscriptions" "usage_tracking" "billing_history" "user_profiles"
        "channel_integrations" "configs" "follow_ups")

for table in "${tables[@]}"; do
  psql "postgresql://..." -c "\COPY $table TO '${table}_data.csv' CSV HEADER"
done
```

#### 3.3 Data Import Commands
```bash
# Import data to Coolify PostgreSQL
for table in "${tables[@]}"; do
  psql "postgresql://salesbot_app:PASSWORD@coolify-host:5432/sales_bot_production" \
    -c "\COPY $table FROM '${table}_data.csv' CSV HEADER"
done

# Reset sequences after import
psql "postgresql://..." -c "SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE(MAX(id), 1)) FROM users;"
psql "postgresql://..." -c "SELECT setval(pg_get_serial_sequence('messages', 'id'), COALESCE(MAX(id), 1)) FROM messages;"
# ... repeat for all tables with SERIAL primary keys
```

### Phase 4: Authentication Migration

#### 4.1 Supabase Auth Options

**Option 1: Keep Supabase Auth (Easiest)**
- Continue using Supabase for authentication only
- Keep `auth_user_id` linking to Supabase `auth.users`
- Only migrate application database, not auth
- Minimal code changes required

**Option 2: Migrate to Self-Hosted Auth (Complex)**
- Export users from Supabase Auth
- Setup alternative auth solution (Auth0, Keycloak, custom)
- Migrate user credentials and sessions
- Update frontend authentication flow
- **Not recommended** unless Supabase costs are prohibitive

**Recommendation:** Keep Supabase Auth (Option 1)
- Supabase Auth is reliable and free for reasonable usage
- Authentication is separate concern from application data
- Reduces migration complexity and risk

#### 4.2 Environment Variables Update
```bash
# Current (Supabase)
DATABASE_URL=postgresql+asyncpg://postgres.oveixhmndwrtymuymdxm:5vNAztJpXzbt3@aws-0-us-west-2.pooler.supabase.com:5432/postgres
SUPABASE_URL=https://oveixhmndwrtymuymdxm.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_KEY=eyJhbGci...

# After Migration (Coolify + Supabase Auth)
DATABASE_URL=postgresql+asyncpg://salesbot_app:PASSWORD@coolify-postgres-host:5432/sales_bot_production
SUPABASE_URL=https://oveixhmndwrtymuymdxm.supabase.co  # Keep for auth
SUPABASE_ANON_KEY=eyJhbGci...  # Keep for auth
SUPABASE_SERVICE_KEY=eyJhbGci...  # Keep for auth
```

### Phase 5: Application Configuration

#### 5.1 Update Database Connection
```python
# apps/api/src/database.py
# No code changes needed - DATABASE_URL env var handles connection

# Verify async driver is asyncpg (for PostgreSQL)
# Already configured correctly in current setup
```

#### 5.2 Connection Pool Tuning
```python
# apps/api/src/database.py
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,  # Adjust based on Coolify resources
    max_overflow=40,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections every hour
)
```

#### 5.3 Health Check Updates
```python
# apps/api/src/main.py
@app.get("/health/db")
async def health_check_db():
    """Database health check endpoint."""
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "coolify-postgresql"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### Phase 6: Testing & Validation

#### 6.1 Pre-Migration Testing
- [ ] Test migration script in staging environment
- [ ] Verify all API endpoints work with Coolify database
- [ ] Run full integration test suite
- [ ] Load test with production-like traffic
- [ ] Verify bot engine works correctly
- [ ] Test all CRUD operations
- [ ] Verify foreign key constraints
- [ ] Test backup/restore procedures

#### 6.2 Post-Migration Validation
```bash
# Run comprehensive verification
psql "postgresql://..." -f <one-time verification SQL script>

# Check row counts match
psql "postgresql://..." -c "SELECT 'users' AS table, COUNT(*) FROM users UNION ALL SELECT 'messages', COUNT(*) FROM messages;"

# Verify data integrity
psql "postgresql://..." -c "SELECT COUNT(*) AS orphaned_messages FROM messages m LEFT JOIN users u ON m.user_id = u.id WHERE u.id IS NULL;"

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/health/db
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/users/profile
```

#### 6.3 Monitoring Setup
- [ ] Setup Prometheus metrics for PostgreSQL
- [ ] Configure Grafana dashboards
- [ ] Setup alerting for:
  - Connection pool exhaustion
  - Slow queries (>1s)
  - Disk space <20%
  - Database downtime
  - Replication lag (if using replicas)

### Phase 7: Rollback Plan

#### 7.1 Rollback Procedure
If migration fails or issues detected within 24 hours:

```bash
# 1. Revert environment variables to Supabase
DATABASE_URL=postgresql+asyncpg://postgres.oveixhmndwrtymuymdxm:5vNAztJpXzbt3@aws-0-us-west-2.pooler.supabase.com:5432/postgres

# 2. Restart application
systemctl restart whatsapp-sales-bot-api

# 3. Verify health
curl http://localhost:8000/health/db

# 4. If data loss occurred, restore from Supabase backup
pg_restore --dbname="postgresql://..." supabase_backup.dump
```

#### 7.2 Rollback Criteria
- API error rate >5%
- Database query latency >2x baseline
- Data inconsistencies detected
- Authentication failures
- Critical bug discovered in production

---

## Performance Optimization

### Post-Migration Tuning

#### 1. Analyze and Vacuum
```sql
-- After data import
ANALYZE;
VACUUM ANALYZE;

-- Setup automatic vacuum
ALTER TABLE users SET (autovacuum_vacuum_scale_factor = 0.1);
ALTER TABLE messages SET (autovacuum_vacuum_scale_factor = 0.05);
```

#### 2. Index Optimization
```sql
-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- Create missing indexes based on query patterns
CREATE INDEX CONCURRENTLY idx_messages_user_timestamp ON messages(user_id, timestamp DESC);
CREATE INDEX CONCURRENTLY idx_deals_stage_updated ON deals(stage, updated_at DESC);
```

#### 3. Query Performance Monitoring
```sql
-- Enable pg_stat_statements
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slow queries
SELECT query, calls, total_exec_time, mean_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 1000  -- queries slower than 1 second
ORDER BY total_exec_time DESC
LIMIT 20;
```

---

## Cost Comparison

### Supabase (Current)
- **Free Tier Limits:**
  - 500 MB database size
  - 2 GB bandwidth
  - 50,000 monthly active users
  - 500,000 Edge Function invocations

- **Pro Tier ($25/mo):**
  - 8 GB database size
  - 50 GB bandwidth
  - 100,000 monthly active users
  - Daily backups

### Coolify Self-Hosted (Estimated)
- **Infrastructure:** $10-20/mo (VPS for PostgreSQL)
- **Backup Storage:** $5/mo (object storage)
- **Monitoring:** Free (self-hosted Prometheus/Grafana)
- **Total:** $15-25/mo

**Cost Benefit:** Minimal savings, but full control and data sovereignty

---

## Security Considerations

### 1. Network Security
```bash
# Coolify PostgreSQL firewall rules (iptables)
# Only allow API server IP
iptables -A INPUT -p tcp --dport 5432 -s API_SERVER_IP -j ACCEPT
iptables -A INPUT -p tcp --dport 5432 -j DROP

# Or use PostgreSQL pg_hba.conf
# host    sales_bot_production    salesbot_app    API_SERVER_IP/32    scram-sha-256
```

### 2. Connection Security
```bash
# Enforce SSL connections
# In postgresql.conf:
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'

# Update connection string:
DATABASE_URL=postgresql+asyncpg://salesbot_app:PASSWORD@coolify-host:5432/sales_bot_production?ssl=require
```

### 3. Backup Encryption
```bash
# Encrypt backups before storage
pg_dump "postgresql://..." | gpg --encrypt --recipient admin@company.com > backup_encrypted.gpg

# Decrypt when needed
gpg --decrypt backup_encrypted.gpg | pg_restore --dbname="postgresql://..."
```

---

## Timeline Estimate

### Conservative Estimate (Full Migration)
- **Week 1:** Infrastructure setup, testing in staging
- **Week 2:** Data migration dry runs, performance tuning
- **Week 3:** Production migration, monitoring, validation
- **Week 4:** Optimization, documentation, team training

### Aggressive Estimate (Auth-only kept in Supabase)
- **Day 1:** Coolify PostgreSQL setup, schema migration
- **Day 2:** Data migration, testing
- **Day 3:** Production cutover, monitoring
- **Day 4-7:** Optimization, validation

---

## References

- **Migration Script:** create an explicit one-time SQL script for the cutover window
- **Verification Script:** create an explicit one-time verification SQL script for the cutover window
- **Backup Location:** keep external backups outside the active repository
- **Database Models:** `packages/database/whatsapp_bot_database/models.py`
- **Coolify Deployment:** `deployment-coolify.md`

---

## Decision Log

### 2025-12-17: Initial Documentation
- ✅ Decided to keep Supabase Auth (simpler, reliable)
- ✅ Only migrate application database
- ✅ Use consolidated migration script for consistency
- ✅ Plan for zero-downtime blue-green deployment
- ✅ Maintain compatibility with existing `.env` configuration

---

## Contact & Support

For questions during migration:
1. Review this document thoroughly
2. Test in staging environment first
3. Run verification scripts before and after
4. Monitor database performance closely for first week
5. Keep Supabase backup available for 30 days post-migration

**Last Updated:** 2025-12-17
**Next Review:** When Coolify production environment is ready
