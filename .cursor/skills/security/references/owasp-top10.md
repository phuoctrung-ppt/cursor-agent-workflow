# OWASP Top 10 — Implementation Guide

Practical mitigations for each OWASP Top 10 vulnerability class. Adapt code examples to your stack.

---

## A01 — Broken Access Control

**Impact:** Users access other users' data, escalate privileges, reach admin functions.

```typescript
// ✅ Check ownership on every resource fetch
async getDocument(id: string, requestingUserId: string): Promise<Document> {
  const doc = await this.repo.findOne({ where: { id } });
  if (!doc) throw new NotFoundException();
  if (doc.ownerId !== requestingUserId) throw new ForbiddenException();  // ownership check
  return doc;
}

// ✅ Deny by default — require explicit permission grant
// Never: if (user.role !== 'banned') { allow }
// Always: if (user.role === 'admin' || user.id === resource.ownerId) { allow }

// ❌ Insecure direct object reference — trusting client-supplied ID
async getDocument(id: string) {
  return this.repo.findOne({ where: { id } }); // no ownership check!
}
```

**Checklist:**
- [ ] JWT/session validated on every request (not just login)
- [ ] Resource ownership checked before read/write/delete
- [ ] Admin endpoints protected by role guard, not just authenticated
- [ ] No client-side-only access control (always verify server-side)

---

## A02 — Cryptographic Failures

```typescript
// ✅ Password hashing — bcrypt with cost factor ≥ 12
import bcrypt from 'bcrypt';
const SALT_ROUNDS = 12;
const hash = await bcrypt.hash(password, SALT_ROUNDS);
const valid = await bcrypt.compare(password, storedHash);

// ✅ Symmetric encryption of PII (AES-256-GCM)
import { createCipheriv, createDecipheriv, randomBytes } from 'crypto';
function encrypt(plaintext: string, key: Buffer): { iv: string; ciphertext: string; tag: string } {
  const iv = randomBytes(12);
  const cipher = createCipheriv('aes-256-gcm', key, iv);
  const ciphertext = Buffer.concat([cipher.update(plaintext, 'utf8'), cipher.final()]);
  return {
    iv: iv.toString('hex'),
    ciphertext: ciphertext.toString('hex'),
    tag: cipher.getAuthTag().toString('hex'),
  };
}

// ❌ Never
const hash = require('crypto').createHash('md5').update(password).digest('hex'); // MD5 is broken
const hash = crypto.createHash('sha1').update(password).digest('hex');           // SHA1 too fast
```

---

## A03 — Injection (SQL, Command, Template)

```typescript
// ✅ Parameterized queries — always
const user = await db.query('SELECT * FROM users WHERE id = $1', [userId]);

// ✅ ORM (TypeORM, Prisma, SQLAlchemy) — uses parameterized queries by default
const user = await userRepo.findOne({ where: { id: userId } });

// ❌ String interpolation — SQL injection vulnerability
const user = await db.query(`SELECT * FROM users WHERE id = '${userId}'`); // NEVER

// ✅ Shell command injection prevention
import { execFile } from 'child_process';
// Use execFile (not exec) with explicit args array — never construct a command string with user input
execFile('ffmpeg', ['-i', userFilePath, outputPath], callback);

// ❌ Never
exec(`ffmpeg -i ${userFilePath} output.mp4`); // userFilePath could contain ; rm -rf /
```

---

## A05 — Security Misconfiguration

```typescript
// ✅ CORS — restrict origins in production
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') ?? [],
  credentials: true,
}));

// ✅ Remove framework version headers
app.disable('x-powered-by'); // Express
// Or: app.use(helmet()) which does this automatically

// ✅ Disable debug endpoints in production
if (process.env.NODE_ENV !== 'production') {
  app.use('/debug', debugRouter);
}

// ✅ Helmet — sets all security headers in one call (Express)
import helmet from 'helmet';
app.use(helmet());
```

---

## A07 — Authentication / Session Failures

```typescript
// ✅ JWT best practices
const token = jwt.sign(
  { sub: userId, role: user.role },
  process.env.JWT_SECRET!,
  {
    expiresIn: '15m',   // short-lived access token
    algorithm: 'HS256',
    issuer: 'myapp',
    audience: 'myapp-api',
  }
);

// ✅ Account lockout — track failed attempts in cache
async function recordFailedLogin(email: string): Promise<void> {
  const key = `login_failures:${email}`;
  const attempts = await cache.incr(key);
  await cache.expire(key, 900); // 15 minute window

  if (attempts >= 5) {
    await lockAccount(email, '30m');
    await notifyUser(email, 'Account locked after failed attempts');
  }
}

// ✅ Constant-time comparison for tokens (prevents timing attacks)
import { timingSafeEqual } from 'crypto';
const valid = timingSafeEqual(Buffer.from(providedToken), Buffer.from(storedToken));
```

---

## A10 — SSRF (Server-Side Request Forgery)

```typescript
// ✅ Allowlist outbound URLs
const ALLOWED_HOSTS = ['api.stripe.com', 'api.sendgrid.com'];

function validateOutboundUrl(url: string): void {
  const parsed = new URL(url);
  if (!ALLOWED_HOSTS.includes(parsed.hostname)) {
    throw new Error(`Outbound request to ${parsed.hostname} not allowed`);
  }
  // Block internal/cloud metadata ranges
  const blocked = ['169.254.', '10.', '192.168.', '172.16.', '127.'];
  if (blocked.some(prefix => parsed.hostname.startsWith(prefix))) {
    throw new Error('Requests to internal addresses are forbidden');
  }
}
```

---

## Security Testing

```bash
# Dependency vulnerabilities
npm audit --audit-level=high
pip-audit
bundle audit

# SAST (Static Application Security Testing)
npx semgrep --config auto src/

# Container scanning
trivy image myapp:latest
docker scout cves myapp:latest

# Secret scanning
truffleHog git file://. --since-commit HEAD~50
git-secrets --scan-history
```
