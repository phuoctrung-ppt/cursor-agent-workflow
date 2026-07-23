---
name: agentic-workflow
description: Generic Planner-Worker-Judge workflow for scoped agentic execution. Use when planning work, coordinating workers, evaluating protected changes, or porting this workflow to another repo.
---

# Agentic Workflow

This skill is **repo/domain agnostic**. Project-specific context (name, tech stack, paths, compliance) lives in `AGENTS.md` and `.cursor/config/*.json`. This skill explains the workflow mechanics only.

## Core Loop

1. **Classify** — use `.cursor/config/protected-paths.json`; do not rely on agent self-report.
2. **Plan** — for protected or module-spanning work, write `docs/plans/YYYY-MM-DD-topic.md`.
3. **Execute** — dispatch the narrowest worker with a handoff packet.
4. **Verify** — run checks proportional to risk.
5. **Review** — for protected work, persist `docs/reviews/YYYY-MM-DD-topic.md`.
6. **Loop or complete** — changes requested return to a focused worker handoff.

## Handoff Packet

Every worker task starts from a handoff packet. Fill this before dispatching:

```markdown
Objective:
In-scope paths:
Out-of-scope paths:
Plan/ADR:
Required skills:
Acceptance criteria:
Required verification:
Risk notes:
Scope expansion path:
```

## Agent Roster

See `AGENTS.md §4` for the full agent table for this project. Standard agents available in `.cursor/agents/`:

| Agent | Role |
|---|---|
| `architect-planner` | Plans, writes ADRs, dispatches handoff packets |
| `scaffold-agent` | Bootstraps module/page shells before workers implement |
| `designer-worker` | UI/UX design, component specs, design systems |
| `backend-worker` | API features, services, DTOs |
| `frontend-worker` | UI components, pages, data fetching |
| `database-worker` | Migrations, schema design, query optimization |
| `ai-worker` | LLM integration, embeddings, cost tracking |
| `devops-worker` | Docker, CI/CD, infra |
| `security-worker` | Auth, RBAC, encryption, compliance |
| `qa-worker` | Tests: unit, integration, E2E |
| `judge-agent` | Read-only review gate |
| `admin-worker` | Admin/control-plane (elevated privilege) |

## Porting to Another Repo

Copy the workflow files, then update only configuration — do not modify hook code or skill-loader:

### Files to Copy (unchanged)
- `.cursor/hooks/` (all files)
- `.cursor/config/` (all files — update content, not structure)
- `.cursor/skills/agentic-workflow/`
- `.cursor/skills/scripts/skill-loader.py`
- `.cursor/rules/006-agentic-workflow.mdc`

### Files to Update for Your Project
1. **`AGENTS.md`** (project root) — fill in project name, tech stack, structure, agent scopes, compliance
2. **`.cursor/config/workflow-policy.json`** — no changes needed (already domain-agnostic)
3. **`.cursor/config/protected-paths.json`** — update `projectProtectedGlobs` with your sensitive paths
4. **`.cursor/config/worker-scopes.json`** — update `agents` section with your concrete folder paths
5. **`.cursor/skills/skills-manifest.json`** — add domain skills for your tech stack, remove unneeded ones

### Files to Copy Selectively (bring the skills your project needs)
- `.cursor/skills/databases/` — if using a SQL/NoSQL database
- `.cursor/skills/docker-devops/` — if using Docker
- `.cursor/skills/testing-qa/` — always useful
- `.cursor/skills/frontend-skills/` — if building a React/Next.js frontend
- `.cursor/skills/taste-design/` — if building any user-facing UI
- Domain skills (nestjs-skills, bullmq-worker, etc.) — only if your stack uses them

Keep hook code generic unless the hook payload format changes.

## References

- [workflow-phases.md](references/workflow-phases.md)
