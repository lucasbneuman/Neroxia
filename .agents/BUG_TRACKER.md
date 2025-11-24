# 🐛 Bug Tracker

**Purpose**: Live tracking of bugs and fixes
**Last Updated**: 2025-11-25 02:15:00

---

## 🔴 Critical Bugs (P0)

### Bug #12: Async Mock Database Returns Coroutine Instead of Object - 🆕 NEW
- **Reported**: 2025-11-24 18:30:00
- **Reporter**: QA Agent
- **Severity**: 🔴 Critical
- **Status**: 🆕 NEW
- **Priority**: P0 - Blocks integration tests
- **Affects**: 7 integration tests, all bot message processing
- **Files**:
  - `apps/api/tests/conftest.py` (mock_get_db fixture, lines 179-195)
  - `apps/api/src/routers/bot.py` (process_bot_message, line 93)
- **Root Cause**: Mock database dependency returns coroutine instead of awaited result
- **Assigned To**: Dev Agent
- **Related**: Test Suite Verification
- **Error Message**:
  ```
  AttributeError: 'coroutine' object has no attribute 'id'
  File "src\\routers\\bot.py", line 93, in process_bot_message
      messages_data = await crud.get_user_messages(db, user.id, limit=20)
                                                       ^^^^^^
  ```
- **Reproduction**:
  1. Run integration tests: `pytest tests/integration/test_user_flows.py -v`
  2. All 7 workflow tests fail with 500 Internal Server Error
  3. Error shows coroutine object has no attribute 'id'
- **Impact**:
  - Cannot test bot message processing
  - Cannot test complete user workflows
  - Cannot test sales conversation flows
  - Cannot test multi-user scenarios
  - Cannot test error recovery
  - Blocks verification of core functionality
- **Affected Tests** (7):
  1. `test_complete_configuration_flow` - FAILED
  2. `test_test_chat_workflow` - FAILED
  3. `test_configuration_affects_bot_behavior` - FAILED
  4. `test_complete_sales_conversation_flow` - FAILED
  5. `test_multi_user_concurrent_conversations` - FAILED
  6. `test_error_recovery_flow` - FAILED
  7. `test_configuration_persistence` - FAILED
- **Fix Plan**:
  1. Update `mock_get_db` fixture to properly handle async operations
  2. Ensure CRUD operations return mock objects, not coroutines
  3. Add proper async/await handling in mock
  4. Configure AsyncMock to return awaitable results
  5. Re-run integration tests to verify fix
- **Suggested Fix**:
  ```python
  async def mock_get_db():
      db = AsyncMock()
      # Configure mock to return proper awaitable results
      db.execute = AsyncMock(return_value=AsyncMock())
      db.commit = AsyncMock()
      db.rollback = AsyncMock()
      db.close = AsyncMock()
      try:
          yield db
      finally:
          await db.close()
  ```

### Bug #8: RAG Endpoints 404 Error - Incorrect API Routes - 🔄 IN PROGRESS
- **Reported**: 2025-11-25 01:20:00
- **Reporter**: User / LLM Bot Optimizer Agent
- **Severity**: 🔴 Critical
- **Status**: 🔄 IN PROGRESS - Upload fix attempt #3 (LLM Bot Optimizer Agent)
- **Fixed**: 2025-11-25 01:30:00 (routes), 2025-11-25 02:15:00 (clear), 2025-11-25 03:00:00 (upload v3)
- **Priority**: P0 - Blocks RAG functionality
- **Affects**: File upload feature in Configuration page, all users trying to upload documents
- **Files**:
  - `apps/web/src/lib/api.ts` (lines 49, 58, 63) - Frontend API calls
  - `apps/api/src/routers/rag.py` (lines 8, 40-71, 225) - Backend endpoint signature
- **Root Causes**:
  1. Frontend calling `/config/rag/*` but backend endpoints mounted at `/rag/*` ✅ FIXED
  2. Backend only accepting single file, frontend sending multiple files ✅ FIXED
  3. FastAPI multipart/form-data handling - multiple attempts ⏳ IN PROGRESS
  4. Clear endpoint using POST instead of DELETE ✅ FIXED
- **Assigned To**: LLM Bot Optimizer Agent
- **Related**:
  - FileUpload component (src/components/config/FileUpload.tsx)
  - RAG router (apps/api/src/routers/rag.py)
