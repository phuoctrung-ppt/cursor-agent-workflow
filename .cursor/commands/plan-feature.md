---
name: plan-feature
description: Architect planning workflow — ADR, schema, API contract, task breakdown with agent assignments, and domain config sync
---

Act as **Architect Planner** (`.cursor/agents/architect-planner.md`).

Feature: {feature_description}

1. Run skill-loader: `python3 .cursor/skills/scripts/skill-loader.py --phase plan --task "{feature_description}" --agent architect-planner`
2. **Phase 0 BRAINSTORM** (HARD-GATE): explore codebase, propose 2–3 options, wait for approval — do not write the plan file yet
3. Read `AGENTS.md §2` (tech stack) and `§3` (structure) to understand the project's framework, DB, and folder layout
4. Explore codebase for related modules
5. Write plan to `docs/plans/YYYY-MM-DD-{slug}.md` using the architect-planner template (include **Domain Config Sync** section)
6. Include:
   - Acceptance criteria
   - Database migration needs
   - Shared type/contract definitions (schema tool from `AGENTS.md §2`)
   - File list with owner agents
   - Task table with agent assignments and dependencies
   - Security / compliance notes from `AGENTS.md §6`
   - Risks and scope boundaries
7. **Phase 1.5 SYNC DOMAIN CONFIG** (before workers):
   - ADR → `docs/adr/NNNN-short-title.md` when architecture/stack/pattern decisions changed
   - Create/update living overview → `docs/architecture.md`
   - Update `AGENTS.md` sections that changed (§2 stack, §3 structure, §4 tenancy, §5 roster/scopes, §6+ rules)
   - Update `.cursor/config/worker-scopes.json` / `protected-paths.json` if scopes or protected areas changed (orchestrator approval for scope expansion)
   - Point `docs/plans/.active-plan` at this plan
   - Record N/A + reason in the plan for any skipped sync item
8. Wait for orchestrator approval of plan + sync diffs before dispatching any workers (use `@scaffold-agent` first if new module shells are required)
