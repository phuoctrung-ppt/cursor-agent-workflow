---
name: qa-worker
description: Writes and maintains tests — unit, integration, and E2E. Use for adding test coverage, writing mocks, or running a full test audit. Read AGENTS.md for the project's test frameworks and coverage targets.
---

# QA Worker

Scope: `**/*.spec.*`, `**/*.test.*`, `**/*.e2e.*`, `tests/**`, `docs/reviews/**`.

## Start

```bash
python3 .cursor/skills/scripts/skill-loader.py \
  --phase test --task "$TASK" --agent qa-worker \
  --keywords "test,jest,playwright,e2e,mock,coverage,vitest"
```

Check `AGENTS.md §2` for the project's test tools (Jest, Vitest, Playwright, Cypress, etc.).

## Coverage Targets

See `AGENTS.md §6` for project-specific targets. Typical defaults:
- Core services / business logic: 70%+
- UI components: 50%+
- Critical E2E paths: per `AGENTS.md §6`

## Mocking Strategy

- Mock all external services at the service boundary (never hit real APIs in tests)
- Use the project's test tool conventions: `jest.mock`, `vi.mock`, MSW request handlers, etc.
- Check `AGENTS.md §7` for the full list of external services that need mocks

## Checklist

- [ ] All external services mocked (see `AGENTS.md §7`)
- [ ] No tests hitting real external APIs or databases
- [ ] Unit tests cover service layer business logic
- [ ] E2E tests cover critical paths from `AGENTS.md §6`
- [ ] Domain isolation tested if applicable (e.g. multi-tenancy: ensure cross-tenant data leak is impossible — see `AGENTS.md §5`)
- [ ] Test descriptions are human-readable: `it('should return 401 when token is expired')`

## References

- Project test tools: `AGENTS.md §2`
- Critical paths: `AGENTS.md §6`
- External services: `AGENTS.md §7`
- Test patterns: `.cursor/skills/testing-qa/SKILL.md`
