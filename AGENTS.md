# AGENTS.md — <PROJECT_NAME>

> **TEMPLATE — DOMAIN-NEUTRAL.** This repo ships the portable Planner-Worker-Judge workflow with **no** target domain.
> Replace every `<PLACEHOLDER>` and every block tagged `> _EXAMPLE_` with your project's real values when you port this setup.
> **Agents:** if a section below is still a `<PLACEHOLDER>`, treat that fact as *unknown* — gather it from the codebase or ask the orchestrator. **Never invent stack, structure, or compliance facts from an example block.**

> **How to use this file:** This is the canonical domain-config hub for the agentic workflow.
> Every agent reads this file at task start. Generic workflow rules, hooks, and skills live in `.cursor/` and do not need editing when you port this setup to a new repo.
> Only this file and the config JSONs below need updating when adding new features:
> - `.cursor/config/protected-paths.json` → `projectProtectedGlobs`
> - `.cursor/config/worker-scopes.json` → `agents` section
> - `.cursor/skills/skills-manifest.json` → add/remove domain skills

---

**IMPORTANT** : Always follow the development rules during the coding phase. See `./docs/development-rules.md`.

## 1. Project Overview

| Field | Value |
|---|---|
| **Project Name** | `<name>` |
| **Domain** | `<domain / industry>` |
| **Description** | `<one-sentence description of what the product does>` |
| **Monorepo** | `<yes (tool: nx / turbo / pnpm-workspaces) | no>` |
| **Multi-Tenancy** | `<none | soft (tenant column) | hard (schema/RLS per tenant)>` |

---

## 2. Tech Stack (Locked — ADR required to change)

> Fill one row per layer your project uses; delete rows that don't apply. State a version only when it is actually pinned. Once filled, changing a locked choice requires an ADR in `docs/adr/`.

| Layer | Technology | Notes |
|---|---|---|
| Language | `<e.g. TypeScript (strict)>` | |
| Backend framework | `<...>` | |
| Frontend framework | `<...>` | |
| Shared contracts | `<schema/validation lib, e.g. Zod>` | source of truth for API types |
| Database | `<...>` | |
| ORM / Migrations | `<...>` | migrations only — no auto-sync |
| Cache / Queue | `<...>` | |
| AI / LLM | `<provider(s) | none>` | |
| Object storage | `<...>` | |
| Auth | `<...>` | |
| Email / Notifications | `<...>` | |
| Payments | `<... | none>` | |
| Infra / Deploy | `<...>` | |
| Testing | `<unit / integration / e2e frameworks>` | |

---

## 3. Repository Structure

> Describe the actual layout of THIS repo. Keep it in sync with `.cursor/config/worker-scopes.json` (agent path scopes must match real folders).

```
<root>/
├── <app-or-package-1>/        # <role>
├── <app-or-package-2>/        # <role>
├── docs/                      # plans, adr, reviews, architecture
└── .cursor/                   # workflow: agents, skills, hooks, config
```

> _EXAMPLE_ (delete when porting): a monorepo might use `apps/api`, `apps/web`, `apps/worker`, `packages/shared-types`. Whatever you choose, mirror it exactly in `worker-scopes.json`.

---

## 4. Multi-Tenancy Rules

> **Applies only if §1 Multi-Tenancy ≠ `none`.** If single-tenant, write "N/A — single-tenant" and skip the guard requirements below.

### Tenant Isolation Pattern

Choose and document your tenant column name (e.g. `tenant_id`, `workspace_id`, `org_id`). Every table that belongs to a tenant **MUST** carry `<TENANT_COL> NOT NULL` with an FK to the tenant table.

- **Tenant-scoped tables:** `<list here>`
- **Global / non-tenant tables:** `<list here>`

### Tenant Guard (mandatory on every tenant-scoped query)

> _EXAMPLE_ pattern — adapt to your framework/ORM:

```typescript
// Every tenant-scoped read MUST filter by the tenant column and select explicit columns:
async findRecords(tenantId: string): Promise<Record[]> {
  return this.repo.find({
    where: { tenantId },            // ALWAYS filter by tenant
    select: ['id', 'name', 'status', 'createdAt'], // NEVER select *
  });
}
```

> ❗ **NEVER write a tenant-scoped query without a tenant filter — no exceptions, not even in admin convenience methods, unless an explicit, logged override flag is used.**

---

## 5. Agent Roster & Scopes

