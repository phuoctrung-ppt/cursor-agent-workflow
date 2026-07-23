---
name: planning
description: Use when you need to plan technical solutions that are scalable, secure, and maintainable.
license: MIT
---

# Planning

Create detailed technical implementation plans through research, codebase analysis, solution design, and comprehensive documentation.

## When to Use

Use this skill when:
- Planning new feature implementations
- Architecting system designs
- Evaluating technical approaches
- Creating implementation roadmaps
- Breaking down complex requirements
- Assessing technical trade-offs

## Core Responsibilities & Rules

Always honoring **YAGNI**, **KISS**, and **DRY** principles.
**Be honest, be brutal, straight to the point, and be concise.**


### 1. Codebase Understanding
Load: `references/codebase-understanding.md`
**Skip if:** Provided with codebase or architecture exiting

### 2. Planning on a lower-capability model
Load: `references/planning-with-lower-models.md`
**Load when:** running on a small/cheap model, or when plans come out vague,
truncated, or full of placeholders. It grounds the model in real facts, forces
one-section-at-a-time output, and adds a self-verify gate.


## Workflow Process

1. **Initial Analysis** → Read `docs/architecture.md` + `.cursor/rules/*.mdc` for the real stack/structure (AGENTS.md §2/§3 may be blank template — do not plan from blanks). Read 1–3 similar existing files.
2. **Research Phase** → Investigate approaches yourself; if the task is large, delegate targeted lookups via the Task tool (`generalPurpose`). This roster has no standalone "researcher" agent — do not invent one.
3. **Synthesis** → Analyze findings, identify optimal solution
4. **Design Phase** → Create architecture, implementation design
5. **Plan Documentation** → Fill the architect-planner Plan Template field-by-field (do not restructure it)
6. **Review & Refine** → Run the self-verify gate (see `references/planning-with-lower-models.md` §2 Rule 5) before handoff

## Output Requirements

- DO NOT implement code - only create plans (and sync domain config docs)
- Respond with plan file path and summary
- Ensure self-contained plans with necessary context
- Include code snippets/pseudocode when clarifying
- Provide multiple options with trade-offs when appropriate
- Fully respect the `./docs/development-rules.md` file.

**Plan Directory Structure**
```
    - ADR: `docs/adr/NNNN-short-title.md`
    - Plan: `docs/plans/YYYY-MM-DD-feature-name.md`
    - Architecture overview: `docs/architecture.md`
    - Domain hub: `AGENTS.md` (update sections that the plan changes)
```

## Domain Config Sync (required before workers)

After the plan is drafted and the approach is approved, sync durable project docs — do not stop at the plan file alone.

1. Fill the plan's **Domain Config Sync** checklist (`N/A — reason` allowed per item).
2. Write/update ADR(s) under `docs/adr/` when architecture decisions changed.
3. Create or update `docs/architecture.md` (living system overview).
4. Update `AGENTS.md` only for approved changes (§2 stack, §3 structure, §4 tenancy, §5 agents/scopes, §6+ rules).
5. Update `.cursor/config/worker-scopes.json` / `protected-paths.json` when scopes or protected areas change (scope expansion needs orchestrator approval).
6. Point `docs/plans/.active-plan` at the new plan.

Module file scaffolds remain `@scaffold-agent`'s job. Architect owns domain config + ADR + architecture overview.

## Active Plan State

Prevents version proliferation by tracking current working plan.

### State File

`<WORKING-DIR>` = current project's working directory (where was launched or `pwd`).

**Canonical path:** `docs/plans/.active-plan` (unified with `.cursor` workflow; do not use `.plan/`).

**Example content:**
```
docs/plans/2026-07-21-agent-worker-refactor.md
```

### Rules

1. **Check first**: Before creating plan, check if `<WORKING-DIR>/docs/plans/.active-plan` exists
2. **Validate path**: If exists, verify the path points to a valid plan file under `docs/plans/`
3. **Prompt user**: If valid, ask "Continue with existing plan? [Y/n]"
   - Y (default): Reuse existing plan path
   - n: Create new plan, update state file
4. **Set on create**: When creating new plan, write path to `<WORKING-DIR>/docs/plans/.active-plan`
5. **Reset**: User can delete file manually (`rm docs/plans/.active-plan`) to start fresh

### Report Output Location

All agents writing reports MUST:
1. Read `<WORKING-DIR>/docs/plans/.active-plan` to get current plan path
2. Write reviews to `docs/reviews/YYYY-MM-DD-description.md`
3. Optionally reference the active plan path in the review header

**Fallback:** If no active-plan file exists, write to `docs/reviews/` with a dated filename.

## Quality Standards

- Be thorough and specific
- Consider long-term maintainability
- Research thoroughly when uncertain
- Address security and performance concerns
- Make plans detailed enough for junior developers
- Validate against existing codebase patterns

**Remember:** Plan quality determines implementation success. Be comprehensive and consider all solution aspects.
