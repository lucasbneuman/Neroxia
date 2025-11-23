# 📋 BRF Requests (Brief de Requerimientos Funcionales)

**Purpose**: UX Agent requests backend changes from Dev Agent
**Last Updated**: 2025-11-23 15:00:00

---

## 🔄 Active BRF Requests

> **RULE**: UX Agent creates, Dev Agent implements, QA Agent verifies

*No active BRF requests at this time*

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

- **Active BRFs**: 0
- **In Progress**: 0
- **Completed Today**: 0
- **Average Implementation Time**: N/A

---

## 🔗 Related Files

- `.agents/TASK_LOG.md` - Track BRF implementation as tasks
- `.agents/BUG_TRACKER.md` - Link bugs if BRF fixes issues
- `.agents/AGENT_ROLES.md` - Reference UX and Dev agent roles
- `ARCHITECTURE.md` - Follow architectural guidelines
