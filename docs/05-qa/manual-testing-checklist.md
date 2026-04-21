# Manual Testing Checklist - Multi-Channel Integration

**Purpose:** Systematic manual testing guide for Instagram & Messenger integration (Phases 1-8)

**Date Created:** 2025-12-09
**Agent:** QA Lead

---

## Pre-Test Setup

### Environment Configuration
- [ ] `.env` file has all required variables:
  - [ ] `OPENAI_API_KEY` configured
  - [ ] `SUPABASE_DATABASE_URL` accessible
  - [ ] `SUPABASE_URL` configured
  - [ ] `SUPABASE_ANON_KEY` configured
  - [ ] `SUPABASE_SERVICE_KEY` configured
  - [ ] `FACEBOOK_APP_ID` configured
  - [ ] `FACEBOOK_APP_SECRET` configured
  - [ ] `FACEBOOK_VERIFY_TOKEN` configured
  - [ ] `HUBSPOT_ACCESS_TOKEN` configured (optional)
- [ ] Supabase PostgreSQL database accessible
- [ ] Meta App created in Facebook Developers Console
- [ ] Meta App has Instagram and Messenger products enabled
- [ ] Webhook URLs configured in Meta App
- [ ] Test Instagram Business Account connected to Facebook Page
- [ ] Test Facebook Page created

### Service Status
- [ ] API service running on http://localhost:8000
- [ ] Frontend service running on http://localhost:3000 (or 7860)
- [ ] API health check passes: `GET /health`
- [ ] Bot health check passes: `GET /bot/health`

---

## Phase 1-2: Database & CRUD Operations

### Database Schema
- [ ] Migration 006 applied successfully
- [ ] `channel_integrations` table exists with columns:
  - [ ] `id`, `auth_user_id`, `channel`, `page_id`, `page_access_token`
  - [ ] `page_name`, `instagram_account_id`, `connected_at`, `updated_at`
- [ ] `users` table has channel columns:
  - [ ] `channel` (enum: whatsapp, instagram, messenger)
  - [ ] `channel_user_id` (PSID for Instagram/Messenger)
- [ ] Indexes created on:
  - [ ] `users.channel`
  - [ ] `users.channel_user_id`
  - [ ] `channel_integrations.auth_user_id`

### CRUD Operations
- [ ] Can create Instagram user: `create_user(channel="instagram", channel_user_id="PSID")`
- [ ] Can create Messenger user: `create_user(channel="messenger", channel_user_id="PSID")`
- [ ] `get_user_by_identifier()` retrieves Instagram user by PSID
- [ ] `get_user_by_identifier()` retrieves Messenger user by PSID
- [ ] `get_user_by_identifier()` retrieves WhatsApp user by phone
- [ ] `get_channel_config_for_user()` returns correct config for page
- [ ] Can create channel integration: `create_channel_integration()`
- [ ] Can list integrations: `get_channel_integrations_by_user()`

---

## Phase 3: Meta Webhooks

### Instagram Webhook Verification (GET)
- [ ] GET `/webhook/instagram?hub.mode=subscribe&hub.challenge=123&hub.verify_token=TOKEN`
- [ ] Returns challenge value (200 OK)
- [ ] Invalid mode returns 400
- [ ] Invalid token returns 403
- [ ] Missing env var returns 500

### Messenger Webhook Verification (GET)
- [ ] GET `/webhook/messenger?hub.mode=subscribe&hub.challenge=456&hub.verify_token=TOKEN`
- [ ] Returns challenge value (200 OK)
- [ ] Invalid mode returns 400
- [ ] Invalid token returns 403

### Instagram Message Processing (POST)
- [ ] POST `/webhook/instagram` with valid signature accepted
- [ ] Invalid signature rejected (403)
- [ ] Missing signature rejected (403)
- [ ] Signature without `sha256=` prefix rejected (BUG-008 fix)
- [ ] Message text extracted correctly
- [ ] User created with Instagram channel
- [ ] Message stored in database
- [ ] Response returned within 2 seconds

