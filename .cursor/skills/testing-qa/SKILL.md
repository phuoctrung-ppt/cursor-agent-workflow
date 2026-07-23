---
name: testing-qa
description: Writes unit tests, integration tests, and Playwright E2E tests with external API mocks. Use for any project needing test coverage. Read AGENTS.md for the project's test framework, coverage targets, and critical E2E paths.
---

# Testing & QA

## Stack

Check `AGENTS.md §2` (Testing) for the project's chosen tools. Common defaults:

- **Unit**: Jest or Vitest
- **Integration**: Supertest (Node) or equivalent
- **E2E**: Playwright or Cypress
- **Mocks**: `jest.mock` / `vi.mock` / MSW for external services

See `AGENTS.md §7` for the full list of external services that need mocks in this project.

## Coverage Targets

See `AGENTS.md §6` for project-specific targets. Typical defaults:
- Core services / business logic: 70%+
- UI components: 50%+
- Critical E2E paths: per `AGENTS.md §6`

## E2E Critical Paths

Document your critical E2E flows in `AGENTS.md §6`. These become the Playwright test targets.

## References

- [jest-setup.md](references/jest-setup.md)
- [playwright-e2e.md](references/playwright-e2e.md)
- [mocking-patterns.md](references/mocking-patterns.md)

Framework test references: load from skill-loader output (e.g. `nestjs-skills/references/test-*.md` for NestJS).

## Agent

`@qa-worker` | Command: `/generate-test`
