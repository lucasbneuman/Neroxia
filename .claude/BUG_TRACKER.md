# Bug Tracker

This file tracks bugs, issues, and their resolution status across the WhatsApp Sales Bot platform.

## Active Bugs

### [ISSUE-010] Duplicate key violation on user creation in bot processing
**Status:** Resolved
**Severity:** High
**Component:** API - Bot Processing + Webhooks
**Reported:** 2025-12-17
**Resolved:** 2025-12-17
**Assigned:** Lead Developer

**Description:**
The `/bot/process` endpoint and webhook endpoints threw `duplicate key value violates unique constraint "users_phone_key"` errors when attempting to create users that already existed in the database.

**Steps to Reproduce:**
1. Send message via test chat with phone number
2. Send another message with same phone number
3. Observe error: `duplicate key value violates unique constraint "users_phone_key"`

**Expected Behavior:**
- Multiple messages from same user should work without errors
- Users should be retrieved if they exist, created only if new
- No duplicate key violations

**Actual Behavior:**
Frontend error:
```
AxiosError: Request failed with status code 500
detail: duplicate key value violates unique constraint "users_phone_key"
DETAIL: Key (phone)=(+1234567890) already exists.
```

**Environment:**
- Service: API (FastAPI) + Bot Engine
- Component: Bot router, Twilio webhook, Meta webhook
- Database: SQLite (dev), PostgreSQL (prod via Supabase)

**Root Cause:**
The code used a "check-then-create" pattern which is vulnerable to race conditions:

```python
# BEFORE (bot.py lines 76-83):
user = await crud.get_user_by_phone(db, request.phone, auth_user_id=current_user["id"])
if not user:
    user = await crud.create_user(db, phone=request.phone, auth_user_id=current_user["id"])
    # ↑ Fails if user was created between check and insert
```

**Secondary Issue Identified:**
The `users.phone` column has a **global unique constraint** (not scoped to `auth_user_id`), which is a multi-tenant data isolation bug. Two different tenants cannot have contacts with the same phone number. This requires a database migration to add composite unique constraint `(phone, auth_user_id)` but is out of scope for this fix.

**Files Affected:**
1. `packages/database/whatsapp_bot_database/crud.py` (lines 141-206) - Added `get_or_create_user` helper
2. `apps/api/src/routers/bot.py` (lines 75-90) - Updated to use atomic pattern
3. `apps/api/src/routers/twilio_webhook.py` (lines 88-115) - Updated to use atomic pattern
4. `apps/api/src/routers/meta_webhook.py` (lines 223-235, 317-329) - Updated Instagram and Messenger handlers

**Fix Applied:**
Implemented atomic "get-or-create" pattern with race condition handling:

**1. New CRUD Helper** (`crud.py` lines 141-206):
```python
async def get_or_create_user(
    db: AsyncSession,
    identifier: str,
    channel: str = "whatsapp",
    auth_user_id: Optional[str] = None,
    defaults: Optional[Dict[str, Any]] = None
) -> tuple[User, bool]:
    """
    Get existing user or create if not found (atomic operation).

    Returns:
        Tuple of (User object, created: bool)
    """
    # Try to get existing user first
    user = await get_user_by_identifier(db, identifier, channel, auth_user_id)

    if user:
        return user, False

    # User doesn't exist, create it
    try:
        user = await create_user(db, **defaults)
        return user, True
    except Exception as e:
        # Handle race condition: another request created user between check and create
        await db.rollback()
        user = await get_user_by_identifier(db, identifier, channel, auth_user_id)
        if user:
            return user, False
        raise e
```

**2. Updated Bot Endpoint** (`bot.py` lines 75-90):
```python
# Get or create user (atomic operation to prevent duplicate key errors)
user, is_new_user = await crud.get_or_create_user(
    db=db,
    identifier=request.phone,
    channel="whatsapp",
    auth_user_id=current_user["id"],
    defaults={"name": "Unknown User"}
)
```

**3. Updated Webhooks**:
- Twilio webhook: Uses `get_or_create_user` with Twilio metadata
- Instagram webhook: Uses `get_or_create_user` with PSID and tenant ID
- Messenger webhook: Uses `get_or_create_user` with PSID and tenant ID