- **Error Messages**:
  1. Initial: `AxiosError: Request failed with status code 404` ✅ FIXED
  2. Upload (attempt 1): `{"detail": [{"type": "missing", "loc": ["body", "file"], "msg": "Field required"}]}` ❌ FAILED
  3. Upload (attempt 2): Same error after Request+form.getlist() approach ❌ FAILED
  4. Clear: `{"detail": "Method Not Allowed"}` ✅ FIXED
- **Reproduction**:
  1. Go to `/dashboard/config`
  2. Navigate to file upload section
  3. Try to upload files → Field required error
  4. Try to clear collection → Method not allowed ✅ FIXED
- **Fix Attempts**:
  1. ✅ **Frontend Routes** (apps/web/src/lib/api.ts) - Commit 723ecf3:
     - Changed `/config/rag/upload` → `/rag/upload`
     - Changed `/config/rag/clear` → `/rag/clear`
     - Changed `/config/rag/stats` → `/rag/stats`
     - **Status:** Working correctly

  2. ✅ **Backend Clear** (apps/api/src/routers/rag.py) - Commit 76f42a0:
     - Changed `@router.post("/clear")` → `@router.delete("/clear")`
     - **Status:** Fixed, matches frontend DELETE call

  3. ❌ **Backend Upload Attempt 1** (apps/api/src/routers/rag.py) - Commit 76f42a0:
     - Approach: Changed to `Request` object + manual `form.getlist("files")`
     - **Result:** FastAPI still validated expecting 'file' parameter
     - **Why Failed:** Pydantic validation triggered before function execution

  4. ⏳ **Backend Upload Attempt 3** (apps/api/src/routers/rag.py) - Commit f7e6527:
     - Approach: Standard FastAPI pattern `files: List[UploadFile] = File(...)`
     - Removed manual form parsing
     - Let FastAPI handle multipart/form-data automatically
     - Parameter name 'files' matches frontend FormData field
     - **Status:** Awaiting user testing

- **Testing Status**:
  - ✅ Stats endpoint returns proper data (404 resolved)
  - ✅ Clear endpoint responds to DELETE method (verified working)
  - ⏳ Upload endpoint - attempt #3 needs user verification

### Bug #1: React hydration error on login page - ✅ FIXED
- **Reported**: 2025-11-23 11:50:00
- **Reporter**: QA Agent
- **Severity**: 🔴 Critical
- **Status**: ✅ FIXED (Dev Agent)
- **Fixed**: 2025-11-23 12:35:00
- **Priority**: P0 - Blocks all users
- **Affects**: Login functionality, 100% of users blocked
- **Files**:
  - `apps/web/src/lib/supabase.ts`
  - `apps/web/src/lib/api.ts`
  - `apps/web/src/app/login/page.tsx`
- **Root Cause**: localStorage access in SSR context causing hydration mismatch
- **Fix Started**: 2025-11-23 12:25:00
- **Assigned To**: Dev Agent
- **Related**:
  - QA_REPORT.md (detailed analysis)
  - STATIC_ANALYSIS_REPORT.md (root cause)
  - TEST_CASES.md TC-AUTH-001
- **Reproduction**:
  1. Navigate to login page
  2. Enter valid credentials
  3. Click "Sign In"
  4. **Expected**: Redirect to dashboard
  5. **Actual**: Hydration error crash
- **Fix Plan**:
  1. Add ErrorBoundary component
  2. Fix Supabase client to use `createClientComponentClient()`
  3. Add SSR guards for localStorage access
  4. Test on fresh session

### Bug #2: TypeError in ConversationList Component - ✅ FIXED
- **Reported**: 2025-11-23 12:17:00
- **Reporter**: QA Agent
- **Severity**: 🔴 Critical
- **Status**: ✅ FIXED (Dev Agent)
- **Fixed**: 2025-11-23 12:40:00
- **Priority**: P0 - Blocks dashboard access
- **Affects**: Dashboard/Chat page, 100% of users after login
- **Files**:
  - `apps/web/src/components/chat/ConversationList.tsx` (line 108)
  - `apps/api/src/routers/conversations.py`
  - `apps/web/src/types/index.ts`
