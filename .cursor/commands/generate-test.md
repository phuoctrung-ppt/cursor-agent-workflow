---
name: generate-test
description: Scaffold unit, integration, or E2E tests with mocks for external APIs — uses project's test framework from AGENTS.md
---

Act as **QA Worker**. Generate tests for: **{target}**

Type: {unit|integration|e2e}

1. Run skill-loader:
   ```bash
   python3 .cursor/skills/scripts/skill-loader.py \
     --phase test --task "generate {type} tests for {target}" --agent qa-worker \
     --keywords "test,mock,coverage,e2e,jest,vitest,playwright"
   ```
2. Read `AGENTS.md §2` (test framework) and `§7` (external services to mock)

Requirements:
- Load `testing-qa` SKILL.md; load framework test references from skill-loader output if needed
- Mock all external services listed in `AGENTS.md §7` (never hit real APIs in tests)
- Multi-tenancy isolation cases if `AGENTS.md §5` declares multi-tenancy
- Follow naming convention from `AGENTS.md §2` (e.g. `*.spec.ts`, `*.test.ts`, `*.e2e-spec.ts`)
- Coverage target: 70%+ for service/business logic layers (see `AGENTS.md §6`)

Output complete test file(s).
