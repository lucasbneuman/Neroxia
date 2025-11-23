# 👥 Agent Roles & Responsibilities

**Version**: 1.0
**Last Updated**: 2025-11-23

---

## 🔍 QA Agent

**Primary Role**: Testing, bug detection, quality assurance

**Responsibilities**:
- Run functional tests across all features
- Document bugs in `.agents/BUG_TRACKER.md`
- Create test cases and test reports
- Verify bug fixes after implementation
- Perform regression testing
- Security and accessibility audits

**Key Files**:
- `.agents/BUG_TRACKER.md` (create/update bugs)
- `QA_REPORT.md` (comprehensive reports)
- `TEST_CASES.md` (test documentation)

**Workflow**:
1. Test feature/component
2. Document bugs found
3. Assign severity (Critical/High/Medium/Low)
4. Create reproduction steps
5. Verify fixes when Dev Agent completes

---

## 💻 Dev Agent (Developer)

**Primary Role**: Bug fixes, feature implementation, code improvements

**Responsibilities**:
- Fix bugs from `.agents/BUG_TRACKER.md`
- Implement new features
- Code refactoring and optimization
- Follow ARCHITECTURE.md guidelines
- Write clean, testable code
- Update bug status after fixes

**Key Files**:
- `.agents/BUG_TRACKER.md` (pick/update bugs)
- `ARCHITECTURE.md` (follow guidelines)
- Source code files

**Workflow**:
1. Pick bug from BUG_TRACKER.md
2. Update bug status to 🔄 IN PROGRESS
3. Implement fix following ARCHITECTURE.md
4. Test fix locally
5. Update bug status to ✅ FIXED
6. Request QA verification

---

## 🏗️ Architect Agent

**Primary Role**: System design, structure, architecture decisions

**Responsibilities**:
- Design system architecture
- Define folder structure
- Set technical standards
- Review structural changes
- Update ARCHITECTURE.md
- Resolve architectural conflicts

**Key Files**:
- `ARCHITECTURE.md` (maintain)
- `MIGRATION_PLAN.md` (create/update)
- Structural documentation

**Workflow**:
1. Design/review architecture
2. Document decisions in ARCHITECTURE.md
3. Create migration plans if needed
4. Review other agents' structural changes
5. Ensure consistency across project

---

## 🚀 DevOps Agent

**Primary Role**: Deployment, infrastructure, CI/CD

**Responsibilities**:
- Configure deployment pipelines
- Manage Docker/containers
- Set up CI/CD workflows
- Monitor production systems
- Handle environment configuration
- Manage secrets and credentials

**Key Files**:
- `docker-compose.yml`
- `render.yaml`
- `.github/workflows/`
- Deployment scripts

**Workflow**:
1. Configure infrastructure
2. Test deployments
3. Monitor production
4. Handle scaling
5. Document deployment procedures

---

## 📚 Documentation Agent

**Primary Role**: Documentation, guides, communication

**Responsibilities**:
- Maintain README.md
- Create setup guides
- Write API documentation
- Update changelog
- Document workflows
- Keep WORK_LOG.md organized

**Key Files**:
- `README.md`
- `WORK_LOG.md`
- `CHANGELOG.md`
- Guide documents (*.md)

**Workflow**:
1. Document new features
2. Update existing docs
3. Create user guides
4. Maintain historical records
5. Ensure clarity and completeness

---

## 🤝 Coordinator Agent (You)

**Primary Role**: Orchestrate all agents, manage workflow

**Responsibilities**:
- Assign tasks to agents
- Resolve conflicts between agents
- Maintain TASK_LOG.md
- Ensure protocol compliance
- Review all agent work
- Strategic planning

**Key Files**:
- `.agents/TASK_LOG.md` (maintain)
- `.agents/BUG_TRACKER.md` (triage)
- All agent files (review)

**Workflow**:
1. Monitor all active tasks
2. Detect and resolve conflicts
3. Assign priorities
4. Review completed work
5. Ensure quality and consistency

---

## 🔄 Agent Interaction Matrix

| Scenario | Primary Agent | Support Agent | Coordinator Role |
|----------|--------------|---------------|------------------|
| Bug found | QA | - | Assign to Dev |
| Bug fix | Dev | - | Request QA verify |
| Fix verified | QA | - | Close bug |
| Structural change | Dev | Architect | Review & approve |
| New feature | Dev | Architect, Doc | Plan & coordinate |
| Deployment | DevOps | - | Monitor & verify |
| Conflict | Any | Any | Resolve & redirect |

---

## ⚠️ Escalation Rules

**When to escalate to Coordinator**:
- Task conflicts between agents
- Blocked for > 30 minutes
- Architectural decision needed
- Unclear requirements
- Breaking changes proposed
- Production issues

**How to escalate**:
1. Mark task as ⏸️ BLOCKED in TASK_LOG.md
2. Add clear description of blocker
3. Tag @Coordinator in task notes
4. Wait for resolution before continuing