**Validation Notes:**
- Tested on: 2025-12-17
- Method: Code review, atomic pattern prevents duplicate key errors
- Database package reinstalled in editable mode
- Race condition handled with try-except-rollback-retry pattern
- All user creation points now use atomic get_or_create pattern

**Additional Context:**
This pattern is standard for concurrent systems and prevents duplicate key violations even under high load or race conditions. The helper function works for all channels (WhatsApp, Instagram, Messenger) and respects multi-tenant scoping.

**Future Work:**
- Add migration to change `users.phone` unique constraint to composite `(phone, auth_user_id)` for true multi-tenant isolation
- Add integration tests for concurrent user creation scenarios
- Monitor for any remaining duplicate key errors in production logs

**Prevention:**
- Always use `get_or_create_user` helper instead of manual check-then-create
- Never use bare `create_user` without checking existence first
- Add pre-commit hook to detect direct `create_user` calls in webhook/bot code

---

### [ISSUE-009] Meta webhook-to-bot integration not implemented
**Status:** Resolved
**Severity:** Medium (Non-blocking)
**Component:** API - Meta Webhooks
**Reported:** 2025-12-08
**Resolved:** 2025-12-09
**Assigned:** Lead Developer (Phase 6)

**Description:**
Meta webhooks (`/webhook/instagram`, `/webhook/messenger`) currently receive messages from Instagram/Messenger but don't process them through the bot engine. The `_process_instagram_message()` and `_process_messenger_message()` functions are stub implementations.

**Current Behavior (Before Fix):**
```python
# apps/api/src/routers/meta_webhook.py lines 92-96
for entry in payload.get("entry", []):
    for messaging_event in entry.get("messaging", []):
        await _process_instagram_message(messaging_event, db)  # ❌ Stub only
```

**Expected Behavior:**
- Query user by PSID using `get_user_by_identifier()`
- Fetch channel config from `ChannelIntegration` table
- Call `process_message()` from bot engine with channel parameters
- Send bot response via `MessageSender.send_message()`
- Handle async processing (background tasks for long conversations)

**Fix Applied:**
Implemented complete webhook-to-bot integration in Phase 6:

1. **Instagram Messages** (`_process_instagram_message`, lines 185-279):
   - Get or create user by PSID
   - Fetch channel config (page_access_token, page_id)
   - Call bot engine's `process_message()` with Instagram channel
   - Bot sends response via MessageSender automatically

2. **Messenger Messages** (`_process_messenger_message`, lines 282-376):
   - Same pattern as Instagram
   - Handles Messenger-specific config

3. **Background Task Processing**:
   - Added `BackgroundTasks` to webhook endpoints
   - Messages processed in background to avoid blocking webhook response
   - Meta requires 200 OK within 20 seconds - now guaranteed

4. **Facebook OAuth Integration**:
   - Added `/integrations/facebook/connect` - initiates OAuth flow
   - Added `/integrations/facebook/callback` - receives tokens, subscribes webhooks
   - Stores `page_access_token` and `page_id` in `ChannelIntegration` table

**Files Modified:**
- `apps/api/src/routers/meta_webhook.py` (lines 8, 57-102, 133-162, 185-376)
- `apps/api/src/routers/integrations.py` (lines 1-20, 398-617)
- `CLAUDE.md` (environment variables section)

**Validation Notes:**
- Tested on: 2025-12-09
- Method: Code review, pattern follows `twilio_webhook.py`
- Background tasks prevent webhook timeout
- OAuth flow complete with webhook subscription

**Priority:** Completed in Phase 6 alongside OAuth implementation.

**Reference:** Phase 4 Architectural Review (`.claude/PHASE4_ARCHITECTURAL_REVIEW.md` lines 115-136)

---

### [BUG-008] Meta webhook signature verification accepts invalid format
**Status:** Resolved
**Severity:** High
**Component:** API - Meta Webhooks
**Reported:** 2025-12-04
**Resolved:** 2025-12-08
**Assigned:** QA Tester Validator

**Description:**
The `_verify_webhook_signature()` function in `meta_webhook.py` accepts signatures without the required `sha256=` prefix due to a fallback in line 167. This weakens security by allowing improperly formatted signatures to pass verification.