### Messenger Message Processing (POST)
- [ ] POST `/webhook/messenger` with valid signature accepted
- [ ] Invalid signature rejected (403)
- [ ] User created with Messenger channel
- [ ] Message stored in database
- [ ] Webhook returns 200 OK quickly

### Webhook Timeout Protection
- [ ] Webhooks respond within 20 seconds (Meta requirement)
- [ ] Long bot processing doesn't block webhook response
- [ ] Background tasks process messages asynchronously

---

## Phase 4: Bot Engine Multi-Channel Support

### Bot Engine Parameters
- [ ] `process_message()` accepts `channel` parameter
- [ ] `process_message()` accepts `user_identifier` parameter
- [ ] Instagram messages processed: `channel="instagram"`, `user_identifier="PSID"`
- [ ] Messenger messages processed: `channel="messenger"`, `user_identifier="PSID"`
- [ ] WhatsApp still works: `channel="whatsapp"`, `user_identifier="phone"`

### MessageSender Routing
- [ ] MessageSender routes to TwilioSender for WhatsApp
- [ ] MessageSender routes to MetaSender for Instagram
- [ ] MessageSender routes to MetaSender for Messenger
- [ ] Missing config logs error gracefully
- [ ] Invalid channel throws appropriate error

### MetaSenderService
- [ ] Sends message to Instagram via Graph API
- [ ] Sends message to Messenger via Graph API
- [ ] Typing indicators work
- [ ] Character limit (2000) enforced
- [ ] Retry logic on failure (3 retries)
- [ ] Error handling logs errors without crashing

### Backwards Compatibility
- [ ] WhatsApp messages still process correctly
- [ ] Existing WhatsApp users not affected
- [ ] TwilioSender still works for WhatsApp
- [ ] No regressions in WhatsApp flow

---

## Phase 5: HubSpot Multi-Channel Sync

### Instagram Contact Sync
- [ ] Instagram user syncs to HubSpot without phone
- [ ] Email-only contacts created successfully
- [ ] `lead_source` field = "instagram"
- [ ] `channel_user_id` field = Instagram PSID
- [ ] Custom properties created: `intent_score`, `sentiment`, `needs`
- [ ] Lifecycle stage maps correctly (qualifying → marketingqualifiedlead)

### Messenger Contact Sync
- [ ] Messenger user syncs to HubSpot without phone
- [ ] `lead_source` field = "messenger"
- [ ] `channel_user_id` field = Messenger PSID
- [ ] Custom properties populated

### WhatsApp Contact Sync (Backwards Compatibility)
- [ ] WhatsApp contacts sync with phone number
- [ ] `lead_source` field = "whatsapp"
- [ ] Phone field populated for WhatsApp
- [ ] No regressions in WhatsApp HubSpot sync

### Contact Search
- [ ] Can search by email
- [ ] Can search by phone (WhatsApp)
- [ ] Can search by PSID (Instagram/Messenger)
- [ ] Duplicate prevention works

---

## Phase 6: OAuth & Integration

### OAuth Connection Flow
- [ ] Click "Connect Instagram" button in UI
- [ ] Redirects to Facebook OAuth page
- [ ] OAuth URL includes correct scopes: `instagram_basic,pages_show_list,pages_messaging`
- [ ] OAuth state parameter includes user_id:channel
- [ ] User grants permissions
- [ ] Redirects back to frontend `/integrations/callback`

### OAuth Callback Processing
- [ ] Callback receives `code` and `state` parameters
- [ ] Backend exchanges code for access token
- [ ] Retrieves user's Facebook Pages
- [ ] Gets page access token for first page
- [ ] Gets Instagram Business Account ID
- [ ] Stores integration in `channel_integrations` table:
  - [ ] `page_id` stored
  - [ ] `page_access_token` stored
  - [ ] `page_name` stored
  - [ ] `instagram_account_id` stored (for Instagram)
