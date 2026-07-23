---
name: security
description: Portable security skill covering OWASP Top 10, authentication patterns, authorization/RBAC, input validation, secrets management, and rate limiting. Use for any project needing security review, auth implementation, or compliance hardening. Load with security-worker or judge-agent. Read AGENTS.md §5 for project-specific compliance requirements.
---

# Security Skill

Universal security patterns and checks. All project-specific compliance requirements (GDPR, HIPAA, RBAC roles, multi-tenancy isolation) are in `AGENTS.md §5`.

---

## When to Use This Skill

- Implementing authentication or authorization
- Reviewing code for security vulnerabilities
- Running a security audit (`/security-audit`)
- Adding rate limiting, input validation, or encryption
- Hardening a service before production

---

## OWASP Top 10 Quick Reference

| # | Risk | Key mitigation |
|---|---|---|
| A01 | Broken Access Control | Check permissions on every request, deny by default |
| A02 | Cryptographic Failures | Encrypt PII at rest, TLS in transit, never roll your own crypto |
| A03 | Injection | Parameterized queries, ORM only, never string interpolation in SQL |
| A04 | Insecure Design | Threat model early; security by design not afterthought |
| A05 | Security Misconfiguration | Disable defaults, remove debug endpoints, lock down CORS |
| A06 | Vulnerable Components | `npm audit`, `pip-audit`, dependabot — keep deps updated |
| A07 | Auth/Session Failures | HttpOnly cookies, rotate tokens, secure session management |
| A08 | Software Integrity Failures | Verify dependencies (lockfiles), signed containers, CI integrity |
| A09 | Logging Failures | Log security events, never log secrets/PII, centralize logs |
| A10 | SSRF | Allowlist outbound URLs, block internal CIDR ranges |

See [owasp-top10.md](references/owasp-top10.md) for implementation details.

---

## Authentication Checklist

- [ ] JWT signed with RS256 (asymmetric) or HS256 with strong secret (≥256 bit)
- [ ] Access tokens short-lived (15min); refresh tokens long-lived but rotatable
- [ ] Refresh token rotation — invalidate old token on use (detect token theft)
- [ ] HttpOnly + Secure + SameSite=Strict cookies for web — never localStorage for tokens
- [ ] Passwords hashed with bcrypt/argon2 (min cost factor 12)
- [ ] MFA available for elevated-privilege accounts (per `AGENTS.md §5`)
- [ ] Account lockout after N failed attempts (with exponential backoff)

See [auth-patterns.md](references/auth-patterns.md) for JWT implementation.

---

## Authorization / RBAC Checklist

- [ ] All routes require authentication by default; public routes explicitly declared
- [ ] Role check on every operation — not just at the route level
- [ ] Roles defined in `AGENTS.md §5`; no hardcoded role strings outside config
- [ ] Resource ownership verified: user can only access their own data
- [ ] Admin actions logged with actor identity (who did what, when)
- [ ] Principle of least privilege — services only have permissions they need

---

## Input Validation Checklist

- [ ] Validate at the API boundary — never trust client input
- [ ] Schema-first: use Zod, Joi, class-validator, Pydantic, etc.
- [ ] Strict type coercion — don't silently accept wrong types
- [ ] Whitelist allowed values (enums) rather than blacklisting bad values
- [ ] File upload: check MIME type and file size; scan for malware if sensitive
- [ ] GraphQL: depth/complexity limits to prevent DoS queries

---

## Secrets Management Checklist

- [ ] Secrets only in environment variables, never in source code
- [ ] `.env` in `.gitignore`; `.env.example` with placeholder values committed
- [ ] Production secrets in a secrets manager (AWS Secrets Manager, Vault, GCP Secret Manager)
- [ ] Secret rotation policy defined and tested
- [ ] No secrets in logs, error messages, or API responses
- [ ] CI/CD secrets in platform secret store (GitHub Actions secrets, not env vars in YAML)

See [secrets-management.md](references/secrets-management.md) for patterns.

---

## Common Vulnerabilities Checklist (Code Review)

```
[ ] SQL injection: parameterized queries everywhere, no string interpolation
[ ] XSS: sanitize HTML output; never dangerouslySetInnerHTML with user content
[ ] CSRF: SameSite cookies or CSRF token for state-changing forms
[ ] Path traversal: never use user input in file paths without sanitization
[ ] ReDoS: avoid complex regex with user input; use linear-time regex engines
[ ] Prototype pollution: validate JSON carefully, use Object.create(null)
[ ] Mass assignment: explicitly allow only known fields in create/update
[ ] Open redirect: whitelist redirect URLs; never trust user-supplied redirect params
[ ] SSRF: validate/allowlist outbound URLs; block 169.254.x.x (metadata) and RFC1918
```

---

## Rate Limiting

- Apply to: auth endpoints, API endpoints, LLM calls, file uploads, email sending
- Strategy: sliding window or token bucket
- Limits by: IP, user ID, API key, or tenant
- Response: `429 Too Many Requests` with `Retry-After` header
- See `AGENTS.md §5` for project-specific rate limit values

---

## Encryption

```
At rest:
  - PII fields: AES-256-GCM (symmetric), key in KMS
  - Database: disk encryption (cloud provider managed)
  - Backups: encrypted before upload

In transit:
  - TLS 1.2+ everywhere, TLS 1.3 preferred
  - HSTS header on all web responses
  - No HTTP in production (redirect all to HTTPS)
  - mTLS for internal service-to-service if sensitive
```

---

## Security Headers (Web APIs)

```
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

## References

- [owasp-top10.md](references/owasp-top10.md) — implementation guidance per vulnerability class
- [auth-patterns.md](references/auth-patterns.md) — JWT, refresh tokens, session management
- [secrets-management.md](references/secrets-management.md) — env vars, secret managers, rotation

## Agent

`@security-worker` | Command: `/security-audit`