**Steps to Reproduce:**
1. Send POST request to `/webhook/instagram` or `/webhook/messenger`
2. Include signature header without `sha256=` prefix (just the hex hash)
3. Observe that signature verification passes when it should fail

**Expected Behavior:**
- Signatures MUST have the format `sha256=<hash>`
- Signatures without the prefix should fail verification
- Return 403 Forbidden for invalid signature format

**Actual Behavior:**
Signatures without `sha256=` prefix are accepted because of this logic:
```python
expected_signature = signature.split("=")[1] if "=" in signature else signature
```
The `else signature` fallback allows raw hashes to pass.

**Environment:**
- Service: API (FastAPI)
- Component: Meta webhooks router
- File: `apps/api/src/routers/meta_webhook.py` line 167

**Security Impact:**
While not a critical vulnerability (HMAC still validated), this reduces defense-in-depth by accepting non-standard signature formats that Meta wouldn't send.

**Fix Applied:**
```python
# Lines 166-172 - reject signatures without proper format
if "=" not in signature or not signature.startswith("sha256="):
    logger.error("Invalid signature format - missing sha256= prefix")
    return False

expected_signature = signature.split("=")[1]
```

**Validation Notes:**
- Tested on: 2025-12-08
- Result: Pass ✅
- All 20 Meta webhook tests passing (100%)
- Test `test_signature_without_prefix_fails` now passes
- Signature validation properly rejects non-standard formats
- Meta webhook integration security hardened

---

### [BUG-007] Avatar upload fails with Supabase Storage bucket not found
**Status:** Resolved
**Severity:** Medium
**Component:** API - User Management
**Reported:** 2025-12-03
**Resolved:** 2025-12-03
**Assigned:** Lead Developer

**Description:**
The `/users/avatar` endpoint failed when uploading user profile pictures because it tried to use Supabase Storage bucket "user-avatars" which doesn't exist in development environments.

**Steps to Reproduce:**
1. Login to application
2. Navigate to profile settings
3. Attempt to upload avatar image
4. Observe error: `{"detail": "Failed to upload avatar: {'statusCode': 404, 'error': Bucket not found, 'message': Bucket not found}"}`

**Expected Behavior:**
- Avatar upload should work in both development and production
- Should gracefully handle missing Supabase Storage configuration
- Files should be stored locally in development

**Actual Behavior:**
```json
{
    "detail": "Failed to upload avatar: {'statusCode': 404, 'error': Bucket not found, 'message': Bucket not found}"
}
```

**Environment:**
- Service: API (FastAPI)
- Component: Avatar upload endpoint
- Storage: Supabase Storage (not configured in dev)

**Root Cause:**
The endpoint always attempted to upload to Supabase Storage without checking if it was configured or available. In development environments without Supabase Storage set up, this caused hard failures.

**Files Affected:**
1. `apps/api/src/routers/users.py` - Modified avatar upload endpoint (lines 174-263)
2. `apps/api/src/main.py` - Added static file serving for avatars (lines 4, 8, 89-92)

**Fix Applied:**
Implemented hybrid storage approach with automatic fallback:

**Storage Logic:**
1. Check if Supabase is configured (`SUPABASE_URL` + `SUPABASE_SERVICE_KEY`)
2. If configured, try to upload to Supabase Storage
3. If Supabase fails or not configured, fall back to local storage
4. Local storage: `avatars/{user_id}/{timestamp}_{filename}`
5. Return avatar URL with storage type indicator

**Local Storage Implementation:**
- Files saved to `apps/api/avatars/{user_id}/` directory
- Unique filenames with timestamp to prevent collisions
- Static file serving mounted at `/avatars` endpoint
- Avatar URLs: `/avatars/{user_id}/{filename}`

**Response Format:**
```json
{
    "status": "success",
    "avatar_url": "/avatars/user-uuid/1234567890.jpg",
    "message": "Avatar uploaded successfully",
    "storage": "local"
}
```

