# 📋 BRF Requests (Brief de Requerimientos Funcionales)

**Purpose**: UX Agent requests backend changes from Dev Agent
**Last Updated**: 2025-11-24 00:53:00

---

## 🔄 Active BRF Requests

> **RULE**: UX Agent creates, Dev Agent implements, QA Agent verifies

### BRF #3: Fix Configuration Persistence - 🔴 CRITICAL
- **Created**: 2025-11-24 00:53
- **Requested By**: UX Agent
- **Assigned To**: Dev Agent (awaiting assignment)
- **Priority**: 🔴 Critical
- **Status**: 🆕 NEW
- **Estimated Effort**: M (Medium - 2-3 hours)

**User Story**:
As a user, I want my configuration changes to be saved and persist across page navigations so that I don't have to re-enter my settings every time.

**Problem Statement**:
1. Configuration save API returns 200 but doesn't actually save the data
2. When navigating between tabs, configuration reverts to default/old values
3. Users cannot persist their chatbot settings

**Current Behavior**:
- User fills out configuration form
- Clicks "Guardar Configuración"
- API responds with 200 OK
- Configuration appears saved momentarily
- Upon navigating to another tab and back, configuration is lost

**Expected Behavior**:
- Configuration should be saved to database
- Configuration should persist across page navigations
- Configuration should be loaded correctly on page mount

**API Requirements**:
- Endpoint: `POST /api/config/save` (already exists)
- Fix: Ensure data is actually written to database
- Verify: Configuration can be retrieved with `GET /api/config`

**Frontend Impact**:
- Frontend already implements correct save/load logic
- No frontend changes needed once backend is fixed

**Acceptance Criteria**:
- [ ] Configuration save actually writes to database
- [ ] Configuration persists after page refresh
- [ ] Configuration persists when navigating between tabs
- [ ] GET /api/config returns the most recently saved configuration

**Dependencies**:
- Blocks: User configuration workflow
- Related: BRF #4 (Login issues)

**Notes**:
- This is CRITICAL for MVP launch
- Users cannot use the application without being able to save config
- Frontend implementation is correct, issue is backend-only

---

### BRF #4: Fix Login Authentication - 🔴 CRITICAL
- **Created**: 2025-11-24 00:53
- **Requested By**: UX Agent
- **Assigned To**: Dev Agent (awaiting assignment)
- **Priority**: 🔴 Critical
- **Status**: 🆕 NEW
- **Estimated Effort**: S (Small - 1-2 hours)

**User Story**:
As a user, I want to be able to log in with valid credentials so that I can access the dashboard.

**Problem Statement**:
Login endpoint is not working correctly. Users cannot authenticate even with correct credentials.

**Current Behavior**:
- User enters email: `admin@example.com`
- User enters password: `admin`
- Clicks "Iniciar Sesión"
- API returns error
- Toast notification shows: "Error al iniciar sesión. Por favor, intenta de nuevo."

**Expected Behavior**:
- User enters valid credentials
- API validates credentials
- API returns access token
- User is redirected to dashboard

**API Requirements**:
- Endpoint: `POST /api/auth/login` (already exists)
- Fix: Ensure authentication logic works correctly
- Verify: Valid credentials return access token

**Frontend Impact**:
- Frontend already implements correct login logic
- No frontend changes needed once backend is fixed

**Acceptance Criteria**:
- [ ] Login with valid credentials returns access token
- [ ] Access token can be used to access protected routes
- [ ] Invalid credentials return appropriate error message
- [ ] Error handling is clear and user-friendly

**Dependencies**:
- Blocks: All dashboard functionality
- Related: Cannot test BRF #3 without working login

**Notes**:
- This is CRITICAL for MVP launch
- Users cannot access the application at all
- Frontend implementation is correct, issue is backend-only
- Verify database has test user with credentials: admin@example.com / admin

---

### BRF #1: Sales Oracle Branding Assets API - 🆕 NEW
- **Created**: 2025-11-23 21:56
- **Requested By**: UX Agent
- **Assigned To**: Dev Agent (awaiting assignment)
- **Priority**: 🟢 Low
- **Status**: 🆕 NEW
- **Estimated Effort**: S (Small - 1-2 hours)

