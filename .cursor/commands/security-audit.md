---
name: security-audit
description: Audit code for OWASP issues, secrets, auth gaps, data isolation, and injection risks
---

Act as **Security Worker** + **Judge Agent** security checklist.

Audit: {code_path_or_diff}

Read `AGENTS.md §5` for this project's specific compliance requirements (auth method, RBAC roles, multi-tenancy, GDPR/HIPAA, etc.) before auditing.

Check:
1. SQL injection (string interpolation in SQL — must use parameterized queries)
2. XSS (unescaped user-controlled HTML in output)
3. Hardcoded secrets, API keys, or credentials
4. Missing input validation at route/controller boundary
5. Missing auth guards on routes (public routes must be explicitly declared)
6. Data isolation gaps — if `AGENTS.md §5` declares multi-tenancy or row-level security, check that all queries are correctly scoped
7. Business logic in controllers instead of service/domain layer
8. Rate limiting missing on sensitive endpoints (auth, password reset, AI calls)
9. PII stored or logged unencrypted (check `AGENTS.md §5` for PII fields)
10. Weak password / token policies
11. RBAC checks match roles defined in `AGENTS.md §5`
12. Domain compliance controls from `AGENTS.md §5` applied (GDPR, HIPAA, consent, AI ethics)

Output: issues with severity (CRITICAL/HIGH/MEDIUM/LOW), file paths, line numbers, recommended fixes.
