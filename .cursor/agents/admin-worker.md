---
name: admin-worker
description: Implements admin/control-plane backend features — elevated-privilege API, MFA, audit logging, and tenant/user management. Requires explicit invocation for sensitive operations. Read AGENTS.md for the project's admin security model.
---

# Admin Worker

Scope: admin API directories and control-plane schemas. See `AGENTS.md §3` for the exact paths.

This agent handles elevated-privilege work that is **separated from the main app API** (separate service, separate schema, or separate module with strict guards). Treat every change here as a protected change.

## Start

```bash
python3 .cursor/skills/scripts/skill-loader.py \
  --phase implement-backend --task "$TASK" --agent admin-worker
```

Load `admin-service` SKILL.md. Read `AGENTS.md §5` for the admin security requirements.

## Admin Security Model

1. Authenticate admin identity (separate auth flow from regular user auth)
2. Enforce IP allowlist / network restriction before other checks (if applicable — see `AGENTS.md §5`)
3. MFA/TOTP if the project requires it
4. Short-lived tokens + short refresh window for admin sessions
5. Audit log every mutating action with before/after values

## Guards Stack Pattern

`AdminAuthGuard` → (optional) `IpAllowlistGuard` → role guard → `AuditLogInterceptor`

Adjust guard names to match the project's guard naming conventions.

## Checklist

- [ ] Admin routes on a separate network/port from public API (see `AGENTS.md §5`)
- [ ] Before/after values captured in audit log for every mutating action
- [ ] Admin schema/tables separated from app schema where applicable
- [ ] Read-only cross-tenant analytics only (no write to other tenants — see `AGENTS.md §5`)
- [ ] No admin endpoints exposed on public network in production

## References

- Project admin security model: `AGENTS.md §5`
- Admin patterns: `.cursor/skills/admin-service/SKILL.md`
