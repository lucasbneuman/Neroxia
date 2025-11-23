# 📝 Test Cases - WhatsApp Sales Bot Frontend

**Project**: WhatsApp Sales Bot SaaS  
**Version**: 2.0.0 (Microservices)  
**Last Updated**: 2025-11-23  
**Branch**: saas-migration

---

## 📋 Table of Contents

1. [Authentication Test Cases](#authentication-test-cases)
2. [Dashboard Test Cases](#dashboard-test-cases)
3. [Chat Interface Test Cases](#chat-interface-test-cases)
4. [Configuration Test Cases](#configuration-test-cases)
5. [Test Interface Test Cases](#test-interface-test-cases)
6. [API Integration Test Cases](#api-integration-test-cases)
7. [UI/UX Test Cases](#uiux-test-cases)
8. [Performance Test Cases](#performance-test-cases)
9. [Security Test Cases](#security-test-cases)

---

## 🔐 Authentication Test Cases

### TC-AUTH-001: Successful Login with Valid Credentials
**Priority**: P0 (Critical)  
**Status**: ❌ BLOCKED (Bug #1)

**Preconditions**:
- User account exists in Supabase
- User is not already logged in
- Frontend is running on localhost:3000

**Test Steps**:
1. Navigate to `http://localhost:3000/login`
2. Enter valid email: `automationinnova640@gmail.com`
3. Enter valid password: `;automation.innova$864`
4. Click "Sign In" button

**Expected Results**:
- User is authenticated successfully
- User is redirected to `/dashboard`
- Session token is stored
- No errors in console

**Actual Results**: ❌ FAILED - Hydration error occurs

---

### TC-AUTH-002: Failed Login with Invalid Email
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/login`
2. Enter invalid email: `invalid@example.com`
3. Enter any password
4. Click "Sign In"

**Expected Results**:
- Error message: "Invalid email or password"
- User remains on login page
- No redirect occurs

---

### TC-AUTH-003: Failed Login with Invalid Password
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/login`
2. Enter valid email: `automationinnova640@gmail.com`
3. Enter invalid password: `wrongpassword`
4. Click "Sign In"

**Expected Results**:
- Error message: "Invalid email or password"
- User remains on login page

---

### TC-AUTH-004: Email Field Validation
**Priority**: P2  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/login`
2. Enter invalid email format: `notanemail`
3. Try to submit form

**Expected Results**:
- Client-side validation error
- Message: "Please enter a valid email"
- Form does not submit

---

### TC-AUTH-005: Password Field Validation
**Priority**: P2  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/login`
2. Leave password field empty
3. Try to submit form

**Expected Results**:
- Validation error: "Password is required"
- Form does not submit

---

### TC-AUTH-006: Sign Up Flow
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/login`
2. Click "Sign Up" link
3. Fill in registration form
4. Submit

**Expected Results**:
- User is registered in Supabase
- Confirmation email sent (if configured)
- User is redirected to dashboard or email confirmation page

---

### TC-AUTH-007: Logout Functionality
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Log in successfully
2. Navigate to dashboard
3. Click logout button

**Expected Results**:
- Session is cleared
- User is redirected to `/login`
- Cannot access protected routes

---

### TC-AUTH-008: Session Persistence
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Log in successfully
2. Close browser tab
3. Reopen `http://localhost:3000`

**Expected Results**:
- User remains logged in
- Redirected to dashboard
- Session is still valid

---

### TC-AUTH-009: Protected Route Access (Unauthenticated)
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Ensure user is logged out
2. Try to access `/dashboard` directly

**Expected Results**:
- User is redirected to `/login`
- Error message: "Please log in to continue"

---

### TC-AUTH-010: Password Reset Flow
**Priority**: P2  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/login`
2. Click "Forgot Password" link (if exists)
3. Enter email
4. Submit

**Expected Results**:
- Password reset email sent
- Confirmation message shown
- User can reset password via email link

---

## 📊 Dashboard Test Cases

### TC-DASH-001: Dashboard Loads Successfully
**Priority**: P0  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Log in successfully
2. Verify redirect to `/dashboard`

**Expected Results**:
- Dashboard page loads
- Statistics are displayed
- Navigation menu is visible
- No console errors

---

### TC-DASH-002: Display Conversation Statistics
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to dashboard
2. Verify statistics display

**Expected Results**:
- Total conversations count
- Active conversations count
- Conversion rate
- Average response time
- Data is fetched from API

---

### TC-DASH-003: Navigation to Chats
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. From dashboard, click "Chats" menu item

**Expected Results**:
- Redirected to `/chats`
- Chat interface loads

---

### TC-DASH-004: Navigation to Configuration
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. From dashboard, click "Configuration" menu item

**Expected Results**:
- Redirected to `/config`
- Configuration panel loads

---

### TC-DASH-005: Navigation to Test Interface
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. From dashboard, click "Test" menu item

**Expected Results**:
- Redirected to `/test`
- Test interface loads

---

## 💬 Chat Interface Test Cases

### TC-CHAT-001: Load Conversation List
**Priority**: P0  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/chats`
2. Verify conversation list loads

**Expected Results**:
- List of conversations displayed
- Each conversation shows:
  - Phone number
  - Last message
  - Timestamp
  - Stage (welcome, qualifying, etc.)
  - Intent score

---

### TC-CHAT-002: Select Conversation
**Priority**: P0  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/chats`
2. Click on a conversation from list

**Expected Results**:
- Conversation details load
- Message history displayed
- Input field available

---

### TC-CHAT-003: View Message History
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Select a conversation
2. Scroll through message history

**Expected Results**:
- All messages displayed in chronological order
- User messages aligned right
- Bot messages aligned left
- Timestamps shown
- Audio messages have play button (if applicable)

---

### TC-CHAT-004: Send Message (Manual Mode)
**Priority**: P0  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Select a conversation
2. Type message in input field
3. Click send button

**Expected Results**:
- Message sent to API
- Message appears in chat
- Bot response received (if auto-reply enabled)

---

### TC-CHAT-005: Human Handoff Control
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Select a conversation
2. Click "Take Over" button

**Expected Results**:
- Conversation switches to manual mode
- Bot auto-reply disabled
- Human agent can send messages
- Visual indicator shows manual mode

---

### TC-CHAT-006: Return to Bot Control
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. In manual mode conversation
2. Click "Return to Bot" button

**Expected Results**:
- Conversation switches back to bot mode
- Bot resumes auto-reply
- Visual indicator shows bot mode

---

### TC-CHAT-007: Filter Conversations by Stage
**Priority**: P2  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/chats`
2. Select filter: "Closing" stage

**Expected Results**:
- Only conversations in "closing" stage shown
- Count updates

---

### TC-CHAT-008: Search Conversations
**Priority**: P2  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/chats`
2. Enter phone number in search field

**Expected Results**:
- Matching conversations displayed
- Search is case-insensitive

---

### TC-CHAT-009: Real-time Message Updates
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Open conversation in browser
2. Send message via Twilio (external)
3. Verify message appears in UI

**Expected Results**:
- New message appears without refresh
- Notification shown (if implemented)

---

### TC-CHAT-010: Display Customer Data
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Select a conversation
2. View customer data panel

**Expected Results**:
- Customer name displayed
- Email displayed
- Phone number displayed
- Needs/pain points shown
- Budget information shown
- Data extracted by bot

---

## ⚙️ Configuration Test Cases

### TC-CONFIG-001: Load Configuration Panel
**Priority**: P0  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/config`

**Expected Results**:
- Configuration panel loads
- All settings displayed
- Current values shown

---

### TC-CONFIG-002: Update System Prompt
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/config`
2. Modify system prompt text
3. Click "Save"

**Expected Results**:
- Configuration saved to database
- Success message shown
- New prompt used in future conversations

---

### TC-CONFIG-003: Update Product Information
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/config`
2. Modify product info
3. Click "Save"

**Expected Results**:
- Configuration saved
- Bot uses new product info in responses

---

### TC-CONFIG-004: Configure TTS Settings
**Priority**: P2  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/config`
2. Change TTS voice (e.g., "alloy" to "nova")
3. Adjust TTS ratio slider (0-100)
4. Click "Save"

**Expected Results**:
- Settings saved
- New voice used in audio messages
- Ratio controls audio vs text percentage

---

### TC-CONFIG-005: Upload RAG Document
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/config`
2. Go to RAG section
3. Click "Upload Document"
4. Select PDF/TXT file
5. Submit

**Expected Results**:
- File uploaded to server
- Document processed and chunked
- Embeddings created in ChromaDB
- Document appears in list

---

### TC-CONFIG-006: Delete RAG Document
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to RAG documents list
2. Click delete on a document
3. Confirm deletion

**Expected Results**:
- Document removed from database
- Embeddings removed from ChromaDB
- Document no longer in list

---

### TC-CONFIG-007: Configure Twilio Integration
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/config`
2. Go to Integrations section
3. Enter Twilio credentials
4. Click "Save"

**Expected Results**:
- Credentials saved to database
- Connection tested
- Success/error message shown

---

### TC-CONFIG-008: Configure HubSpot Integration
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/config`
2. Go to Integrations section
3. Enter HubSpot access token
4. Click "Save"

**Expected Results**:
- Token saved to database
- Connection tested
- Success/error message shown

---

### TC-CONFIG-009: Test Configuration Changes
**Priority**: P2  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Update any configuration
2. Go to `/test` interface
3. Send test message

**Expected Results**:
- New configuration applied
- Bot behavior reflects changes

---

## 🧪 Test Interface Test Cases

### TC-TEST-001: Load Test Interface
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/test`

**Expected Results**:
- Test interface loads
- Input field available
- Send button visible

---

### TC-TEST-002: Send Test Message
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate to `/test`
2. Enter test message
3. Click "Send"

**Expected Results**:
- Message sent to bot engine
- Bot response received
- Conversation flow simulated
- No actual WhatsApp message sent

---

### TC-TEST-003: View Bot Workflow Steps
**Priority**: P2  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Send test message
2. View workflow visualization

**Expected Results**:
- Shows which nodes were executed
- Intent score displayed
- Sentiment displayed
- Data extraction results shown

---

### TC-TEST-004: Test Different Conversation Stages
**Priority**: P2  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Send messages to trigger different stages
2. Verify stage transitions

**Expected Results**:
- Welcome → Qualifying → Nurturing → Closing
- Stage changes reflected in UI

---

## 🔌 API Integration Test Cases

### TC-API-001: Authentication API
**Priority**: P0  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Call `POST /auth/login` with valid credentials

**Expected Results**:
- 200 OK response
- JWT token returned
- Token is valid for subsequent requests

---

### TC-API-002: Get Conversations
**Priority**: P0  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Call `GET /conversations` with auth token

**Expected Results**:
- 200 OK response
- Array of conversations returned
- Each conversation has required fields

---

### TC-API-003: Get Single Conversation
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Call `GET /conversations/{id}` with valid ID

**Expected Results**:
- 200 OK response
- Conversation details returned
- Includes messages array

---

### TC-API-004: Send Bot Message
**Priority**: P0  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Call `POST /bot/message` with message data

**Expected Results**:
- 200 OK response
- Bot response returned
- Message saved to database

---

### TC-API-005: Update Configuration
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Call `PUT /config` with new settings

**Expected Results**:
- 200 OK response
- Configuration updated in database

---

### TC-API-006: Upload RAG Document
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Call `POST /rag/documents` with file

**Expected Results**:
- 200 OK response
- Document processed
- Document ID returned

---

### TC-API-007: Error Handling - Unauthorized
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Call any protected endpoint without auth token

**Expected Results**:
- 401 Unauthorized response
- Error message: "Authentication required"

---

### TC-API-008: Error Handling - Not Found
**Priority**: P2  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Call `GET /conversations/invalid-id`

**Expected Results**:
- 404 Not Found response
- Error message: "Conversation not found"

---

## 🎨 UI/UX Test Cases

### TC-UI-001: Responsive Design - Mobile
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Open app on mobile device (or DevTools mobile view)
2. Navigate through all pages

**Expected Results**:
- Layout adapts to mobile screen
- All elements accessible
- No horizontal scrolling
- Touch targets are adequate size

---

### TC-UI-002: Responsive Design - Tablet
**Priority**: P2  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Open app on tablet (or DevTools tablet view)
2. Navigate through all pages

**Expected Results**:
- Layout optimized for tablet
- Good use of screen space

---

### TC-UI-003: Responsive Design - Desktop
**Priority**: P1  
**Status**: ✅ PARTIAL (Login page only)

**Test Steps**:
1. Open app on desktop browser
2. Navigate through all pages

**Expected Results**:
- Layout optimized for desktop
- Sidebar navigation visible
- Multi-column layouts where appropriate

---

### TC-UI-004: Color Scheme Consistency
**Priority**: P2  
**Status**: ✅ PASSED (Login page)

**Test Steps**:
1. Review all pages
2. Verify color scheme

**Expected Results**:
- Minimalist black and white design
- Consistent across all pages
- Good contrast for readability

---

### TC-UI-005: Loading States
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Trigger actions that require API calls
2. Observe loading indicators

**Expected Results**:
- Loading spinners shown
- Buttons disabled during loading
- No UI freeze

---

### TC-UI-006: Error Messages
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Trigger various errors
2. Verify error messages

**Expected Results**:
- Clear, user-friendly error messages
- Errors are dismissible
- Errors don't crash the app

---

### TC-UI-007: Success Notifications
**Priority**: P2  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Perform successful actions (save config, send message)
2. Verify notifications

**Expected Results**:
- Success messages shown
- Auto-dismiss after few seconds
- Non-intrusive

---

### TC-UI-008: Keyboard Navigation
**Priority**: P2  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Navigate app using only keyboard
2. Use Tab, Enter, Escape keys

**Expected Results**:
- All interactive elements accessible
- Logical tab order
- Focus indicators visible

---

### TC-UI-009: Accessibility - Screen Reader
**Priority**: P2  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Use screen reader (NVDA, JAWS, VoiceOver)
2. Navigate through app

**Expected Results**:
- All content readable
- Proper ARIA labels
- Semantic HTML used

---

### TC-UI-010: Browser Compatibility
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Test in Chrome, Firefox, Edge, Safari

**Expected Results**:
- Consistent behavior across browsers
- No browser-specific bugs

---

## ⚡ Performance Test Cases

### TC-PERF-001: Page Load Time
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Measure time to interactive for each page

**Expected Results**:
- Login page: < 2 seconds
- Dashboard: < 3 seconds
- Chat interface: < 3 seconds

---

### TC-PERF-002: API Response Time
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Measure API response times

**Expected Results**:
- GET requests: < 500ms
- POST requests: < 1000ms
- Bot responses: < 5000ms (depends on OpenAI)

---

### TC-PERF-003: Bundle Size
**Priority**: P2  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Check Next.js build output
2. Analyze bundle size

**Expected Results**:
- Main bundle: < 500KB
- Total page size: < 2MB
- Code splitting implemented

---

### TC-PERF-004: Memory Usage
**Priority**: P2  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Monitor memory usage during extended use
2. Check for memory leaks

**Expected Results**:
- No significant memory growth
- No memory leaks

---

## 🔒 Security Test Cases

### TC-SEC-001: SQL Injection Protection
**Priority**: P0  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Attempt SQL injection in input fields
2. Example: `' OR '1'='1`

**Expected Results**:
- Input sanitized
- No SQL injection possible
- Error handled gracefully

---

### TC-SEC-002: XSS Protection
**Priority**: P0  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Attempt XSS in message fields
2. Example: `<script>alert('XSS')</script>`

**Expected Results**:
- Script tags escaped
- No script execution
- Content displayed as text

---

### TC-SEC-003: CSRF Protection
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Verify CSRF tokens on forms
2. Attempt cross-site request

**Expected Results**:
- CSRF tokens validated
- Unauthorized requests rejected

---

### TC-SEC-004: Authentication Token Security
**Priority**: P0  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Inspect token storage
2. Verify token expiration

**Expected Results**:
- Tokens stored securely (httpOnly cookies or secure storage)
- Tokens expire appropriately
- Refresh token mechanism works

---

### TC-SEC-005: API Rate Limiting
**Priority**: P1  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Send multiple rapid requests to API

**Expected Results**:
- Rate limiting enforced
- 429 Too Many Requests response
- Retry-After header present

---

### TC-SEC-006: Sensitive Data Exposure
**Priority**: P0  
**Status**: ⏸️ BLOCKED

**Test Steps**:
1. Check network requests
2. Verify no sensitive data in URLs or logs

**Expected Results**:
- No passwords in URLs
- No API keys in client-side code
- No sensitive data in console logs

---

## 📊 Test Summary

### Total Test Cases: 80+

**By Priority**:
- P0 (Critical): 15
- P1 (High): 40
- P2 (Medium): 25+

**By Status**:
- ✅ Passed: 2
- ❌ Failed: 1
- ⏸️ Blocked: 77+

**By Category**:
- Authentication: 10
- Dashboard: 5
- Chat Interface: 10
- Configuration: 9
- Test Interface: 4
- API Integration: 8
- UI/UX: 10
- Performance: 4
- Security: 6

---

## 🔄 Test Execution Plan

### Phase 1: Fix Critical Bug
1. Fix Bug #1 (Hydration Error)
2. Re-run TC-AUTH-001

### Phase 2: Authentication Tests
1. Run all TC-AUTH-* tests
2. Verify login/logout flow

### Phase 3: Core Functionality
1. Run TC-DASH-* tests
2. Run TC-CHAT-* tests
3. Run TC-CONFIG-* tests

### Phase 4: Integration Tests
1. Run TC-API-* tests
2. Verify end-to-end flows

### Phase 5: Non-Functional Tests
1. Run TC-UI-* tests
2. Run TC-PERF-* tests
3. Run TC-SEC-* tests

---

**Document Version**: 1.0.0  
**Created**: 2025-11-23  
**Next Review**: After Bug #1 fix