- [ ] Subscribes webhook to page
- [ ] Returns success to frontend

### Integration Management
- [ ] GET `/integrations/list` returns user's integrations
- [ ] Shows Instagram integrations
- [ ] Shows Messenger integrations
- [ ] Shows page names and connection dates
- [ ] DELETE `/integrations/facebook/disconnect` removes integration
- [ ] Disconnection removes from database

---

## Phase 7: Frontend UI

### Channel Badges
- [ ] Conversations page shows channel badges
- [ ] Instagram badge: Purple/Pink color
- [ ] Messenger badge: Blue color
- [ ] WhatsApp badge: Green color
- [ ] Badges display correctly in conversation list

### Channel Filtering
- [ ] "All Channels" filter shows all conversations
- [ ] "WhatsApp" filter shows only WhatsApp
- [ ] "Instagram" filter shows only Instagram
- [ ] "Messenger" filter shows only Messenger
- [ ] Filter persists on page refresh

### CRM Page Channel Info
- [ ] CRM contacts show channel badge
- [ ] Channel info visible in contact details
- [ ] Channel user ID displayed (PSID or phone)
- [ ] Source channel tracked

### Integrations Page
- [ ] Integrations page accessible at `/dashboard/integrations`
- [ ] Shows connected integrations list
- [ ] "Connect Instagram" button visible
- [ ] "Connect Messenger" button visible
- [ ] Connection status accurate (Connected/Not Connected)
- [ ] "Disconnect" button works
- [ ] OAuth flow works from UI

---

## Phase 8: Deployment & Production

### Docker Compose Production
- [ ] `docker compose build` succeeds
- [ ] All app services start: `docker compose up -d`
- [ ] API container running
- [ ] Web container running
- [ ] PostgreSQL container running when local profile is enabled: `docker compose --profile local up -d`
- [ ] Health checks pass in containers

### Service Accessibility
- [ ] API accessible on port 8000
- [ ] Frontend accessible on port 3000
- [ ] PostgreSQL accessible from API container
- [ ] Environment variables loaded correctly
- [ ] Database migrations applied on startup

### Health Checks
- [ ] API health: `GET http://localhost:8000/health` returns 200
- [ ] Frontend health: `GET http://localhost:3000/api/health` returns 200
- [ ] Bot health: `GET http://localhost:8000/bot/health` returns 200

---

## End-to-End Integration Tests

### Instagram End-to-End Flow
**Scenario:** User sends DM to Instagram Business Account

1. **Send Instagram DM**
   - [ ] Open Instagram
   - [ ] Send DM to test business account: "Hello, I'm interested in your product"

2. **Verify Webhook Received**
   - [ ] Check API logs: Webhook POST received
   - [ ] Signature verified successfully
   - [ ] No errors in logs

3. **Verify User Created**
   - [ ] Query database: `SELECT * FROM users WHERE channel='instagram'`
   - [ ] User has correct PSID
   - [ ] User name populated (if available)

4. **Verify Bot Response**
   - [ ] Bot `process_message()` called
   - [ ] Response generated
   - [ ] MetaSender sends message
   - [ ] User receives response in Instagram DM

5. **Verify Message Stored**
   - [ ] Query: `SELECT * FROM messages WHERE user_id=...`
   - [ ] Incoming message stored
   - [ ] Outgoing response stored

6. **Verify HubSpot Contact**
   - [ ] Check HubSpot: Contact created
   - [ ] `lead_source` = "instagram"
   - [ ] `channel_user_id` = Instagram PSID
   - [ ] Custom properties populated

---

### Messenger End-to-End Flow
**Scenario:** User sends message to Facebook Page

1. **Send Messenger Message**
   - [ ] Open Messenger
   - [ ] Send message to test page: "I need help with pricing"

2. **Verify Webhook**
   - [ ] Webhook received at `/webhook/messenger`
   - [ ] Signature valid
   - [ ] Returns 200 OK

3. **Verify User Created**
   - [ ] User in database with channel='messenger'
   - [ ] PSID stored correctly

