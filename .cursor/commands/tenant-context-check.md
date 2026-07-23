---
name: tenant-context-check
description: "[DOMAIN EXAMPLE] Audits multi-tenancy isolation for projects using soft multi-tenancy via tenant_id. Only activate if AGENTS.md §5 declares multi-tenancy. Generic projects do not need this command."
---

> **Domain example** — this command is for multi-tenant projects that use `tenant_id` column isolation
> (see `.cursor/rules/004-multi-tenancy-pattern.mdc`). Skip this command if your project is
> single-tenant or uses a different isolation model. Adapt the checklist to match `AGENTS.md §5`.

Audit tenant isolation for: {code_path}

Per `.cursor/rules/004-multi-tenancy-pattern.mdc` and `AGENTS.md §5`:

1. All tenant-scoped tables have `tenant_id` (or are explicitly marked as global)
2. Tenant guard applied on every tenant-scoped route
3. Every query that touches tenant-scoped data filters by `tenant_id`
4. No cross-tenant data leaks in API responses
5. Global/shared entities (users, roles, etc.) have `tenant_id` NULL or use a global flag per `AGENTS.md §5`
6. Soft limits (quotas) return 403 with an appropriate upgrade/contact prompt

Output: PASS/FAIL with file:line issues.