> Roles below are the portable defaults shipped in `.cursor/agents/`. **Path scopes and skills are defined in `.cursor/config/worker-scopes.json` and `.cursor/skills/skills-manifest.json`** — keep those two files as the source of truth and update this table to match. Remove agents you don't use.

| Agent | Role | Scope source | Skills source |
|---|---|---|---|
| `architect-planner` | Plan, ADR, task breakdown, scope definition | `worker-scopes.json` | `skills-manifest.json` |
| `scaffold-agent` | Bootstrap new module/page shells; update §3 paths | `worker-scopes.json` | `skills-manifest.json` |
| `designer-worker` | UI/UX design, component specs, design tokens | `worker-scopes.json` | `skills-manifest.json` |
| `backend-worker` | API features, services, DTOs, guards | `worker-scopes.json` | `skills-manifest.json` |
| `frontend-worker` | Pages, forms, data fetching, client state | `worker-scopes.json` | `skills-manifest.json` |
| `database-worker` | Migrations, entities, query optimization | `worker-scopes.json` | `skills-manifest.json` |
| `ai-worker` | LLM/AI integration, embeddings, cost tracking (if any) | `worker-scopes.json` | `skills-manifest.json` |
| `devops-worker` | Docker, CI/CD, infra | `worker-scopes.json` | `skills-manifest.json` |
| `security-worker` | Auth, RBAC, encryption, rate limiting | `worker-scopes.json` | `skills-manifest.json` |
| `qa-worker` | Unit / integration / E2E tests | `worker-scopes.json` | `skills-manifest.json` |
| `admin-worker` | Admin/control-plane elevated APIs & UI (if any) | `worker-scopes.json` | `skills-manifest.json` |
| `judge-agent` | Read-only review gate for protected changes | `docs/reviews/**` | `skills-manifest.json` |

> Add/remove domain worker agents (e.g. a queue/worker-process agent) to match your stack. Every agent you list here must have a matching entry in `worker-scopes.json`.

---

## 6. Domain-Specific Compliance Requirements

> Fill each subsection with YOUR project's rules. The categories are generic; the values below are placeholders. Delete subsections that don't apply.

### Authentication & Authorization

- Every endpoint is **explicitly** public or protected — no ambiguity. Public routes use an explicit `<@Public()>`-equivalent marker.
- Token strategy: `<e.g. JWT access + rotating refresh; describe TTLs, storage, rotation>`.
- RBAC roles: `<list your roles>`. Authorization enforced via `<guard/middleware mechanism>`.

### Multi-Tenancy (if applicable)

- Tenant filter is **required** on every tenant-scoped query (see §4).
- Never expose another tenant's data — even in debug/admin code — without a logged override.

### Data Privacy & Compliance

- Applicable regimes: `<e.g. GDPR / CCPA / HIPAA / none>`.
- PII handling: `<what is PII here; never log it in raw form>`.
- Data retention / deletion: `<policy>`.
- Never log: passwords, tokens, API keys, payment data, or PII.

### AI / LLM Rules (only if §2 AI/LLM ≠ none)

- Log every LLM call to `<your usage/audit table>`; enforce cost budget where required.
- Never pass raw user input into a prompt — sanitize and wrap it in a structured template; escape template delimiters.
- Ground responses ("answer only from provided context"); validate/sanitize model output before returning it.

### Rate Limiting

> _EXAMPLE_ table — replace categories and limits with yours:

| Endpoint Category | Limit | Scope |
|---|---|---|
| `<auth>` | `<n req/min>` | `<per IP>` |
| `<expensive/AI op>` | `<n req/min>` | `<per user>` |
| `<upload>` | `<n req/min>` | `<per user>` |

---

## 7. Critical Paths (E2E flow targets)

> List the end-to-end user flows that MUST have an E2E test before a feature is "Done". These are your Playwright/E2E targets.

- `<Flow 1: e.g. sign up → verify → first core action>`
- `<Flow 2>`
- `<Flow 3>`

---

## 8. External Services & Mocking Rules

> List every third-party service and how tests mock it. Delete the example rows.

| Service | Purpose | Mock in tests? | Mock Strategy |
|---|---|---|---|
| `<service>` | `<purpose>` | `<yes/no>` | `<how it is mocked>` |

> _EXAMPLE_: `Payments provider → checkout → yes → provider test mode + webhook test events`.

---

## 9. Database Entities Reference

> List core entities/tables with their tenant scoping. Keep names generic to your domain.

| Entity | Tenant-scoped? | Notes |
|---|---|---|
| `<entity>` | `<yes/no>` | `<key fields, relationships>` |

---

## 10. Workflow Artifacts

