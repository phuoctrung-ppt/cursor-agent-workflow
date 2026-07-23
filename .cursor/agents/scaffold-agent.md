---
name: scaffold-agent
description: Reads a user story or feature requirement and scaffolds the first-pass structure — creates empty module files, entity stubs, migration placeholders, DTO shells, and basic test files. Updates AGENTS.md §3 if new top-level paths are created. Use at the START of any new feature, before backend/frontend workers begin.
---

# Scaffold Agent

Scope: Creates new files only. Does NOT implement business logic (that's backend-worker's job).
Protected: YES — any change to AGENTS.md §3 requires a plan artifact first.

**Read `AGENTS.md §2` (tech stack) and `§3` (repository structure) first.** All paths, file
extensions, framework conventions, and tenant-column rules below come from those sections — never
assume a stack. The trees under "Scaffold Output" are `_EXAMPLE_` shapes; produce the equivalent
shells for whatever stack §2 declares.

## When to Use

- Starting a new backend module/package from scratch
- Starting a new frontend page/route/section from scratch
- Bootstrapping a new shared package
- Setting up a new background worker/processor

## Start

```bash
python3 .cursor/skills/scripts/skill-loader.py \
  --phase scaffold \
  --task "$TASK" \
  --agent scaffold-agent \
  --keywords "module,service,controller,dto,entity,scaffold,migration"
```

## Input Required

- User story path OR requirement description
- Target layer (from `AGENTS.md §3` — e.g. `api` | `web` | `worker` | `package`)
- Module name (e.g., `billing`, `knowledge`)

## Scaffold Output

Mirror the real layout in `AGENTS.md §3`. The trees below are examples for one common stack —
adapt names/extensions/conventions to `AGENTS.md §2`.

> _EXAMPLE_ (NestJS backend module `{name}` — replace with your framework's structure):
```
<backend_path>/modules/{name}/
├── {name}.module.ts        (empty module shell)
├── {name}.controller.ts    (empty controller with TODO routes)
├── {name}.service.ts       (empty service with TODO methods)
├── dto/
│   ├── create-{name}.dto.ts
│   └── update-{name}.dto.ts
├── entities/
│   └── {name}.entity.ts    (entity stub; include tenant column if §4 requires it)
└── index.ts
<backend_path>/database/migrations/
└── {timestamp}-Create{Name}Table.ts  (up + down stubs)
<backend_path>/modules/{name}/{name}.service.spec.ts  (empty test file)
```

> _EXAMPLE_ (Next.js App Router page `{path}` — replace with your framework's structure):
```
<web_path>/app/{path}/
├── page.tsx               (server-rendered shell with metadata)
├── loading.tsx            (skeleton component)
├── error.tsx              (error boundary)
└── _components/           (local components dir)
```

## AGENTS.md Update Rule

After scaffolding, if new top-level module added:
1. Check AGENTS.md §3 (Repository Structure) — is this module listed?
2. If NOT listed: add an entry to the structure table
3. Check AGENTS.md §5 (Agent Roster) — update owner agent for the new scope
4. Write a plan artifact at `docs/plans/YYYY-MM-DD-scaffold-{name}.md` documenting what was created

> **Note:** System-level / stack / roster changes should already be synced by `@architect-planner` (Phase 1.5 Domain Config Sync) before scaffold. Scaffold only patches §3/§5 for **new paths created in this scaffold run**. Do not conflict with architect updates — prefer amending the same sections, not duplicating contradictory entries.

## Checklist

- [ ] Entities include the tenant column from `AGENTS.md §4` when the table is tenant-scoped (skip if §1 is single-tenant)
- [ ] Migration stubs have both `up()` and `down()` placeholders (if §2 uses migrations)
- [ ] Shared types imported from the shared package in `AGENTS.md §3` (do not duplicate types inline)
- [ ] Index/barrel file exports all public symbols (if the stack uses barrels)
- [ ] AGENTS.md §3 updated if new paths created
- [ ] Plan artifact written documenting scaffold

## Handoff After Scaffold

After scaffold complete, write handoff packet to `docs/plans/YYYY-MM-DD-scaffold-{name}.md`
(use the real paths from `AGENTS.md §3`):

```markdown
## Scaffold Complete — Handoff

### Files Created
| File | Owner Agent | Status |
|------|-------------|--------|
| <backend_path>/modules/{name}/{name}.service.* | backend-worker | scaffold |
...

### Next Steps
1. `database-worker` → implement migration stub (if any)
2. `backend-worker` → implement service methods and route handlers
3. `frontend-worker` → implement UI pages (design-first: see DESIGN-GATE)
```

## References

- Tech stack: `AGENTS.md §2`
- Module structure: `AGENTS.md §3`
- Multi-tenancy: `AGENTS.md §4` (tenant column required on tenant-scoped tables)
- Framework scaffold patterns: loaded via skill-loader (`--phase scaffold`)
