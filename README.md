# Agentic Planner-Worker-Judge Workflow

A **portable, domain-neutral** Cursor workflow for building software with coordinated AI agents.
It splits work into three roles — **Planner** (designs), **Workers** (implement), **Judge** (reviews) —
and enforces the flow with skills, scoped edit permissions, protected-path gates, and durable
artifacts (`docs/plans`, `docs/adr`, `docs/reviews`, `docs/design`).

Everything ships stack-agnostic. You describe your project **once** in `AGENTS.md`, and every agent
reads that file to learn your tech stack, structure, and compliance rules.

---

## Table of Contents

1. [Core idea](#1-core-idea)
2. [Quick start (new idea → shipped module)](#2-quick-start-new-idea--shipped-module)
3. [The two workflows](#3-the-two-workflows)
4. [Commands](#4-commands)
5. [Agents](#5-agents)
6. [Skills & the skill-loader](#6-skills--the-skill-loader)
7. [Gates & guardrails](#7-gates--guardrails)
8. [Design-first frontend](#8-design-first-frontend)
9. [Directory map](#9-directory-map)
10. [Porting to another repo](#10-porting-to-another-repo)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Core idea

| Role | Who | Does | Can edit |
|---|---|---|---|
| **Planner** | `architect-planner` | Brainstorm, ADRs, task breakdown, syncs `AGENTS.md` | `docs/**`, `.cursor/**`, `AGENTS.md` |
| **Workers** | `backend-`, `frontend-`, `designer-`, `database-`, `ai-`, `devops-`, `security-`, `admin-`, `scaffold-`, `qa-` | Implement inside a narrow scope | only their configured paths |
| **Judge** | `judge-agent` | Read-only review of **plans** and **code** | `docs/reviews/**` |

Key principles:

- **`AGENTS.md` is the single source of truth** for domain facts (stack, structure, compliance).
  The `.cursor/` machinery never needs editing to change domains.
- **Nothing is claimed "done" from intent alone** — completion requires evidence (build/tests/artifacts).
- **Protected changes** (auth, migrations, config, `AGENTS.md`, …) require a plan + a review artifact.
- **Workers ship; they don't freelance** — planning and design happen upstream.

---

## 2. Quick start (new idea → shipped module)

From an empty or fresh project:

```text
# 1. Brainstorm + define the whole system (creates AGENTS.md, architecture, ADRs, roadmap)
/architecture-plan brainstorming <your idea in a sentence or two>

# 2. After you approve the concept and the judge approves the plan:
/architecture-plan            # breaks the roadmap into concrete, executable per-module tasks

# 3. Build each module through the full loop (execute → test → judge → fix → done):
/dev-module <module_name>
```

That's the golden path. Steps 1–2 are **planning** (`architect-plan`), step 3 is **execution**
(`dev-module`). Each stage ends with a judge gate that writes an artifact under `docs/reviews/`.

If you already have a project and just want to add one feature, you can skip straight to
`/dev-module <feature>` (it will brainstorm + plan inline when no approved plan exists).

---

## 3. The two workflows

### A. `/architecture-plan` — idea → system (planning)

Two modes, auto-selected by whether you pass an idea:

**GENESIS** — `/architecture-plan brainstorming {idea}`
1. **Brainstorm** (chat-only HARD-GATE) — concept brief, MVP vs Later, 2–3 approaches. *Waits for your approval.*
2. **Standardize domain** — fills the `AGENTS.md` template with real values for the approved idea.
3. **Architecture + ADRs** — creates `docs/architecture.md` and `docs/adr/NNNN-*.md`.
4. **System roadmap** — writes `docs/plans/YYYY-MM-DD-{slug}.md`, sets `docs/plans/.active-plan`.
5. **Judge Plan Review** — verifies feature coverage + no leftover placeholders → `PLAN_APPROVED`.

**BREAKDOWN** — `/architecture-plan` (no idea; an approved roadmap exists)
1. Expands each roadmap module into executable tasks (real paths, owner agent, testable acceptance, ordered deps, handoff packets).
2. **Judge Plan Review** — every MVP feature maps to ≥1 task → `PLAN_APPROVED` → ready for `/dev-module`.

### B. `/dev-module {name}` — plan → shipped (execution)

A resumable state-machine loop (state in `.cursor/state/module-{name}-loop.json`):

```
Phase 0  Restore state (resume if interrupted)
Phase 1  Brainstorm         ─┐ skipped if /architecture-plan already produced
Phase 2  Plan + sync config ─┘ an approved breakdown for this module
Phase 1.5 Scaffold          (optional — @scaffold-agent creates shells)
Phase 3  Execute            (workers implement; design-first for UI)
Phase 4  Test               (@qa-worker)
Phase 5  Verify             (@judge-agent → APPROVED / CHANGES_REQUESTED)
Phase 5a Fix loop           (≤ 3 iterations, then Phase 5b escalate)
Phase 6  Done ✅
```

The final judge review enforces: **build error-free**, **no missing features vs the plan**,
and **coverage meets `AGENTS.md` targets**.

---

## 4. Commands

Type these as slash-commands in Cursor. Located in `.cursor/commands/`.

| Command | Purpose |
|---|---|
| `/architecture-plan brainstorming {idea}` | GENESIS: idea → `AGENTS.md` + architecture + roadmap |
| `/architecture-plan` | BREAKDOWN: roadmap → executable tasks |
| `/dev-module {name}` | Full per-module execution loop with judge gate + fix loop |
| `/plan-feature {desc}` | Lightweight single-feature planning (subset of GENESIS) |
| `/generate-module {name}` | Scaffold a backend feature module (stack from `AGENTS.md §2`) |
| `/generate-migration` | Create a DB migration (up + down) |
| `/generate-test` | Generate unit/integration/E2E tests |
| `/workflow-eval {target}` | Judge review that always persists a `docs/reviews/` artifact |
| `/security-audit` | Security-focused review pass |
| `/ai-cost-check` | *(AI/LLM projects only)* verify cost tracking + human-in-the-loop |
| `/tenant-context-check` | *(multi-tenant projects only)* audit tenant isolation |

> Commands tagged *(… only)* are domain examples; they're inert for projects that don't use those features.

---

## 5. Agents

Defined in `.cursor/agents/`. Invoke with `@agent-name`. Each reads `AGENTS.md` first and loads
skills via the skill-loader.

| Agent | Role |
|---|---|
| `architect-planner` | Plans, ADRs, task breakdown, syncs domain config |
| `scaffold-agent` | Creates empty module/page shells (no logic) |
| `designer-worker` | Design specs + sketches (taste-design + imagegen skills) |
| `frontend-worker` | UI components/pages (design-first — see §8) |
| `backend-worker` | API modules, services, DTOs, guards |
| `database-worker` | Migrations, entities, query optimization |
| `ai-worker` | LLM/embeddings/cost tracking (if the stack has AI) |
| `security-worker` | Auth, RBAC, encryption, rate limiting |
| `devops-worker` | Docker, CI/CD, infra |
| `admin-worker` | Admin / control-plane elevated features (if any) |
| `qa-worker` | Unit / integration / E2E tests |
| `judge-agent` | Read-only quality gate (plan + code review) |

Each agent may only edit the paths configured in `.cursor/config/worker-scopes.json`.

---

## 6. Skills & the skill-loader

Skills are focused knowledge packs in `.cursor/skills/` (registered in `skills-manifest.json`).
Agents don't bulk-read them — they call the **skill-loader** to get only what's relevant:

```bash
python3 .cursor/skills/scripts/skill-loader.py \
  --phase <brainstorm|plan|design|implement-backend|implement-frontend|database|devops|test|review|scaffold> \
  --task "<what you're doing>" \
  --agent <agent-name> \
  --keywords "comma,separated,hints"
```

It returns JSON with:
- `matchedSkills[]` → the `SKILL.md` files to read for top-level rules.
- `referenceFiles[]` → deeper reference docs to open **only when needed**.

Skills are split into **portable** (framework-agnostic: `agentic-workflow`, `planning`, `security`,
`taste-design`, `frontend-skills`, `databases`, `testing-qa`, `docker-devops`) and **domain**
(`portable:false`, activated by `AGENTS.md §2`: `nestjs-skills`, `zod-shared-types`,
`ai-llm-integration`, `admin-service`, `bullmq-worker`). Domain skills stay dormant until your
stack calls for them.

---

## 7. Gates & guardrails

Enforced automatically by hooks (`.cursor/hooks.json` → `.cursor/hooks/`):

| Hook | When | What it does |
|---|---|---|
| `session-start` | session start | Loads workflow context |
| `enforce-worker-scope` | before Write/Edit | Blocks edits outside the agent's configured scope |
| `record-file-edit` | after each edit | Records touched files for stop-hook classification |
| `block-destructive-shell` | before shell | Blocks dangerous commands |
| `require-protected-review` | on stop | Blocks completion of **protected** changes without a current plan + review artifact |

**Protected changes** are classified mechanically by `.cursor/config/protected-paths.json`
(globs + keywords + a multi-file threshold), not by agent self-report. Protected work **fails
closed** (must have artifacts); standard work **fails open** (so a broken hook never locks the team out).

To bypass a gate deliberately (rare), log it:
```bash
.cursor/hooks/review-override.sh --skip-review "reason"
```

The judge outputs one of: `PLAN_APPROVED | PLAN_CHANGES_REQUESTED`,
`TASK_APPROVED | TASK_CHANGES_REQUESTED`, `BRANCH_APPROVED | BRANCH_CHANGES_REQUESTED`.

---

## 8. Design-first frontend

UI work cannot start without a design artifact. `frontend-worker` has a **DESIGN-GATE** (Step 0):

1. It checks for a spec `docs/design/YYYY-MM-DD-{feature}.md` **and** a sketch under
   `docs/design/sketches/{feature}/`.
2. If both exist → implement to match.
3. If either is missing → hand off to `@designer-worker`, who uses the `taste-design` +
   `imagegen-frontend-*` skills to produce the spec + sketch first.
4. Skipped only for non-visual work (logic/data/bugfix with no new UI), recorded as
   `DESIGN-GATE: skipped — no new UI`.

`/dev-module` Phase 3 mirrors this: it dispatches `@designer-worker` before `@frontend-worker`
for any new UI, and the judge checks that shipped UI traces back to a design artifact.

---

## 9. Directory map

```
.
├── AGENTS.md                    # ← the one file you fill in per project (domain config hub)
├── README.md                    # this file
├── docs/
│   ├── plans/                   # feature/roadmap plans (+ .active-plan pointer)
│   ├── adr/                     # architecture decision records
│   ├── architecture.md          # living system overview (created at GENESIS)
│   ├── design/                  # design specs + sketches/ (design-first gate)
│   ├── reviews/                 # judge artifacts (+ review-overrides.log)
│   ├── user-stories/            # acceptance-criteria source of truth
│   └── development-rules.md     # coding rules referenced by AGENTS.md
└── .cursor/
    ├── agents/                  # agent role definitions
    ├── commands/                # slash-commands
    ├── rules/                   # always-applied rules (001–006)
    ├── skills/                  # skills + skills-manifest.json + scripts/skill-loader.py
    ├── config/                  # worker-scopes.json, protected-paths.json, workflow-policy.json
    ├── hooks.json + hooks/      # enforcement hooks
    └── state/                   # per-module loop state
```

---

## 10. Porting to another repo

1. Copy `.cursor/` and `AGENTS.md` into the new repo (and optionally `docs/` scaffolding).
2. Fill in `AGENTS.md` §1–§15 — replace every `<PLACEHOLDER>` and delete `_EXAMPLE_` blocks.
   (Or just run `/architecture-plan brainstorming {idea}`, which fills it for you.)
3. Edit `.cursor/config/protected-paths.json` → `projectProtectedGlobs` for your sensitive paths.
4. Tighten `.cursor/config/worker-scopes.json` → `agents{}` to your real folders from `AGENTS.md §3`.
   (They ship as portable globs that work everywhere; tightening is optional but recommended.)
5. Add/remove domain skills in `.cursor/skills/skills-manifest.json`.

No changes are needed to the hooks, `workflow-guard.py`, `skill-loader.py`, or generic rules.

> **Do not** leave raw `<PLACEHOLDER>` values in any `AGENTS.md` section you're actively building
> against, and **never invent** stack/structure/compliance facts from an `_EXAMPLE_` block — the
> judge's Plan Review will flag leftover placeholders.

---

## 11. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Edit blocked "outside scope" | The agent's `worker-scopes.json` entry doesn't include that path. Request scope expansion from the orchestrator or use the right agent. |
| Stop hook blocks completion | It's a protected change without a current plan/review. Produce the plan + run `/workflow-eval`, or override with `review-override.sh` and a logged reason. |
| Judge says `PLAN_CHANGES_REQUESTED` | Leftover `<PLACEHOLDER>` in `AGENTS.md`, a feature with no task, or non-executable tasks. Fix and re-review. |
| `skill-loader.py` returns no skills | Check `--phase`/`--agent`/`--keywords`; confirm the skill is registered in `skills-manifest.json`. |
| Frontend worker refuses to code | DESIGN-GATE: no spec/sketch. Run `@designer-worker` first (or note "no new UI"). |
| Plans come out vague on a smaller model | Read `.cursor/skills/planning/references/planning-with-lower-models.md` — grounding, one section at a time, no placeholders, self-verify. |

---

**In short:** fill `AGENTS.md` (or let GENESIS do it) → `/architecture-plan` to design →
`/dev-module` to build. The gates keep quality high and the artifacts keep everything traceable.
