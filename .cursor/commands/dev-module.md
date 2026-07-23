---
name: dev-module
description: Full per-module development loop — brainstorm → plan → execute → test → verify → fix → loop → done. Use for any new feature module from scratch. Automatically loops through fix cycles until judge approves or loop cap is reached.
---

# Module Development Loop

Act as **Orchestrator**. Run the full development loop for module: **{feature_name}**

State file: `.cursor/state/module-{feature_name}-loop.json` (created/updated at each phase transition)

> **Upstream:** `/dev-module` is the **execution** loop. If planning was already done by
> `/architecture-plan` (a `PLAN_APPROVED` breakdown for this module exists under `docs/plans/`),
> **skip Phase 1–2** — confirm the existing plan and jump to Phase 1.5 (scaffold) / Phase 3
> (execute). Only run Phase 1–2 when no approved plan/breakdown exists for this module.

---

## Phase 0 — Restore State (if resuming)

Check if `.cursor/state/module-{feature_name}-loop.json` exists. If it does, read it and resume from `state.phase`. If not:
- If `docs/plans/.active-plan` (or a `docs/plans/*-{feature_name}.md`) holds a `PLAN_APPROVED` breakdown covering this module → set `state.phase = execute` (or `scaffold` if shells are missing) and start there.
- Otherwise start fresh at Phase 1.

---

## Phase 1 — BRAINSTORM

**Agent:** `@architect-planner`

```bash
python3 .cursor/skills/scripts/skill-loader.py \
  --phase brainstorm --task "{feature_name}" --agent architect-planner
```

Explore:
- Similar existing modules in the codebase
- Relevant patterns in `AGENTS.md §2` (stack) and `§3` (structure)
- Prior art in `docs/plans/` and `docs/adr/`
- 2–3 viable design approaches with tradeoffs

Output a short **Brainstorm Summary** (not a full plan yet) — options, constraints, recommendation.

Save state: `{ "feature": "{feature_name}", "phase": "plan", "loopCount": 0 }`

---

## Phase 2 — PLAN ⏸️ (requires approval)

**Agent:** `@architect-planner`

```bash
python3 .cursor/skills/scripts/skill-loader.py \
  --phase plan --task "{feature_name}" --agent architect-planner
```

Write full plan to `docs/plans/YYYY-MM-DD-{feature_name}.md` using the architect-planner template:
- Acceptance criteria
- DB migrations (if needed)
- Shared type contracts (per `AGENTS.md §2`)
- File list with owner agents
- Task breakdown table
- Security / compliance gates from `AGENTS.md §6`
- Risks
- **Domain Config Sync** section (required)

### Phase 2b — SYNC DOMAIN CONFIG (before execute)

After the plan is drafted, `@architect-planner` must complete Phase 1.5 from `.cursor/agents/architect-planner.md`:
- ADR in `docs/adr/` when architecture decisions changed (or N/A in plan)
- Create/update `docs/architecture.md`
- Update affected `AGENTS.md` sections (§2–§15 as applicable)
- Update `.cursor/config/*` if worker scopes / protected paths changed
- Set `docs/plans/.active-plan` to this plan

**⏸️ STOP — wait for orchestrator approval of plan + sync diffs before Phase 1.5 scaffold / Phase 3.**

Save state: `{ "phase": "execute", "planPath": "docs/plans/..." }`

---

## Phase 1.5 — SCAFFOLD (optional, for new modules)

**Agent:** `@scaffold-agent`

If the feature requires new modules/pages that don't exist yet:
```bash
python3 .cursor/skills/scripts/skill-loader.py \
  --phase scaffold --task "{feature_name}" --agent scaffold-agent \
  --keywords "module,scaffold,entity,migration,stub"
```

Scaffold creates empty shells → workers fill them with logic.
Save state: `{ "phase": "execute", "scaffoldComplete": true }`

---

## Phase 3 — EXECUTE