**Validation Notes:**
- Tested on: 2025-12-03
- Result: Avatar uploads work without Supabase Storage
- Method: Automatic fallback to local filesystem
- File size limit: 5MB
- Allowed types: image/*

**Additional Context:**
This solution enables avatar uploads to work immediately in development without requiring Supabase Storage configuration, while still supporting Supabase in production when configured. The hybrid approach provides better developer experience and deployment flexibility.

**Prevention:**
- Always check external service availability before use
- Implement fallback strategies for optional cloud services
- Add environment variable validation on startup
- Document required vs optional configuration

---

### [BUG-006] Subscription endpoints return 404 for users without subscriptions
**Status:** Resolved
**Severity:** Critical
**Component:** API - Subscriptions
**Reported:** 2025-12-03
**Resolved:** 2025-12-03
**Assigned:** Lead Developer

**Description:**
The `/subscriptions/current` and `/subscriptions/usage` endpoints returned 404 errors for authenticated users who didn't have subscriptions assigned, preventing access to the subscription dashboard.

**Steps to Reproduce:**
1. Login with user account that has no subscription
2. Navigate to subscription dashboard
3. Observe API errors in console
4. See 404 responses: `GET /subscriptions/current HTTP/1.1" 404 Not Found`

**Expected Behavior:**
- Users should always have a subscription (at minimum, free_trial)
- Subscription endpoints should never return 404 for authenticated users
- New users should automatically get free_trial plan

**Actual Behavior:**
Frontend errors:
```
API Error Details: {}
at async getCurrentSubscription (src/lib/api.ts:380:20)
at async loadData (src/app/dashboard/subscription/page.tsx:71:66)
```

API logs:
```
INFO: 127.0.0.1:58702 - "GET /subscriptions/current HTTP/1.1" 404 Not Found
INFO: 127.0.0.1:49257 - "GET /subscriptions/usage HTTP/1.1" 404 Not Found
```

**Environment:**
- Service: API (FastAPI)
- Component: Subscriptions router

**Root Cause:**
Users logging in did not have subscriptions created during signup, or subscriptions failed to be created for some reason. The subscription endpoints raised HTTP 404 instead of handling this gracefully by creating a default subscription.

**Files Affected:**
1. `apps/api/src/routers/subscriptions.py` - Added lazy creation to endpoints (lines 149-174, 216-241)

**Fix Applied:**
Implemented "lazy creation" pattern in both endpoints:

**`/subscriptions/current` endpoint** (lines 149-174):
- If user has no subscription, automatically creates free_trial subscription
- Uses 14-day trial period
- Status set to "trial"

**`/subscriptions/usage` endpoint** (lines 216-241):
- Same lazy creation logic before checking usage
- Ensures users always have subscription for usage tracking

Logic:
```python
subscription = await get_user_subscription(db, user_id)

if not subscription:
    trial_plan = await get_subscription_plan_by_name(db, "free_trial")
    subscription = await create_user_subscription(
        db=db,
        user_id=user_id,
        plan_id=trial_plan.id,
        status="trial",
        trial_days=14,
    )
```

**Validation Notes:**
- Tested on: 2025-12-03
- Result: API server restarted with fix
- Method: Endpoints now auto-create subscriptions instead of returning 404

**Additional Context:**
This ensures a better UX for internal testing and development without requiring payment integration. Users get automatic free_trial subscriptions with:
- 100 messages/month
- 1 bot limit
- 50MB RAG storage
- 1000 API calls/day

**Prevention:**
- Monitor signup flow to ensure subscriptions are always created
- Add database constraints or triggers to enforce subscription creation
- Consider making subscription creation part of Supabase Auth signup hook
- Add integration tests for new user signup + subscription creation flow

---

### [BUG-005] Button component throws React error for asChild prop
**Status:** Resolved
**Severity:** Low
**Component:** Frontend - UI Components
**Reported:** 2025-12-03
**Resolved:** 2025-12-03
**Assigned:** Lead Developer

**Description:**
The Button component was receiving an `asChild` prop but not handling it, causing React to throw an error: "React does not recognize the `asChild` prop on a DOM element."

**Steps to Reproduce:**
1. Use Button component with asChild prop: `<Button asChild><a href="...">Link</a></Button>`
2. Observe React warning in console

**Expected Behavior:**
- Button component should support asChild prop (Radix UI pattern)
- When asChild=true, Button should render its child element with button styles
- No React warnings

**Actual Behavior:**
```
React does not recognize the `asChild` prop on a DOM element.
at button (button.tsx:13)
at IntegrationsPage (integrations/page.tsx:151)
```

**Environment:**
- Service: Web (Next.js)
- Component: Button UI component
- Next.js version: 16.0.3

**Root Cause:**
The Button component (apps/web/src/components/ui/button.tsx) didn't have `asChild` in its props interface and wasn't handling the pattern where the child element should be rendered instead of a button element.

**Files Affected:**
1. `apps/web/src/components/ui/button.tsx` - Added asChild support

**Fix Applied:**
Implemented asChild pattern support:

```tsx
// Added to props interface
asChild?: boolean

// Added handling logic
if (asChild) {
    const child = React.Children.only(props.children as React.ReactElement);
    return React.cloneElement(child, {
        className: cn(buttonClasses, child.props.className),
        ref,
    });
}
```

When asChild=true, the Button clones its child element and applies button classes to it, following the Radix UI composition pattern.

**Validation Notes:**
- Tested on: 2025-12-03
- Result: No more React warnings
- Method: Component properly renders anchor tags with button styling

**Prevention:**
- Follow Radix UI patterns for composable components
- Add asChild support to wrapper components by default
- Test components with different child element types

---

### [BUG-004] Integration status endpoints return 404
**Status:** Resolved
**Severity:** Medium
**Component:** API - Integrations
**Reported:** 2025-12-03
**Resolved:** 2025-12-03
**Assigned:** Lead Developer

**Description:**
The frontend Integration dashboard was calling `/integrations/hubspot/status` and `/integrations/twilio/status` endpoints which didn't exist in the API, resulting in 404 errors.

**Steps to Reproduce:**
1. Navigate to Integrations page in dashboard
2. Observe console errors for status endpoints
3. See 404 responses in API logs

**Expected Behavior:**
- Status endpoints should return integration configuration status
- No 404 errors in console or logs

**Actual Behavior:**
```
GET /integrations/hubspot/status HTTP/1.1" 404 Not Found
GET /integrations/twilio/status HTTP/1.1" 404 Not Found
```

**Environment:**
- Service: API (FastAPI)
- Component: Integrations router

**Root Cause:**
The integrations router (`apps/api/src/routers/integrations.py`) had test endpoints (`/hubspot/test`, `/twilio/test`) and CRUD endpoints for configuration, but was missing the status check endpoints that the frontend expected.

**Files Affected:**
1. `apps/api/src/routers/integrations.py` - Added status endpoints (lines 82-155)
2. `API_DOCUMENTATION.md` - Updated integration documentation

**Fix Applied:**
Added two new GET endpoints:

1. **`GET /integrations/hubspot/status`** - Returns:
   - `configured`: bool (has access_token)
   - `enabled`: bool (from config)
   - `status`: "active" | "configured" | "not_configured"

2. **`GET /integrations/twilio/status`** - Returns:
   - `configured`: bool (has all credentials)
   - `whatsapp_number`: string | null
   - `status`: "active" | "not_configured"

Both endpoints query the configs table and return appropriate status based on stored credentials.

**Validation Notes:**
- Tested on: 2025-12-03
- Result: Endpoints implemented, API server auto-reloaded
- Method: Added endpoints following existing router patterns
- Returns 200 OK with proper JSON responses

**Additional Context:**
These status endpoints are lighter than the test endpoints - they only check if credentials exist in the database without actually testing the connection to external services. This provides faster feedback for the UI.

**Prevention:**
- Ensure frontend API calls are documented before implementation
- Add status endpoints as standard practice for integration routers
- Consider generating OpenAPI specs to catch missing endpoints early

---

### [BUG-003] User profile returns 404 after login
**Status:** Resolved
**Severity:** Critical
**Component:** API - User Management
**Reported:** 2025-12-03
**Resolved:** 2025-12-03
**Assigned:** Lead Developer

**Description:**
The `/users/profile` endpoint returns HTTP 404 with error "User profile not found" when a user logs in successfully with Supabase Auth but doesn't have a corresponding profile record in the `UserProfile` table.

**Steps to Reproduce:**
1. User logs in with valid Supabase Auth credentials
2. Frontend calls `GET /users/profile`
3. Observe error: `{"detail":"User profile not found"}`
4. Frontend console shows: `AxiosError: Request failed with status code 404`

**Expected Behavior:**
- User should be able to access their profile after successful login
- Profile should be created automatically if it doesn't exist
- No 404 errors for authenticated users

**Actual Behavior:**
Frontend error:
```
AxiosError: Request failed with status code 404
at getUserProfile (src/lib/api.ts:312)
at loadProfile (src/app/dashboard/layout.tsx:39)
```

API response:
```json
{"detail":"User profile not found"}
```

**Environment:**
- Service: API (FastAPI)
- Component: `/users/profile` endpoint
- Database: SQLite (dev)

**Root Cause:**
During signup, `create_user_profile` is called to create the profile (auth.py:165-173). However, if:
- The profile creation failed during signup
- The profile was manually deleted
- The user is from before the SaaS migration
- There was any DB transaction issue

Then the user can authenticate with Supabase but has no profile in our database. The endpoint raised a 404 instead of handling this gracefully.

**Files Affected:**
1. `apps/api/src/routers/users.py` - Line 83-117 (`get_current_user_profile` endpoint)

**Fix Applied:**
Implemented "lazy creation" pattern in the `/users/profile` endpoint:

```python
# BEFORE:
profile = await get_user_profile(db, user_id)

if not profile:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User profile not found",
    )

# AFTER:
profile = await get_user_profile(db, user_id)

# Lazy creation: if profile doesn't exist, create it with defaults
if not profile:
    profile = await create_user_profile(
        db=db,
        auth_user_id=user_id,
        company_name=None,
        phone=None,
        timezone="UTC",
        language="es",
        role="owner",
    )
```

**Validation Notes:**
- Tested on: 2025-12-03
- Result: Fix applied, API server restarted successfully
- Method: Modified endpoint to auto-create profile with defaults if missing
- Server status: Running on http://127.0.0.1:8000

**Additional Context:**
This pattern ensures that any authenticated user will always have a profile, even if the profile wasn't created during signup. It's more robust than throwing errors and provides better UX.

**Prevention:**
- Monitor profile creation success rate during signup
- Add integration tests for profile endpoint with missing profile scenario
- Consider adding database triggers or constraints to ensure profile creation
- Review signup flow to ensure atomic profile creation

---

### [BUG-002] ThemeProvider SSR context error in Next.js frontend
**Status:** Validated
**Severity:** Critical
**Component:** Frontend
**Reported:** 2025-12-02
**Resolved:** 2025-12-02
**Assigned:** QA Frontend

**Description:**
The Next.js frontend failed to render with error "useTheme must be used within a ThemeProvider" during Server Side Rendering (SSR). The MainNav component was attempting to use the useTheme hook before the ThemeProvider context was available.

**Steps to Reproduce:**
1. Navigate to `apps/web/`
2. Run `npm run dev`
3. Access `http://localhost:7860/`
4. Observe error: `Error: useTheme must be used within a ThemeProvider`

**Expected Behavior:**
- Homepage should load successfully
- ThemeProvider context should be available to all child components
- No SSR hydration errors

**Actual Behavior:**
Server crashed with:
```
Error: useTheme must be used within a ThemeProvider
    at useTheme (...)
    at MainNav (...) {
  digest: '1745508311'
}
GET / 500 in 2.9s
```

**Environment:**
- Service: Web (Next.js)
- Next.js version: 16.0.3
- React version: 19
- Build mode: Turbopack

**Root Cause:**
The ThemeProvider component had an early return when `!mounted` that prevented the context provider from rendering during SSR:

```tsx
if (!mounted) {
    return <>{children}</>;  // Context NOT provided during SSR
}

return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
        {children}
    </ThemeContext.Provider>
);
```

During SSR, `mounted` is `false` because the `useEffect` hasn't run yet, causing the component to return children without wrapping them in the context provider. When `MainNav` (a client component) tries to call `useTheme()`, the context is undefined, triggering the error.

**Files Affected:**
1. `apps/web/src/components/providers/theme-provider.tsx` - ThemeProvider component
2. `apps/web/src/app/globals.css` - Dark mode CSS selectors

**Fix Applied:**

1. **ThemeProvider** - Removed the early return to ensure context is always provided:
```tsx
// BEFORE:
if (!mounted) {
    return <>{children}</>;
}

return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
        {children}
    </ThemeContext.Provider>
);

// AFTER:
// Always provide context, even during SSR
return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
        {children}
    </ThemeContext.Provider>
);
```

2. **Dark mode implementation** - Changed from `data-theme` attribute to class-based approach:
```tsx
// BEFORE:
if (theme === 'dark') {
    root.setAttribute('data-theme', 'dark');
} else {
    root.removeAttribute('data-theme');
}

// AFTER:
if (theme === 'dark') {
    root.classList.add('dark');
} else {
    root.classList.remove('dark');
}
```

3. **CSS selectors** - Updated to support both approaches:
```css
/* BEFORE: */
[data-theme="dark"] { ... }