| Artifact Type | Path Pattern | Required For |
|---|---|---|
| Feature plans | `docs/plans/YYYY-MM-DD-feature-name.md` | Any change touching > 1 file or > 50 lines |
| ADRs | `docs/adr/NNNN-short-title.md` | Tech stack changes, architecture patterns, infra decisions |
| Design specs | `docs/design/YYYY-MM-DD-{feature}.md` | Any new/changed UI (design-first gate) |
| Design sketches | `docs/design/sketches/{feature}/` | Visual mockups for UI features (generated via taste-design) |
| Judge reviews | `docs/reviews/YYYY-MM-DD-description.md` | Protected-path changes (auth, billing, DB migrations, config) |
| Review overrides | `docs/reviews/review-overrides.log` | Manual bypass of the judge gate (reason must be logged) |
| User Stories | `docs/user-stories/` | Source of truth for acceptance criteria |

---

## 11. Git Conventions

- **Commits:** Conventional Commits — `type(scope): description` (`feat` / `fix` / `chore` / `refactor` / `docs` / `test`).
  - Example: `feat(<module>): <what changed>`
  - Example: `fix(<module>): <bug fixed>`
- **Branches:** `feature/<ticket>-short-description` | `fix/<ticket>-bug-name` | `chore/update-deps`
- **PR size:** keep PRs small (target ≤ ~400 lines). Split large features by layer: DB → API → Frontend.
- **PR template:** must include story/ticket reference, test plan, and screenshot/video if UI changed.
- **Protected branches:** `<main / develop>` — require PR + at least 1 review.
- **Deploy order:** `<staging> → verify → <production>`. Never deploy straight to production.

---

## 12. Forbidden Patterns (Agents must NEVER do)

> Generic defaults below apply to most stacks. Items in _(stack-specific)_ are examples — adjust to §2.

### Database
- ❌ Auto-sync/auto-migrate schemas in staging or production — migrations only.
- ❌ `DROP TABLE`/destructive migration without a matching `down()` rollback.
- ❌ Query tenant-scoped data without the tenant filter (see §4).
- ❌ `SELECT *` in production queries — use explicit column lists.
- ❌ N+1 queries — use eager loading / batching.

### Security
- ❌ Log secrets, tokens, passwords, API keys, or PII in any sink (console, APM, error tracker).
- ❌ Commit `.env` files or put real values in `.env.example`.
- ❌ Return password hashes or secrets in API responses.
- ❌ String-interpolate user input into queries — use parameterized queries / the ORM.
- ❌ Pass raw user content into LLM prompts without sanitizing and wrapping it.

### Code Quality
- ❌ Ad-hoc `console.log` in production code — use the project's structured logger _(stack-specific)_.
- ❌ `any` in TypeScript without an eslint-disable + justification — prefer `unknown` + guards.
- ❌ Hardcode URLs, endpoints, or secrets — use the config layer _(stack-specific)_.
- ❌ Business logic in controllers/route handlers — logic belongs in services.
- ❌ Silent catches — always re-throw or log.

### AI / LLM (if applicable)
- ❌ Call an LLM without try/catch and a fallback path.
- ❌ Skip logging AI usage to your usage table.
- ❌ Omit the grounding constraint from prompts.
- ❌ Return raw model output without validation/sanitization.

### Infrastructure
- ❌ Deploy to production without passing staging first.
- ❌ Change SSL/domain config without testing on staging first.

---

## 13. Environment Variables (Required)

> ⚠️ Never commit `.env` files. Use a secret manager for production. List NAMES only here — never values.

```env
# <VAR_NAME>=            # <what it is; required by which service>
# Example categories: database URL, cache/queue URL, auth secrets,
# third-party API keys, storage credentials, app base URLs.
```

---

## 14. Queue / Background Jobs

> Only if your stack uses a job queue. Otherwise write "N/A".

| Queue Name | Processor | Concurrency | Priority | Notes |
|---|---|---|---|---|
| `<queue>` | `<processor>` | `<n>` | `<High/Normal/Low>` | `<what it does>` |

---

## 15. API Naming Convention

> Define your API surface conventions so all workers stay consistent.

- **Style:** `<REST | GraphQL | RPC>`
- **Resource paths:** `<e.g. /api/v1/<plural-nouns>; kebab-case>`
- **Versioning:** `<e.g. URL prefix /v1>`
- **Response envelope:** `<e.g. { data, meta, error }>`
- **Status codes:** `<the set you standardize on>`
- **Pagination:** `<cursor | offset; params>`