> **Design-first for UI:** For any task that creates/changes UI, a design artifact MUST exist before `@frontend-worker` runs — a spec `docs/design/YYYY-MM-DD-{feature}.md` **and** a sketch under `docs/design/sketches/{feature}/`. If it's missing, dispatch `@designer-worker` (phase `design`) FIRST to produce the spec + sketch with taste-design/imagegen skills, then dispatch `@frontend-worker` to ship from it. Skip the design step only for non-visual frontend work (note "no new UI"). This mirrors the `<DESIGN-GATE>` in `frontend-worker`.

**Dispatch workers in parallel** based on the task table in the plan:

| Task type | Agent | Phase |
|---|---|---|
| New module/feature scaffold | `@scaffold-agent` | `scaffold` |
| Backend / API | `@backend-worker` | `implement-backend` |
| UI design (spec + sketch) — before any new UI | `@designer-worker` | `design` |
| Frontend / UI | `@frontend-worker` | `implement-frontend` |
| Database / schema | `@database-worker` | `database` |
| AI/LLM integration | `@ai-worker` | `implement-backend` |
| Auth / security | `@security-worker` | `implement-backend` |
| DevOps / infra | `@devops-worker` | `devops` |

Each worker starts with a handoff packet from the plan. Frontend tasks receive the design spec + sketch paths in their packet.

Save state: `{ "phase": "test" }`

---

## Phase 4 — TEST

**Agent:** `@qa-worker`

```bash
python3 .cursor/skills/scripts/skill-loader.py \
  --phase test --task "{feature_name}" --agent qa-worker \
  --keywords "test,jest,playwright,e2e,mock,coverage"
```

- Run unit tests for new service layer
- Run integration tests if API routes changed
- Run E2E for critical paths from `AGENTS.md §6` if affected
- Report: test results, coverage %, any failures

Save state: `{ "phase": "verify" }`

---

## Phase 5 — VERIFY (Judge Gate)

**Agent:** `@judge-agent`

```bash
python3 .cursor/skills/scripts/skill-loader.py \
  --phase review --task "{feature_name}" --agent judge-agent \
  --keywords "workflow,judge,security,test"
```

Run `/workflow-eval` against the plan + diff + test results.
Write review to `docs/reviews/YYYY-MM-DD-{feature_name}-review.md`.

### Decision tree:

```
APPROVED  ──────────────────────────────────────────────▶ Phase 6 (DONE ✅)
CHANGES_REQUESTED + loopCount < 3 ──────────────────────▶ Phase 5a (FIX)
CHANGES_REQUESTED + loopCount >= 3 ─────────────────────▶ Phase 5b (ESCALATE)
```

Save state: `{ "phase": "fix" or "done", "reviewPath": "docs/reviews/..." }`

---

## Phase 5a — FIX (loop back)

Increment `loopCount` in state file.

Dispatch a focused **fix handoff** to the worker responsible for each CHANGES_REQUESTED item:

```
Objective: Fix [specific issue from judge review]
Plan: [planPath from state]
Judge review: [reviewPath from state]
In-scope: [only the files flagged by judge]
Acceptance: [specific criterion from judge review]
```

After fixes are applied → return to **Phase 4 (TEST)**.

---

## Phase 5b — ESCALATE (loop cap reached)

Write escalation artifact to `docs/reviews/YYYY-MM-DD-{feature_name}-escalation.md`:

```markdown
# Escalation Required — {feature_name}

Loop cap (3) reached. Human review needed.

## Remaining Issues
[list from last judge review]

## Fix Attempts
[summary of what was tried]

## Recommendation
[what the orchestrator thinks the blocker is]
```

**⏸️ STOP — do not continue until human resolves.**

---

## Phase 6 — DONE ✅

Save final state: `{ "phase": "done", "loopCount": N }`

Output summary:
```
✅ Module {feature_name} complete
Plan: docs/plans/...
Review: docs/reviews/...
Fix loops: N
Files changed: [list]
```

Clean up: optionally archive `.cursor/state/module-{feature_name}-loop.json` to `docs/plans/` for traceability.