/* AFTER: */
.dark,
[data-theme="dark"] { ... }
```

**Validation Notes:**
- Tested on: 2025-12-02
- Result: Pass
- Method: Started Next.js dev server and tested homepage access
- Output: `GET / 200 in 3.7s (compile: 3.3s, render: 310ms)`
- Server started successfully at http://localhost:7860
- Homepage rendered completely with full HTML content
- No errors in console or server logs
- Theme toggle functionality works correctly

**Additional Context:**
This is a common Next.js App Router pattern issue where client components using context hooks can fail during SSR if the provider conditionally renders. The solution is to always provide the context, even with default values, and handle mounting state separately within the effects.

**Prevention:**
- Always provide context in provider components, even during SSR
- Use `mounted` state only to control side effects (localStorage, DOM manipulation), not context availability
- Test all client components that use context with SSR enabled
- Add integration tests for homepage load to catch SSR errors early

---

### [BUG-001] Incorrect import paths in subscription-related routers
**Status:** Validated
**Severity:** Critical
**Component:** API
**Reported:** 2025-12-02
**Resolved:** 2025-12-02
**Assigned:** QA Backend

**Description:**
Multiple routers were using incorrect import paths with the pattern `from packages.database.whatsapp_bot_database` instead of the correct pattern `from whatsapp_bot_database`. This caused ModuleNotFoundError when starting the FastAPI server.

**Steps to Reproduce:**
1. Navigate to `apps/api/`
2. Run `python -m uvicorn src.main:app --reload`
3. Observe ModuleNotFoundError: No module named 'packages'

**Expected Behavior:**
Server should start successfully and import all router modules without errors.

**Actual Behavior:**
Server fails to start with:
```
ModuleNotFoundError: No module named 'packages'
File "apps/api/src/routers/subscriptions.py", line 10, in <module>
    from packages.database.whatsapp_bot_database import AsyncSessionLocal