- **Root Cause**: Missing null checks for `conversation.user` object
- **Assigned To**: Awaiting assignment
- **Related**:
  - QA_REPORT.md (Bug #2 section)
  - TEST_CASES.md TC-CHAT-001
- **Reproduction**:
  1. Login successfully
  2. Navigate to `/dashboard/chat`
  3. **Expected**: Dashboard loads with conversation list
  4. **Actual**: TypeError crash, ErrorBoundary shows fallback
- **Fix Plan**:
  1. Add optional chaining: `conversation.user?.name`
  2. Add null validation before rendering
  3. Fix API to always include user data
  4. Update TypeScript types

### Bug #7: Test Chat Response Not Displaying - ✅ FIXED
- **Reported**: 2025-11-23 17:31:00
- **Reporter**: User / QA Agent
- **Severity**: 🔴 Critical
- **Status**: ✅ FIXED (Dev Agent)
- **Fixed**: 2025-11-23 18:40:00
- **Priority**: P0 - Cannot test bot functionality
- **Affects**: Test interface page, all users
- **Files**:
  - `apps/web/src/app/dashboard/test/page.tsx` (lines 48-64)
  - `apps/web/src/lib/api.ts` (processTestMessage function)
  - `apps/web/src/components/test/TestChat.tsx`
- **Root Cause**: Frontend doesn't display bot response even though API returns valid data
- **Assigned To**: Awaiting assignment
- **Related**: QA_REPORT.md
- **Reproduction**:
  1. Go to `/dashboard/test`
  2. Type a message and send
  3. API responds correctly: `{"response": "¡Hola de nuevo! 👋...", "user_phone": "+1234567890", ...}`
  4. **Expected**: Bot response appears in chat
  5. **Actual**: No bot response displayed in UI
- **API Response** (confirmed working):
  ```json
  {
    "response": "¡Hola de nuevo! 👋 Si necesitas información o ayuda con un producto, aquí estoy para ayudarte. 😊",
    "user_phone": "+1234567890",
    "user_name": null,
    "intent_score": 0.4,
    "sentiment": "neutral",
    "stage": "qualifying",
    "conversation_mode": "AUTO"
  }
  ```
- **Fix Plan**:
  1. Check `processTestMessage` return format in `api.ts`
  2. Verify response structure matches expected format in `page.tsx` line 48
  3. Add console.log to debug response structure
  4. Fix response parsing to extract `result.data.response` correctly
  5. Ensure `setMessages` is called with bot response
  6. Add error handling for response format mismatch
- **Fix Implemented**:
  1. Changed response check from `result.success && result.data` to `result && result.response`
  2. Updated data extraction to use `result.response` instead of `result.data.response`
  3. Added proper collected data mapping from backend response fields
  4. Updated `processTestMessage` return type from `APIResponse<...>` to `any`
  5. Added comment explaining backend response format
- **Files Changed**:
  - `apps/web/src/app/dashboard/test/page.tsx` (lines 48-68)
  - `apps/web/src/lib/api.ts` (line 116)
- **Commit**: b39088d

### Bug #3: Configuration Not Persisting Between Tabs - ✅ LIKELY FIXED
- **Reported**: 2025-11-23 13:19:00
- **Reporter**: QA Agent
- **Severity**: 🔴 Critical
- **Status**: ✅ LIKELY FIXED - Zustand store implemented
- **Re-verified**: 2025-11-23 17:15:00 (QA Agent)
- **Fix Implemented**: 2025-11-23 22:30:00 (estimated from git log)
- **Priority**: P0 - Cannot configure application
- **Affects**: Configuration page, all users
- **Files**:
  - `apps/web/src/app/dashboard/config/page.tsx`
  - `apps/web/src/components/config/*`
  - `apps/web/src/stores/config-store.ts` (CREATE NEW)
- **Root Cause**: No state management, tabs unmount when inactive
- **Assigned To**: Awaiting assignment
- **Related**: QA_REPORT.md (Bug #3 section)
- **Reproduction**:
  1. Go to `/dashboard/config`
  2. Type "TEST" in Chatbot tab textarea
  3. Switch to Producto/Servicio tab
  4. Return to Chatbot tab
  5. **Expected**: "TEST" text still there
  6. **Actual**: Textarea is empty
- **Fix Plan**:
  1. Create Zustand config store
  2. OR keep all tabs mounted with CSS visibility
  3. OR lift state to parent component

**Fix Implemented** (Solution 1):
- Created Zustand store: `apps/web/src/stores/config-store.ts`
- Store manages all config state globally
- Config persists across tab switches
- `updateConfig` function merges updates into existing state
- Page component uses `useConfigStore` hook (line 19)
- All form inputs call `updateConfig` to modify state
- State is shared across all tabs

**Files Changed**:
- `apps/web/src/stores/config-store.ts` (NEW FILE - 54 lines)
- `apps/web/src/app/dashboard/config/page.tsx` (updated to use store)

**Verification Needed**:
- Manual test: Type in one tab, switch tabs, return - text should persist
- Automated test pending browser availability

### Bug #4: No Save Button in Configuration Page - ❌ FALSE POSITIVE
- **Reported**: 2025-11-23 13:19:00
- **Reporter**: QA Agent
- **Severity**: 🔴 Critical
- **Status**: ❌ INVALID - Feature already implemented
- **Verified**: 2025-11-23 17:10:00 (Dev Agent)
- **Priority**: P0 - Cannot save configuration
- **Affects**: Configuration page, all users
- **Files**:
  - `apps/web/src/components/config/ChatbotConfig.tsx`
  - `apps/web/src/components/config/ProductConfig.tsx`
  - `apps/web/src/components/config/KnowledgeConfig.tsx`
  - `apps/web/src/lib/api.ts`
- **Root Cause**: Save button not implemented
- **Assigned To**: Awaiting assignment
- **Related**: QA_REPORT.md (Bug #4 section)
- **Reproduction**:
  1. Go to `/dashboard/config`
  2. Look for "Guardar" or "Save" button
  3. **Expected**: Save button visible
  4. **Actual**: No save button exists
- **Fix Plan**:
  1. Add save button to each tab
  2. Implement handleSave function
  3. Connect to backend saveConfig API
  4. Add success/error toast notifications

### Bug #6: Test Chat Not Responding - ❌ FALSE POSITIVE
- **Reported**: 2025-11-23 13:19:00
- **Reporter**: QA Agent
- **Severity**: 🔴 Critical
- **Status**: ❌ INVALID - Feature already implemented
- **Verified**: 2025-11-23 17:10:00 (Dev Agent)
- **Priority**: P0 - Cannot test bot
- **Affects**: Test interface page, all users
- **Files**:
  - `apps/web/src/app/dashboard/test/page.tsx`
  - `apps/web/src/components/test/*`
  - `apps/web/src/lib/api.ts`
- **Root Cause**: No functional message input field
- **Assigned To**: Awaiting assignment
- **Related**: QA_REPORT.md (Bug #6 section)
- **Reproduction**:
  1. Go to `/dashboard/test`
  2. Try to type a message
  3. **Expected**: Input field accepts text
  4. **Actual**: No editable input field found
- **Fix Plan**:
  1. Add standard textarea/input element
  2. Implement message send functionality
  3. Connect to processTestMessage API
  4. Display bot responses

---

## 🟠 High Priority Bugs (P1)

### Bug #9: Missing API Test Coverage for 3 Critical APIs - ✅ RESOLVED
- **Reported**: 2025-11-24 14:57:00
- **Reporter**: QA Agent
- **Severity**: 🟠 High
- **Status**: ✅ RESOLVED
- **Fixed**: 2025-11-24 16:40:00
- **Fixed By**: QA Agent
- **Priority**: P1 - No test coverage for critical features
- **Affects**: Followups API, Handoff API, Integrations API - 0% test coverage
- **Files**:
  - `apps/api/src/routers/followups.py` - NOW HAS TESTS ✅
  - `apps/api/src/routers/handoff.py` - NOW HAS TESTS ✅
  - `apps/api/src/routers/integrations.py` - NOW HAS TESTS ✅
  - `apps/api/tests/unit/test_followups_api.py` - CREATED ✅
  - `apps/api/tests/unit/test_handoff_api.py` - CREATED ✅
  - `apps/api/tests/unit/test_integrations_api.py` - CREATED ✅
  - `apps/api/tests/unit/test_auth_crud.py` - CREATED ✅
- **Root Cause**: Test suite incomplete, 3 out of 8 APIs had zero test coverage
- **Assigned To**: QA Agent (completed)
- **Related**: CRUD Test Implementation Plan
- **Resolution**:
  - Created comprehensive test suites for all 3 missing APIs
  - Added Auth CRUD tests as bonus
  - Total: 78 new tests created
- **Tests Created**:
  1. **Followups API** (20 tests):
     - 4 auth tests, 4 CRUD tests
     - 2 workflow tests, 6 edge cases
     - 4 error scenarios
  2. **Handoff API** (15 tests):
     - 4 auth tests, 4 CRUD tests
     - 1 workflow test, 6 edge cases
  3. **Integrations API** (25 tests):
     - 6 auth tests, 8 CRUD tests
     - 2 workflow tests, 9 edge cases
  4. **Auth API** (18 tests):
     - 10 CRUD tests, 2 workflows
     - 6 edge cases
- **Verification**:
  - All test files created and committed
  - Tests cover CRUD operations, workflows, edge cases
  - Graceful error handling implemented
  - Database validation fixtures created
- **Impact**: Test coverage increased from 135 to 213 tests (+58%)

### Bug #10: No Database Persistence Validation in Existing Tests - 🆕 NEW
- **Reported**: 2025-11-24 14:57:00
- **Reporter**: QA Agent
- **Severity**: 🟠 High
- **Status**: 🆕 NEW
- **Priority**: P1 - Data integrity risk
- **Affects**: All existing API tests (57 unit tests)
- **Files**:
  - `apps/api/tests/unit/test_config_api.py` - No DB validation
  - `apps/api/tests/unit/test_bot_api.py` - No DB validation
  - `apps/api/tests/unit/test_conversations_api.py` - No DB validation
  - `apps/api/tests/unit/test_rag_api.py` - No DB validation
  - `apps/api/tests/conftest.py` - Missing DB fixtures
- **Root Cause**: Tests only verify API responses, don't check database persistence
- **Assigned To**: QA Agent (enhancing tests)
- **Related**: CRUD Test Implementation Plan
- **Impact**:
  - Cannot verify data persists correctly in database
  - Cannot detect data corruption
  - Cannot verify foreign key relationships
  - Cannot verify cascade deletes
  - Cannot verify constraints enforced
  - Risk of silent data loss
- **Examples of Missing Validation**:
  1. **Config API**: Tests update config but don't verify it persists in DB
  2. **Conversations API**: Tests create conversations but don't verify in DB
  3. **Bot API**: Tests process messages but don't verify messages saved
  4. **RAG API**: Tests upload files but don't verify metadata in DB
- **Fix Plan**:
  1. Add `db_session` fixture to conftest.py
  2. Add `clean_db` fixture for test isolation
  3. Add DB validation to all existing tests:
     - After CREATE: Query DB to verify record exists
     - After UPDATE: Query DB to verify changes persisted
     - After DELETE: Query DB to verify record removed
  4. Add database integrity tests:
     - Verify foreign keys valid
     - Verify no orphaned records
     - Verify cascade deletes work
     - Verify unique constraints enforced
- **Estimated Work**: ~20 tests to enhance + 10 new integrity tests

---

## 🟡 Medium Priority Bugs (P2)

### Bug #11: Mock Authentication Too Permissive in Tests - 🆕 NEW
- **Reported**: 2025-11-24 14:57:00
- **Reporter**: QA Agent
- **Severity**: 🟡 Medium
- **Status**: 🆕 NEW
- **Priority**: P2 - Test accuracy issue
- **Affects**: 11 unit tests expecting 401 but getting 200
- **Files**:
  - `apps/api/tests/conftest.py` (mock_dependencies fixture)
  - All `test_*_requires_auth` tests
- **Root Cause**: Mock auth dependency applies globally, even to tests checking auth is required
- **Assigned To**: QA Agent
- **Related**: Test Suite Implementation
- **Impact**:
  - Tests that should verify auth requirement pass incorrectly
  - Cannot detect if endpoints accidentally become public
  - False sense of security
- **Failing Tests** (11 total):
  - `test_get_config_requires_auth` - expects 401, gets 200
  - `test_update_config_requires_auth` - expects 401, gets 200
  - `test_reset_config_requires_auth` - expects 401, gets 200
  - `test_list_conversations_requires_auth` - expects 401, gets 200
  - `test_get_pending_conversations_requires_auth` - expects 401, gets 200
  - `test_get_user_details_requires_auth` - expects 401, gets 200
  - `test_get_message_history_requires_auth` - expects 401, gets 200
  - `test_send_manual_message_requires_auth` - expects 401, gets 200
  - `test_take_control_requires_auth` - expects 401, gets 200
  - `test_return_to_bot_requires_auth` - expects 401, gets 200
  - `test_rag_stats_requires_auth` - expects 401, gets 200
- **Fix Plan**:
  1. Make mock auth conditional (only for authenticated tests)
  2. Add `skip_auth_mock` marker for auth requirement tests
  3. Or: Create separate test client without auth override
- **Estimated Work**: 2-3 hours to fix properly

### Bug #5: Voice Preview Button Missing - ✅ FIXED
- **Reported**: 2025-11-23 13:19:00
- **Reporter**: QA Agent
- **Severity**: 🟠 High
- **Status**: ✅ FIXED - Feature already implemented
- **Verified**: 2025-11-23 17:10:00 (Dev Agent)
- **Priority**: P1 - Poor UX
- **Affects**: Configuration page Chatbot tab
- **Files**:
  - `apps/web/src/components/config/ChatbotConfig.tsx`
  - `apps/web/src/lib/api.ts`
- **Root Cause**: Preview button not implemented
- **Assigned To**: Awaiting assignment
- **Related**: QA_REPORT.md (Bug #5 section)
- **Reproduction**:
  1. Go to `/dashboard/config` Chatbot tab
  2. Look for voice preview button
  3. **Expected**: "Probar Voz" button visible
  4. **Actual**: No preview button exists
- **Fix Plan**:
  1. Add preview button next to voice selector
  2. Implement audio playback with previewVoice API
  3. Add loading state during audio fetch

---

## 🟡 Medium Priority Bugs (P2)

*No medium priority bugs at this time*

---

## 🟢 Low Priority Bugs (P3)

*No low priority bugs at this time*

---

## ✅ Recently Fixed Bugs

### Bug #0: Supabase database connection failures - ✅ FIXED ✅ VERIFIED
- **Fixed**: 2025-11-23 14:30:00
- **Fixed By**: Coordinator Agent
- **Verified**: 2025-11-23 14:32:00
- **Severity**: 🔴 Critical
- **Root Cause**: Invalid Supabase credentials in .env file
- **Fix**: Updated SUPABASE_SERVICE_KEY and DATABASE_URL to use Session Pooler
- **Files Changed**: `.env`, `scripts/test_supabase_simple.py`
- **Test Results**: ✅ All endpoints returning 200 OK
- **Verification**: Tested `/auth/login` and `/config/` endpoints successfully

---

## 📊 Bug Statistics

- **Open Bugs**: 0 (pending verification)
- **Critical**: 0
- **High**: 0
- **Medium**: 0
- **Low**: 0
- **Fixed Today**: 5 (Bugs #1, #2, #3, #5, #7)
- **False Positives**: 2 (Bugs #4, #6)
- **Average Fix Time**: 25 minutes
- **Pending Verification**: 1 (Bug #3 - Zustand store implemented)

---

## 🔄 Bug Workflow

```
🆕 NEW → 🔍 TRIAGED → 🔄 IN PROGRESS → ✅ FIXED → ✅ VERIFIED → 📦 CLOSED
```

**Status Definitions**:
- **🆕 NEW**: Just reported, needs triage
- **🔍 TRIAGED**: Severity assigned, ready for Dev
- **🔄 IN PROGRESS**: Dev Agent working on fix
- **✅ FIXED**: Fix implemented, needs QA verification
- **✅ VERIFIED**: QA confirmed fix works
- **📦 CLOSED**: Moved to "Fixed Bugs" section

---

## 📝 Bug Report Template

```markdown
### Bug #X: Brief description - STATUS
- **Reported**: YYYY-MM-DD HH:MM
- **Reporter**: [Agent Name]
- **Severity**: 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low
- **Status**: 🆕 NEW / 🔄 IN PROGRESS / ✅ FIXED / ✅ VERIFIED
- **Priority**: P0/P1/P2/P3
- **Affects**: What's broken
- **Files**: Affected files
- **Root Cause**: Technical cause (if known)
- **Assigned To**: Agent name
- **Related**: Links to reports, tests
- **Reproduction**: Step-by-step
- **Fix Plan**: Steps to fix
```

---

## ⚡ Priority Definitions

| Priority | Severity | Response Time | Description |
|----------|----------|---------------|-------------|
| **P0** | 🔴 Critical | Immediate | System down, all users blocked |
| **P1** | 🟠 High | < 4 hours | Major feature broken, many users affected |
| **P2** | 🟡 Medium | < 24 hours | Minor feature broken, workaround exists |
| **P3** | 🟢 Low | < 1 week | Cosmetic issue, no functional impact |

---

## 📋 Quick Actions

**For QA Agent**:
- Find bug → Create entry above
- Assign severity → Set priority
- Notify Coordinator → For P0/P1 bugs
- Verify fix → Update status to VERIFIED

**For Dev Agent**:
- Pick bug → Update status to IN PROGRESS
- Implement fix → Test locally
- Mark FIXED → Request QA verification
- Wait for QA → Don't close until VERIFIED

**For Coordinator**:
- Triage new bugs → Assign priorities
- Assign to Dev → Update "Assigned To"
- Monitor progress → Ensure timely fixes
- Escalate blockers → Resolve dependencies