4. **Verify Bot Response**
   - [ ] Bot processes message
   - [ ] Response sent via MetaSender
   - [ ] User receives response in Messenger

5. **Verify Message Storage**
   - [ ] Messages in database
   - [ ] Timestamps correct

6. **Verify HubSpot Sync**
   - [ ] Contact created in HubSpot
   - [ ] `lead_source` = "messenger"

---

### Multi-Tenant Isolation Test
**Scenario:** Two tenants with different Facebook Pages

1. **Setup**
   - [ ] Tenant A connects Instagram (Page A)
   - [ ] Tenant B connects Instagram (Page B)

2. **Verify Separate Configs**
   - [ ] Tenant A has page_access_token_A in DB
   - [ ] Tenant B has page_access_token_B in DB
   - [ ] Tokens are different

3. **Test Message Routing**
   - [ ] Send DM to Page A
   - [ ] Verify message routes to Tenant A
   - [ ] Send DM to Page B
   - [ ] Verify message routes to Tenant B

4. **Verify Data Isolation**
   - [ ] Tenant A sees only their conversations
   - [ ] Tenant B sees only their conversations
   - [ ] No cross-tenant data leakage

---

## Performance Tests

### Concurrent Message Processing
- [ ] Send 10 Instagram messages concurrently
- [ ] All messages processed successfully
- [ ] No database connection pool exhaustion
- [ ] No webhook timeouts
- [ ] Response time < 2 seconds per message

### Load Testing
- [ ] Send 10 Messenger messages concurrently
- [ ] All webhooks return 200 OK
- [ ] Bot processes all messages
- [ ] No crashes or errors

### Response Time
- [ ] Webhook response time < 500ms
- [ ] Bot processing time < 2 seconds
- [ ] HubSpot sync < 3 seconds (async)

---

## Security Tests

### Signature Verification
- [ ] Invalid signature rejected (403)
- [ ] Missing signature rejected (403)
- [ ] Signature without prefix rejected (BUG-008)
- [ ] Replay attack prevented (timestamp check if implemented)

### Authentication
- [ ] Unauthenticated requests rejected
- [ ] JWT validation works
- [ ] Expired tokens rejected

### Input Validation
- [ ] SQL injection attempts blocked
- [ ] XSS attempts sanitized
- [ ] Malformed payloads handled gracefully

### Rate Limiting
- [ ] API rate limiting works
- [ ] 200 requests/min limit enforced
- [ ] Rate limit headers returned

---

## Error Handling Tests

### Missing Configuration
- [ ] User without channel integration logs error
- [ ] Missing `page_access_token` handled gracefully
- [ ] Missing env vars return appropriate errors

### External API Failures
- [ ] Facebook Graph API timeout handled
- [ ] HubSpot API failure doesn't crash bot
- [ ] Retry logic works

### Database Errors
- [ ] Connection failures logged
- [ ] Transaction rollbacks work
- [ ] Deadlock handling

---

## Regression Tests

### WhatsApp Still Works
- [ ] Send WhatsApp message via Twilio webhook
- [ ] User created with channel='whatsapp'
- [ ] Bot processes message
- [ ] Response sent via Twilio
- [ ] HubSpot sync includes phone

### Existing Features Unaffected
- [ ] Authentication still works
- [ ] User profiles accessible
- [ ] CRM features functional
- [ ] RAG document upload works
- [ ] Dashboard loads correctly

---

## Testing Notes

**Date:** ___________
**Tester:** ___________
**Environment:** Development / Staging / Production

### Issues Found

| # | Description | Severity | Status |
|---|-------------|----------|--------|
| 1 |             |          |        |
| 2 |             |          |        |
| 3 |             |          |        |

### Notes

```
[Add any observations, concerns, or recommendations here]
```

---

## Sign-Off

- [ ] All critical tests passing
- [ ] No blocking issues found
- [ ] Ready for production deployment

**QA Lead Signature:** ___________
**Date:** ___________
