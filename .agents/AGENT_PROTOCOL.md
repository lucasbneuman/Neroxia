# 🤖 Agent Work Protocol

**Version**: 1.0
**Last Updated**: 2025-11-23

---

## 🔄 Standard Workflow

### STEP 1: READ (Before Anything)

```
✅ Read ARCHITECTURE.md → Understand structure & constraints
✅ Read .agents/TASK_LOG.md → Check active tasks
✅ Read .agents/BUG_TRACKER.md → Check known issues
✅ Verify no conflicts with other agents
```

### STEP 2: REGISTER (Start Work)

Update `.agents/TASK_LOG.md`:

```markdown
### [AGENT_TYPE] Task Name - 🔄 IN PROGRESS
- **Started**: YYYY-MM-DD HH:MM
- **Agent**: [Your Agent Type]
- **Files**: file1.ts, file2.py
- **Description**: Brief task description
```

### STEP 3: EXECUTE (Do Work)

- Follow ARCHITECTURE.md guidelines
- Make focused, atomic changes
- Document as you go
- Test your changes

### STEP 4: FINALIZE (Complete)

```
✅ Update .agents/TASK_LOG.md → Mark COMPLETED
✅ Update .agents/BUG_TRACKER.md → If fixing bugs
✅ Update ARCHITECTURE.md → If structural changes
✅ Commit with clear message
✅ Move task to WORK_LOG.md → For history
```

---

## 📋 File References

| File | Purpose |
|------|---------|
| `.agents/AGENT_PROTOCOL.md` | This file - How to work |
| `.agents/AGENT_ROLES.md` | Role definitions & responsibilities |
| `.agents/TASK_LOG.md` | Active tasks (live state) |
| `.agents/BUG_TRACKER.md` | Bugs & fixes (live state) |
| `WORK_LOG.md` | Historical completed work |
| `ARCHITECTURE.md` | System design & constraints |

---

## 🚨 Critical Rules

1. **NEVER** start work without reading TASK_LOG.md
2. **ALWAYS** register before executing
3. **ONE** task per agent at a time
4. **COMMIT** frequently with clear messages
5. **DOCUMENT** all structural changes

---

## 💡 Best Practices

- Keep tasks small and focused (< 2 hours)
- Update status frequently
- If blocked, mark task as ⏸️ BLOCKED immediately
- Communicate blockers in TASK_LOG.md
- Reference related files/bugs in your task entry

---

## 🎯 Success Criteria

- ✅ All files updated before starting
- ✅ Task registered in TASK_LOG.md
- ✅ Work completed and tested
- ✅ All files updated after completing
- ✅ Clean commit with proper message