**User Story**:
As a frontend developer, I want a centralized API to fetch branding assets so that I can dynamically load the Sales Oracle logo and brand colors.

**Problem Statement**:
Currently, branding is hardcoded in the frontend. For future white-labeling or brand updates, we need a centralized way to manage brand assets.

**Proposed Solution**:
Create an API endpoint that serves Sales Oracle branding assets including logos and color schemes.

**Frontend Impact**:
- Dashboard layout will fetch and display logo dynamically
- Login page will use brand colors from API
- Easier to update branding across all instances

**API Requirements**:
- Endpoint: `GET /api/branding/assets`
- Request Body: None (GET request)
- Response:
  ```json
  {
    "logo": {
      "full": "/assets/sales-oracle-logo.svg",
      "icon": "/assets/sales-oracle-icon.svg",
      "wordmark": "/assets/sales-oracle-wordmark.svg"
    },
    "colors": {
      "accent": "#8B5CF6",
      "accentHover": "#7C3AED"
    }
  }
  ```
- Status Codes: 200 (success), 500 (server error)
- Authentication: Not Required (public endpoint)

**Database Changes** (if needed):
- None required (can serve static files)

**Acceptance Criteria**:
- [ ] API endpoint created and returns brand assets
- [ ] Static assets directory created at `apps/api/static/branding/`
- [ ] Frontend can consume API successfully
- [ ] Documentation updated

**Dependencies**:
- Blocks: None (optional enhancement)
- Related: Sales Oracle UI Redesign

**Notes**:
- This is OPTIONAL for initial launch
- Can use text-based branding for now
- Implement only if time permits
- Low priority enhancement

---

### BRF #2: User Theme Preferences API - 🆕 NEW
- **Created**: 2025-11-23 21:56
- **Requested By**: UX Agent
- **Assigned To**: Dev Agent (awaiting assignment)
- **Priority**: 🟢 Low
- **Status**: 🆕 NEW
- **Estimated Effort**: M (Medium - 2-3 hours)

**User Story**:
As a user, I want my theme preferences saved so that my chosen theme persists across sessions.

**Problem Statement**:
Future dark mode support will need backend storage for user preferences.

**Proposed Solution**:
Create API endpoints to save and retrieve user theme preferences.

**Frontend Impact**:
- Theme toggle component will save preferences
- Preferences will persist across browser sessions
- Better UX for returning users

**API Requirements**:
- Endpoint 1: `GET /api/user/preferences`
  - Response:
    ```json
    {
      "theme": "light",
      "accentColor": "#8B5CF6",
      "fontSize": "medium"
    }
    ```
- Endpoint 2: `PUT /api/user/preferences`
  - Request Body:
    ```json
    {
      "theme": "light" | "dark",
      "accentColor": "#8B5CF6",
      "fontSize": "small" | "medium" | "large"
    }
    ```
  - Response: `{ "success": true }`
- Status Codes: 200, 400, 401, 500
- Authentication: Required

**Database Changes** (if needed):
- New table: `user_preferences` or add columns to existing `users` table
- Columns: `theme`, `accent_color`, `font_size`

**Acceptance Criteria**:
- [ ] GET endpoint returns user preferences
- [ ] PUT endpoint saves preferences
- [ ] Preferences persist across sessions
- [ ] Error handling for invalid values
- [ ] Documentation updated

**Dependencies**:
- Blocks: Dark mode feature (future)
- Related: Sales Oracle UI Redesign

**Notes**:
- NOT required for initial Sales Oracle launch
- Future enhancement for v2.0
- Very low priority

---

## ✅ Completed BRF Requests

*No completed BRF requests yet*

---

## 📝 BRF Request Template

