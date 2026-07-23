# Audit Logging

Every mutating admin action → `admin.admin_audit_logs`:

```typescript
{ admin_user_id, action, target_type, target_id, old_values, new_values, ip_address, user_agent }
```

Use `@AuditAction('tenant:update')` decorator + interceptor.
Fetch `old_values` before update for accurate diff.
