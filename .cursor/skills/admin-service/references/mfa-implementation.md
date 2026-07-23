# MFA Implementation

- TOTP via `speakeasy` or equivalent
- `mfa_verified` claim in JWT payload after OTP validation
- `AdminAuthGuard` rejects if MFA required for role and claim missing
- Store `mfa_secret` encrypted; enable/disable via admin settings