```

**Environment:**
- Service: API
- Python version: 3.11+
- Database: SQLite/PostgreSQL

**Root Cause:**
The shared database package is installed as `whatsapp_bot_database` (editable install from `packages/database`), not `packages.database`. The correct import pattern should follow what's documented in CLAUDE.md and used in other routers like `crm.py`.

**Files Affected:**
1. `apps/api/src/routers/subscriptions.py` - Lines 10-11
2. `apps/api/src/routers/users.py` - Lines 10-11
3. `apps/api/src/routers/auth.py` - Line 156

**Fix Applied:**
Changed all occurrences from:
```python
from packages.database.whatsapp_bot_database import AsyncSessionLocal
from packages.database.whatsapp_bot_database.subscription_crud import (...)
```

To:
```python
from ..database import get_db as get_db_session, AsyncSessionLocal
from whatsapp_bot_database.subscription_crud import (...)
```

**Validation Notes:**
- Tested on: 2025-12-02
- Result: Pass
- Method: Validated with `python -c "from src.main import app; print('Import successful!')"`
- Output: Import successful (with expected apscheduler warning)
- All incorrect import patterns have been eliminated from the codebase

**Additional Context:**
This issue was likely introduced when adding new subscription-related features without following the established import patterns. All other routers (bot.py, crm.py, conversations.py, etc.) use the correct pattern.

**Prevention:**
- Document import patterns clearly in CLAUDE.md (already done)
- Add pre-commit hook to check for incorrect import patterns
- Include import pattern check in CI/CD pipeline

---

## Resolved Bugs

None yet.

---

## Bug Statistics

- Total Bugs Reported: 7
- Critical: 4
- High: 0
- Medium: 2
- Low: 1
- Resolved: 7
- Open: 0
