---
name: architecture-plan
description: Idea → system. GENESIS mode (with an idea) brainstorms, standardizes the project domain by filling AGENTS.md, creates docs/architecture.md + ADRs, and writes a system roadmap. BREAKDOWN mode (no idea) expands the approved roadmap into executable per-module tasks. Both modes end with a judge plan-review gate. Feeds /dev-module.
---

Act as **Orchestrator** driving **`@architect-planner`** (`.cursor/agents/architect-planner.md`) and **`@judge-agent`** (`.cursor/agents/judge-agent.md`). Stay inside the current `.cursor` workflow (AGENTS.md, protected-paths, worker-scopes, skills, hooks).

## Mode selection

- **GENESIS** — invoked as `/architecture-plan brainstorming {idea}` (an idea/argument is present).
  Produces: standardized domain (`AGENTS.md`), `docs/architecture.md`, ADR(s), and a system roadmap plan.
- **BREAKDOWN** — invoked as `/architecture-plan` (no idea; an active plan already exists).
  Expands the roadmap into concrete, executable per-module tasks.

If an idea is present → run GENESIS. Otherwise → run BREAKDOWN against `docs/plans/.active-plan`.

---

# GENESIS mode — `/architecture-plan brainstorming {idea}`

Input: **{idea}**

## Step 0 — Load skills
```bash
python3 .cursor/skills/scripts/skill-loader.py --phase brainstorm --task "{idea}" --agent architect-planner
python3 .cursor/skills/scripts/skill-loader.py --phase plan --task "{idea}" --agent architect-planner
```
Read the matched `planning` + `agentic-workflow` SKILLs. If plans tend to come out
vague/truncated (e.g. on a smaller model), also read
`.cursor/skills/planning/references/planning-with-lower-models.md` and follow it.

## Step 1 — BRAINSTORM (HARD-GATE, chat only)
<HARD-GATE>
Do NOT write or modify any file until the user approves the concept.
</HARD-GATE>

Package the idea into a concept brief (in chat):
- **What it does** — one paragraph; the core job-to-be-done.
- **Target users / personas.**
- **Core features** — split **MVP** vs **Later**. This list is the feature contract the judge checks against.
- **Design/UX needs** — key screens/flows, tone (delegate detail to `@designer-worker` later).
- **Domain & data** — the domain, core entities, tenancy model (none / soft / hard).
- **Constraints** — compliance, scale, budget, integrations.
- **2–3 architecture approaches** with trade-offs + a recommendation.

⏸️ **STOP — wait for explicit user approval of the concept + chosen approach + MVP boundary.**

## Step 2 — STANDARDIZE DOMAIN (fill AGENTS.md)
After approval, replace the neutral template `<PLACEHOLDER>` / `_EXAMPLE_` blocks in `AGENTS.md` with real values for the approved concept. Fill every section you can now; mark unknowns `<TBD — reason>` (not left as raw placeholder):
- §1 Overview, §2 Tech Stack (locked), §3 Repository Structure
- §4 Multi-Tenancy (or "N/A — single-tenant"), §5 Agent Roster & Scopes
- §6 Compliance, §7 Critical Paths, §8 External Services, §9 Entities
- §13 Env var names (names only), §14 Queues (or N/A), §15 API conventions

Then align config for the real paths/agents you introduced (orchestrator approval required for scope expansion):
- `.cursor/config/worker-scopes.json` (agent path globs must match §3)
- `.cursor/config/protected-paths.json` → `projectProtectedGlobs`

## Step 3 — CREATE ARCHITECTURE + ADRs
- Create `docs/architecture.md` (living overview): context, containers/modules, key data flows, tenancy, deploy sketch, decision-log pointer.
- Write ADR(s) under `docs/adr/NNNN-*.md` for each foundational decision (stack, tenancy model, storage, auth, queue topology). Link ADRs from architecture.md and the plan.

## Step 4 — SYSTEM ROADMAP PLAN
Write `docs/plans/YYYY-MM-DD-{slug}.md` using the architect-planner Plan Template. At genesis, focus on the roadmap level:
- Goal, architecture summary, tech stack (from §2)
- MVP boundary + module list, each with priority, dependencies, and 1–3 high-level acceptance criteria
- Global constraints & compliance (from AGENTS.md §4–§6)
- Domain Config Sync section (filled)
- Risks
Set `docs/plans/.active-plan` to this plan.

## Step 5 — JUDGE PLAN REVIEW (gate)
```bash
python3 .cursor/skills/scripts/skill-loader.py --phase review --task "genesis plan {slug}" --agent judge-agent --keywords "workflow,judge,plan"
```
`@judge-agent` runs **Plan Review** over `AGENTS.md` + `docs/architecture.md` + the roadmap:
feature coverage (every MVP feature mapped), domain standardization (no leftover raw
`<PLACEHOLDER>` in in-scope sections), single consistent domain, concrete enough to break down.
Writes `docs/reviews/YYYY-MM-DD-{slug}-plan.md` with `PLAN_APPROVED | PLAN_CHANGES_REQUESTED`.
- `PLAN_CHANGES_REQUESTED` → architect fixes, re-review.
- `PLAN_APPROVED` → ⏸️ STOP. Next: run `/architecture-plan` (BREAKDOWN).

---

# BREAKDOWN mode — `/architecture-plan`

Operates on `docs/plans/.active-plan` (the approved roadmap).

## Step 0 — Load skills
```bash
python3 .cursor/skills/scripts/skill-loader.py --phase plan --task "breakdown $(cat docs/plans/.active-plan)" --agent architect-planner
```

## Step 1 — EXPAND TO EXECUTABLE TASKS
For each module in the roadmap, `@architect-planner` produces a concrete task breakdown (append to the roadmap plan, or write per-module `docs/plans/YYYY-MM-DD-{module}.md` and link them). Each task must have:
- Real file paths (Create/Modify) matching §3 + `worker-scopes.json`
- Owner agent + skill(s) from `skills-manifest.json`
- Testable acceptance criteria (not "works")
- Dependencies / ordering (DB → API → Frontend)
- A filled **Handoff Packet** (objective, in/out-of-scope paths, required skills, acceptance, required checks)
Follow `planning-with-lower-models.md` (one section at a time, no placeholders) when on a smaller model.

## Step 2 — JUDGE PLAN REVIEW (gate)
`@judge-agent` Plan Review verifies: every roadmap/MVP feature maps to ≥1 task with acceptance (**no missing features**), tasks are concrete, owners/skills/scopes valid, dependencies ordered. Writes `docs/reviews/YYYY-MM-DD-{slug}-breakdown.md` with `PLAN_APPROVED | PLAN_CHANGES_REQUESTED`.
- `PLAN_APPROVED` → ⏸️ STOP. Next: execute each module with `/dev-module {module}`.

---

## Handoff to execution

Once BREAKDOWN is `PLAN_APPROVED`, run per module:
```
/dev-module {module_name}
```
`/dev-module` runs the loop: (scaffold →) execute → test → **judge code review** → fix-loop.
The judge's final-branch review enforces: **build error-free**, **no features missing vs the plan**, and **coverage meets AGENTS.md targets**. Loop until `BRANCH_APPROVED` or escalation.

## Guardrails
- Never skip the HARD-GATE brainstorm approval in GENESIS.
- Never write app business logic here — this command only plans/standardizes. Module shells belong to `@scaffold-agent`; logic to workers via `/dev-module`.
- Every gate persists an artifact (`docs/plans/`, `docs/adr/`, `docs/reviews/`).
- Respect protected-path classification and worker scopes at all times.
