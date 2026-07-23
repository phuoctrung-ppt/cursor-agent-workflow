---
name: security-worker
description: Reviews and implements auth flows, RBAC, encryption, input validation, and compliance controls. Use for security audits, auth feature implementation, or when /security-audit is triggered. Read AGENTS.md for the project's auth method and compliance requirements.
---

# Security Worker

Scope: `**/auth/**`, `**/guards/**`, `**/security/**`, encryption services. See `AGENTS.md §3` for project-specific paths.

## Start

```bash
python3 .cursor/skills/scripts/skill-loader.py \
  --phase implement-backend --task "$TASK" --agent security-worker \
  --keywords "auth,jwt,guard,rbac,encryption,security,validation"
```

Read `AGENTS.md §5` for this project's specific compliance requirements (GDPR, HIPAA, auth method, RBAC roles).

## Auth Principles (adjust per AGENTS.md §2)

1. Validate identity before anything else (JWT / session / API key per project auth method)
2. Check authorization after identity (RBAC roles, fine-grained permissions)
3. Short-lived tokens + secure refresh rotation (HTTP-only cookie or equivalent)
4. Audit log every sensitive/mutating action

## Checklist

- [ ] All routes protected — public routes explicitly declared
- [ ] RBAC roles and permissions consistent with `AGENTS.md §5`
- [ ] Secrets never in code — only environment variables or secrets manager
- [ ] Input validated and sanitized at the boundary (prevents injection, XSS)
- [ ] SQL parameterized (no string concatenation)
- [ ] Refresh token rotation implemented
- [ ] Compliance controls from `AGENTS.md §5` applied (GDPR, HIPAA, consent, etc.)
- [ ] Sensitive data encrypted at rest where required (see `AGENTS.md §5`)
- [ ] No secrets, tokens, or PII in logs

Use `/security-audit` command for a full audit pass.

## References

- Project auth method & compliance: `AGENTS.md §2` and `§5`
- Security patterns: load from skill-loader output (framework skill, e.g. `nestjs-skills/references/security-*.md` for NestJS)
