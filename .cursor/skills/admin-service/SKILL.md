---
name: admin-service
description: Implements admin API features — MFA, IP whitelist, audit logging, tenant management, billing, AI cost analytics in apps/admin. Sensitive control-plane operations.
disable-model-invocation: true
---

# Admin Service Skill

**User-invoked only** — admin operations are sensitive.

## When to Use

- `apps/admin` endpoints
- MFA, IP whitelist, audit logs
- Tenant/billing management
- Dead letter queue inspection

## Auth Flow

Email+Password → IP whitelist → TOTP MFA → JWT 30m + refresh 2h

## Guard Stack

`AdminAuthGuard` + `IpWhitelistGuard` + role guard + `AuditLogInterceptor`

## Roles

`SUPER_ADMIN`, `BILLING_ADMIN`, `SUPPORT_ADMIN`, `SECURITY_ADMIN`

## References

- [mfa-implementation.md](references/mfa-implementation.md)
- [audit-logging.md](references/audit-logging.md)
- [ip-whitelist.md](references/ip-whitelist.md)

## Agent

`@admin-worker` | Design templates in `AI_Career_Platform_Agent_System_Design_v1.0.md` §3.4