```markdown
### BRF #X: Brief Title - STATUS
- **Created**: YYYY-MM-DD HH:MM
- **Requested By**: UX Agent
- **Assigned To**: Dev Agent (or awaiting assignment)
- **Priority**: 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low
- **Status**: 🆕 NEW / 🔄 IN PROGRESS / ✅ IMPLEMENTED / ✅ VERIFIED
- **Estimated Effort**: S / M / L / XL (Small/Medium/Large/Extra Large)

**User Story**:
As a [user type], I want [goal] so that [benefit].

**Problem Statement**:
[Brief description of the UX issue or limitation]

**Proposed Solution**:
[What you want the backend to do]

**Frontend Impact**:
[What the UX Agent will implement on frontend once backend is ready]

**API Requirements**:
- Endpoint: `[METHOD] /path/to/endpoint`
- Request Body:
  ```json
  {
    "field": "value"
  }
  ```
- Response:
  ```json
  {
    "data": "value"
  }
  ```
- Status Codes: 200, 400, 500
- Authentication: Required / Not Required

**Database Changes** (if needed):
- New tables: [list]
- New columns: [list]
- Migrations: [description]

**Acceptance Criteria**:
- [ ] API endpoint created and tested
- [ ] Frontend can consume API successfully
- [ ] Error handling implemented
- [ ] Documentation updated
- [ ] QA verified

**Dependencies**:
- Blocks: [UX task in TASK_LOG.md]
- Related: [other BRFs or bugs]

**Notes**:
[Any additional context, edge cases, or considerations]
```

---

## 💡 BRF Workflow

```
1. UX Agent identifies need for backend change
2. UX Agent creates BRF request (above template)
3. UX Agent adds to Active BRF Requests section
4. UX Agent notifies Coordinator (optional for P0/P1)
5. Dev Agent picks BRF from Active section
6. Dev Agent updates status to IN PROGRESS
7. Dev Agent implements backend changes
8. Dev Agent updates status to IMPLEMENTED
9. Dev Agent notifies UX Agent
10. UX Agent implements frontend changes
11. UX Agent requests QA verification
12. QA Agent verifies end-to-end
13. QA Agent updates status to VERIFIED
14. Move BRF to Completed section
```

---

## ⚡ Priority Guidelines for BRFs

| Priority | Definition | Response Time |
|----------|------------|---------------|
| 🔴 **Critical** | Blocks critical UX feature, affects all users | < 4 hours |
| 🟠 **High** | Important UX improvement, affects many users | < 1 day |
| 🟡 **Medium** | Nice-to-have improvement, moderate impact | < 1 week |
| 🟢 **Low** | Minor enhancement, cosmetic improvement | < 2 weeks |

---

## 📏 Effort Estimation

| Size | Description | Typical Examples |
|------|-------------|------------------|
| **S** | < 2 hours | Simple CRUD endpoint, add single field |
| **M** | 2-4 hours | Multiple endpoints, moderate logic |
| **L** | 4-8 hours | Complex feature, database migrations |
| **XL** | > 8 hours | Major feature, architectural changes |

---

## 🎯 BRF Best Practices

### For UX Agent (Creating BRFs):
- ✅ Be specific about API requirements
- ✅ Include clear acceptance criteria
- ✅ Provide mockups or examples if helpful
- ✅ Think through edge cases
- ✅ Consider error handling
- ✅ Estimate priority realistically
- ❌ Don't create BRF for things you can do in frontend

### For Dev Agent (Implementing BRFs):
- ✅ Update status when starting
- ✅ Ask clarifying questions early
- ✅ Notify UX Agent when done
- ✅ Document API in code
- ✅ Test endpoints before marking complete
- ❌ Don't implement without understanding requirements
- ❌ Don't skip error handling

### For QA Agent (Verifying BRFs):
- ✅ Test both frontend and backend integration
- ✅ Verify acceptance criteria are met
- ✅ Test error scenarios
- ✅ Check responsive design (if applicable)
- ✅ Mark VERIFIED only when fully working
- ❌ Don't verify without end-to-end testing

---

## 📊 BRF Statistics

- **Active BRFs**: 2
- **In Progress**: 0
- **Completed Today**: 0
- **Average Implementation Time**: N/A

---

## 🔗 Related Files

- `.agents/TASK_LOG.md` - Track BRF implementation as tasks
- `.agents/BUG_TRACKER.md` - Link bugs if BRF fixes issues
- `.agents/AGENT_ROLES.md` - Reference UX and Dev agent roles
- `ARCHITECTURE.md` - Follow architectural guidelines
