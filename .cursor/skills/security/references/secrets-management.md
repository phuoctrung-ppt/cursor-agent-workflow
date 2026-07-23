# Secrets Management — Generic Reference

Secrets are API keys, database passwords, JWT secrets, encryption keys, and any credential that grants access to a system. They must never appear in source code, logs, or error messages.

---

## The Rules (Non-Negotiable)

```
❌ Never:                           ✅ Always:
  Hardcode in source code             Use environment variables
  Commit to git (even private)        Use .env files locally (gitignored)
  Log secrets                         Use a secrets manager in production
  Put in error messages               Rotate secrets regularly
  Store in localStorage               Use short-lived credentials where possible
  Email or Slack secrets              Audit secret access
```

---

## Local Development — .env Pattern

```bash
# .env.example — commit this file with fake/placeholder values
DATABASE_URL=postgresql://postgres:changeme@localhost:5432/myapp
REDIS_URL=redis://localhost:6379
JWT_SECRET=changeme_use_32_plus_chars_in_production
STRIPE_SECRET_KEY=sk_test_placeholder
OPENAI_API_KEY=sk-placeholder
AWS_ACCESS_KEY_ID=placeholder
AWS_SECRET_ACCESS_KEY=placeholder

# .env — NEVER commit this file
# Listed in .gitignore
DATABASE_URL=postgresql://postgres:real_pass@localhost:5432/myapp
JWT_SECRET=f3a9b2c8d7e6f1a0b9c8d7e6f1a0b9c8d7e6f1a0b9c8d7e6f1a0b9c8d7e6f
STRIPE_SECRET_KEY=sk_live_real_key_here
```

```bash
# .gitignore
.env
.env.local
.env.*.local
*.pem
*.key
*.p12
*.pfx
secrets/
```

---

## Reading Secrets (Application Code)

```typescript
// config/env.ts — validate all required env vars at startup
// Fail fast: if a required secret is missing, crash immediately with a clear error

import { z } from 'zod';

const envSchema = z.object({
  DATABASE_URL:      z.string().url(),
  REDIS_URL:         z.string().url(),
  JWT_SECRET:        z.string().min(32, 'JWT_SECRET must be at least 32 characters'),
  STRIPE_SECRET_KEY: z.string().startsWith('sk_'),
  NODE_ENV:          z.enum(['development', 'test', 'production']).default('development'),
});

export const env = envSchema.parse(process.env);
// If any required var is missing → throws with a clear error message at startup

// Usage: import { env } from './config/env';
// Never: process.env.JWT_SECRET directly (bypasses validation)
```

---

## Production — Secrets Managers

### AWS Secrets Manager

```typescript
import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager';

const client = new SecretsManagerClient({ region: 'us-east-1' });

async function getSecret(secretName: string): Promise<Record<string, string>> {
  const response = await client.send(new GetSecretValueCommand({ SecretId: secretName }));
  return JSON.parse(response.SecretString!);
}

// Fetch at startup, cache in memory — don't fetch on every request
let secrets: Record<string, string>;
async function initSecrets() {
  secrets = await getSecret('myapp/production');
  // Schedule rotation check: re-fetch periodically for auto-rotation
}
```

### HashiCorp Vault

```bash
# Set a secret
vault kv put secret/myapp/production \
  db_password="real_password" \
  jwt_secret="real_jwt_secret"

# Get a secret (in app startup script)
SECRETS=$(vault kv get -format=json secret/myapp/production)
export DB_PASSWORD=$(echo $SECRETS | jq -r '.data.data.db_password')
```

### Kubernetes Secrets

```yaml
# kubernetes/secret.yaml — base64 encoded values
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secrets
type: Opaque
data:
  jwt-secret: <base64-encoded-value>
  db-password: <base64-encoded-value>

# Reference in deployment
env:
  - name: JWT_SECRET
    valueFrom:
      secretKeyRef:
        name: myapp-secrets
        key: jwt-secret
```

---

## CI/CD Secrets

```yaml
# GitHub Actions — use repository secrets
# Add secrets at: Settings > Secrets and variables > Actions

- name: Deploy
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    JWT_SECRET:   ${{ secrets.JWT_SECRET }}
  run: ./deploy.sh

# ❌ Never
env:
  DATABASE_URL: postgresql://user:password@host/db  # hardcoded in workflow file
```

---

## Secret Scanning (Prevent Accidental Commits)

```bash
# Install git-secrets (AWS) — blocks commits containing secrets
git secrets --install
git secrets --register-aws

# Or use detect-secrets (Yelp)
pip install detect-secrets
detect-secrets scan > .secrets.baseline
# Add to pre-commit hook

# TruffleHog — scan git history for secrets
trufflehog git file://. --since-commit HEAD~50 --only-verified

# GitHub Advanced Security — enable "Secret scanning" in repo settings
# (automatically scans push events for 200+ credential patterns)
```

---

## Secret Rotation

```typescript
// Build apps to support secret rotation without downtime
// Pattern: accept both old and new secrets during rotation window

class JwtService {
  private readonly secrets: string[];

  constructor() {
    // Support multiple secrets — rotate by adding new at front, removing old later
    this.secrets = [
      process.env.JWT_SECRET!,
      process.env.JWT_SECRET_PREVIOUS!, // keep for ~15min (existing token lifetime)
    ].filter(Boolean);
  }

  verify(token: string): jwt.JwtPayload {
    for (const secret of this.secrets) {
      try {
        return jwt.verify(token, secret) as jwt.JwtPayload;
      } catch {
        continue; // try next secret
      }
    }
    throw new UnauthorizedException('Invalid token');
  }

  sign(payload: object): string {
    return jwt.sign(payload, this.secrets[0], { expiresIn: '15m' }); // always sign with newest
  }
}
```

---

## Audit Checklist

```bash
# 1. Check for hardcoded secrets in source
grep -r "password\|secret\|apikey\|api_key" --include="*.ts" --include="*.py" src/ \
  | grep -v "process.env\|env\.\|config\.\|placeholder\|changeme\|test\|mock"

# 2. Verify .gitignore covers .env files
git check-ignore -v .env
git check-ignore -v .env.local

# 3. Check git history for accidentally committed secrets
git log --all --full-history -- "*.env"
git log --all --full-history -- "**/.env"

# 4. Verify env vars are validated at startup (not silently missing)
NODE_ENV=production node -e "require('./dist/config/env')"
```
