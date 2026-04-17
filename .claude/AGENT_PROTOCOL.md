# MANDATORY AGENT PROTOCOL

**VERSION:** 1.0
**APPLIES TO:** ALL agents in `.claude/agents/`
**PRIORITY:** CRITICAL - These rules override any conflicting instructions

---

## 🎯 CORE PRINCIPLES

1. **Efficiency First**: Save tokens, minimize verbosity
2. **Clean Workspace**: Delete temporary code immediately after use
3. **Scalable Development**: Every artifact must serve the application long-term
4. **Accountability**: Document everything critical, nothing trivial

---

## 📋 MANDATORY RULES

### 1. CODE HYGIENE

**✅ DO:**
- Delete validation/diagnostic scripts immediately after use
- Remove deprecated code you created
- Keep only production-ready code in the codebase

**❌ DON'T:**
- Leave test scripts in application directories
- Create "temporary" files without cleanup
- Accumulate unused utilities

**📂 Temporary Scripts Location:**
- ALL one-time-use scripts → `.claude/scripts/`
- Add descriptive name: `.claude/scripts/validate_rls_YYYYMMDD.py`
- Delete after task completion

---

### 2. RESPONSE LENGTH

**✅ DO:**
- Be concise: 2-4 sentences for task completion summaries
- Use bullet points for multiple items
- Provide details ONLY when explicitly requested

**❌ DON'T:**
- Write step-by-step replication guides unless asked
- Explain every decision in detail
- Repeat information already in logs

**Example - GOOD:**
```
Task completed. Fixed RLS policies for 3 tables (users, configs, messages).
Applied migration 005_v3, validated with test queries.
```

**Example - BAD:**
```
I have successfully completed the task of fixing the RLS policies.
First, I analyzed the current state... Then I created a new migration file...
Here's how you can replicate this manually: Step 1... Step 2...
The reason I chose this approach is because... [5 more paragraphs]
```

---

### 3. TASK LOGGING

**Required after EVERY task:**

**1. Update `.claude/TASK.md`:**
```markdown
### [YYYY-MM-DD HH:MM] - [Agent Name]
**Task:** Brief description (1 line)
**Changes:** File paths modified
**Status:** ✅ Complete / ⚠️ Partial / ❌ Failed
```

**2. Update `.claude/BUG_TRACKER.md`:**
- ONLY when you discover or fix a bug
- Follow existing format (see file for template)

**3. Commit immediately:**
```bash
git add -A
git commit -m "feat/fix: Brief description

- Bullet point of change 1
- Bullet point of change 2

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### 4. DOCUMENTATION UPDATES

**Update when you modify:**

| File Modified | Update Documentation |
|---------------|---------------------|
| API endpoints | `API_DOCUMENTATION.md` |
| Database schema | `ARCHITECTURE.md` + migration file |
| Architecture/patterns | `ARCHITECTURE.md` |
| Agent workflows | `CLAUDE.md` |
| Environment vars | `CLAUDE.md` (Environment Variables section) |

**Format:**
- Be surgical: Update ONLY affected sections
- No redundant explanations
- Keep existing format/structure

---

### 5. WORKSPACE ORGANIZATION

**Directory Rules:**

```
.claude/
├── scripts/              # ← ONE-TIME-USE SCRIPTS ONLY
│   ├── validate_*.py     # Named with purpose + date
│   └── test_*.sh         # DELETE after use
├── agents/               # Agent definitions (no scripts)
├── AGENT_PROTOCOL.md     # This file
├── BUG_TRACKER.md        # Bug log
└── TASK.md               # Task log
```

**Cleanup Checklist (run before task completion):**
- [ ] Removed all diagnostic scripts from app directories
- [ ] Moved one-time scripts to `.claude/scripts/` (if keeping)
- [ ] Deleted all scripts used (if not needed for reference)
- [ ] No unused files in `apps/`, `packages/`, or project root

---

### 6. COMMIT DISCIPLINE

**When to commit:**
- After EVERY completed subtask
- Before switching context
- After fixing a bug
- After adding a feature

**Commit message format:**
```
<type>: <brief description>

- Change 1
- Change 2

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

---

## 🚨 VIOLATION CONSEQUENCES

Agents violating this protocol will:
1. Have their prompts audited and rewritten
2. Receive explicit reminders in every task
3. Be flagged for removal if patterns persist

---

## ✅ COMPLIANCE CHECKLIST

Before reporting task completion, verify:

- [ ] All temporary/diagnostic code deleted
- [ ] TASK.md updated with brief entry
- [ ] BUG_TRACKER.md updated (if bug found/fixed)
- [ ] Documentation updated (if architecture/API changed)
- [ ] Commit created with proper message
- [ ] Workspace clean (no orphaned scripts)
- [ ] Response concise (<100 words unless details requested)

---

## 📚 REFERENCE

**Read these files before ANY task:**
1. `CLAUDE.md` - Project context
2. `ARCHITECTURE.md` - System design
3. `API_DOCUMENTATION.md` - Endpoint contracts
4. `.claude/BUG_TRACKER.md` - Known issues
5. `.claude/TASK.md` - Recent work by other agents

---

**Last Updated:** 2025-12-03
**Enforcement:** Immediate
