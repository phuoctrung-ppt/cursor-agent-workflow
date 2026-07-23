# IP Whitelist

- `ADMIN_IP_WHITELIST` env: comma-separated CIDRs
- `IpWhitelistGuard` runs BEFORE password validation
- Nginx layer also whitelists admin routes in production
- Log rejected IPs to security audit
