# 🔄 PARALLEL AGENTS COORDINATION

**Fecha**: 2025-11-24 16:20:00
**Coordinador**: Main Agent (Claude Code)

---

## 🎯 OBJETIVOS

3 agentes trabajando en paralelo:
1. **QA Backend Agent** - Testing exhaustivo de APIs
2. **QA Frontend Agent** - Testing completo de UI/UX
3. **Dev Agent** - Resolver bugs reportados en tiempo real

---

## 📋 WORKFLOW

```
QA Backend ──┐
             ├──> Dev Agent ──> Fixes ──> Re-test
QA Frontend ─┘
```

---

## 📊 REPORTING FORMAT

### Para QA Agents:
```markdown
## Bug Report #X
- **Severity**: 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low
- **Component**: [API/Frontend/Database]
- **Endpoint/Page**: [específico]
- **Steps to Reproduce**: [1,2,3...]
- **Expected**: [...]
- **Actual**: [...]
- **Error Message**: [si aplica]
- **Priority**: P0/P1/P2/P3
```

### Para Dev Agent:
```markdown
## Fix #X (Bug #X)
- **Status**: 🔄 In Progress / ✅ Fixed / ❌ Blocked
- **Files Modified**: [lista]
- **Solution**: [breve descripción]
- **Commit**: [hash]
- **Ready for Re-test**: Yes/No
```

---

## 📁 FILES TO UPDATE

- **All Agents**: `.agents/BUG_TRACKER.md` (for bug reports and status)
- **All Agents**: `.agents/TASK_LOG.md` (for task tracking and progress)

---

## 🔴 CRITICAL ISSUES TO PRIORITIZE

1. **Bug #8**: RAG Upload (ya en progreso por Main Agent)
2. Cualquier bug P0 que bloquee funcionalidad core
3. Authentication/Authorization issues
4. Data persistence problems

---

## ✅ SUCCESS CRITERIA

- [ ] QA Backend: All API endpoints tested
- [ ] QA Frontend: All pages tested
- [ ] Dev: All P0 bugs fixed
- [ ] Dev: All P1 bugs fixed or documented
- [ ] Re-test: All fixes verified

---

## ⏱️ TIME BOXES

- **QA Backend**: 45-60 min testing
- **QA Frontend**: 45-60 min testing
- **Dev Agent**: 2-3 hours fixing
- **Total**: ~3 hours para MVP ready

---

**STATUS**: 🟢 READY TO START
