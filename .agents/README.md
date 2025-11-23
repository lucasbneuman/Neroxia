# 🤖 Agent Coordination System

**Version**: 1.0
**Purpose**: Orchestrate multiple AI agents working simultaneously
**Last Updated**: 2025-11-23

---

## 📁 File Structure

```
.agents/
├── README.md                 ← You are here
├── AGENT_PROTOCOL.md         ← HOW to work (workflow steps)
├── AGENT_ROLES.md            ← WHO does WHAT (responsibilities)
├── TASK_LOG.md               ← LIVE active tasks (current work)
├── BUG_TRACKER.md            ← LIVE bugs & fixes (issues)
└── BRF_REQUESTS.md           ← LIVE backend requests from UX (coordination)
```

---

## 🚀 Quick Start

### For New Agents

1. **Read this file first** ← You're doing it right!
2. **Read AGENT_PROTOCOL.md** → Learn the 4-step workflow
3. **Read AGENT_ROLES.md** → Understand your role
4. **Check TASK_LOG.md** → See what others are doing
5. **Check BUG_TRACKER.md** → See known issues
6. **Start working!** → Follow the protocol

### For Returning Agents

```bash
✅ Check TASK_LOG.md → Any conflicts?
✅ Check BUG_TRACKER.md → Any new bugs?
✅ Register your task → Update TASK_LOG.md
✅ Start work → Follow protocol
```

---

## 📋 File Purposes

### AGENT_PROTOCOL.md
- **What**: Standard 4-step workflow
- **When**: Before starting ANY work
- **Who**: ALL agents must follow
- **Format**: Step-by-step instructions

### AGENT_ROLES.md
- **What**: Role definitions & responsibilities
- **When**: When unclear about responsibilities
- **Who**: Reference for all agents
- **Format**: Role descriptions + interaction matrix

### TASK_LOG.md
- **What**: LIVE tracking of active work
- **When**: Update at start/end of every task
- **Who**: ALL agents read/write
- **Format**: Current tasks + recently completed
- **Update Frequency**: Real-time

### BUG_TRACKER.md
- **What**: LIVE bug tracking & fixes
- **When**: When bugs found or fixed
- **Who**: QA creates, Dev fixes, Coordinator triages
- **Format**: Bugs by priority + workflow status
- **Update Frequency**: Real-time

### BRF_REQUESTS.md
- **What**: LIVE backend requests from UX Agent
- **When**: UX needs backend changes (APIs, DB, features)
- **Who**: UX creates, Dev implements, QA verifies
- **Format**: BRF requests with API specs + acceptance criteria
- **Update Frequency**: Real-time

---

## 🔄 How Files Work Together

```mermaid
┌─────────────────┐
│  Agent starts   │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Read PROTOCOL   │  ← How to work
└────────┬────────┘
         ↓
┌─────────────────┐
│ Read ROLES      │  ← What's my job?
└────────┬────────┘
         ↓
┌─────────────────┐
│ Check TASK_LOG  │  ← What are others doing?
└────────┬────────┘
         ↓
┌─────────────────┐
│ Check BUG_TRACK │  ← Any known issues?
└────────┬────────┘
         ↓
┌─────────────────┐
│ Register task   │  ← Update TASK_LOG.md
└────────┬────────┘
         ↓
┌─────────────────┐
│ Do work         │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Update files    │  ← TASK_LOG, BUG_TRACKER
└────────┬────────┘
         ↓
┌─────────────────┐
│ Commit & done   │
└─────────────────┘
```

---

## 🎯 Key Principles

1. **READ FIRST** → Never start work without reading TASK_LOG.md
2. **ONE TASK** → One agent, one task at a time
3. **REGISTER ALWAYS** → Update TASK_LOG.md before starting
4. **COMMUNICATE** → Update status frequently
5. **VERIFY** → QA verifies all fixes
6. **DOCUMENT** → Everything gets recorded

---

## 🔍 Common Workflows

### QA Agent Finds Bug

```
1. Test feature
2. Find bug
3. Document in BUG_TRACKER.md
4. Assign severity (Critical/High/Medium/Low)
5. Notify Coordinator if P0/P1
6. Add to TASK_LOG.md if blocking
```

### Dev Agent Fixes Bug

```
1. Pick bug from BUG_TRACKER.md
2. Update bug status → IN PROGRESS
3. Register task in TASK_LOG.md
4. Implement fix
5. Update bug status → FIXED
6. Request QA verification
7. Mark task COMPLETED
```

### Coordinator Triages

```
1. Monitor TASK_LOG.md for conflicts
2. Review BUG_TRACKER.md for priorities
3. Assign bugs to Dev agents
4. Resolve blockers
5. Ensure protocol compliance
```

### UX Agent Improves Experience (Frontend Only)

```
1. Identify UX issue or improvement
2. Verify it's frontend-only (no backend needed)
3. Register task in TASK_LOG.md
4. Implement changes (CSS, components, layouts)
5. Test across devices/browsers
6. Request QA verification
7. Mark task COMPLETED
```

### UX Agent Needs Backend Changes

```
1. Identify UX improvement needing backend
2. Create BRF in BRF_REQUESTS.md with API specs
3. Register task in TASK_LOG.md as BLOCKED
4. Notify Coordinator if P0/P1
5. Wait for Dev Agent to implement BRF
6. Once Dev marks BRF IMPLEMENTED:
   - Implement frontend changes
   - Request QA end-to-end verification
7. Mark task COMPLETED
```

---

## ⚠️ Critical Rules

1. **NEVER** start without reading TASK_LOG.md
2. **ALWAYS** register before working
3. **ONE** task per agent maximum
4. **UPDATE** status in real-time
5. **VERIFY** all fixes with QA
6. **ESCALATE** if blocked > 30 minutes

---

## 📊 Success Metrics

- **Zero** task conflicts
- **< 30 min** average response to blockers
- **100%** protocol compliance
- **< 4 hours** fix time for P1 bugs
- **All** fixes verified by QA

---

## 🆘 Need Help?

- **Unclear workflow?** → Read AGENT_PROTOCOL.md
- **Unclear role?** → Read AGENT_ROLES.md
- **Task conflict?** → Escalate to Coordinator in TASK_LOG.md
- **Blocker?** → Mark ⏸️ BLOCKED in TASK_LOG.md
- **Bug found?** → Document in BUG_TRACKER.md

---

## 📝 Quick Reference

| Need | File | Section |
|------|------|---------|
| How to work | AGENT_PROTOCOL.md | 4-step workflow |
| My role | AGENT_ROLES.md | Your agent section |
| What's happening | TASK_LOG.md | Active tasks |
| Known issues | BUG_TRACKER.md | By priority |
| Report bug | BUG_TRACKER.md | Bug template |
| Register task | TASK_LOG.md | Task template |
| Request backend (UX) | BRF_REQUESTS.md | BRF template |
| Implement BRF (Dev) | BRF_REQUESTS.md | Active BRFs |

---

**Remember**: This system only works if ALL agents follow the protocol. You're part of a team! 🤝
