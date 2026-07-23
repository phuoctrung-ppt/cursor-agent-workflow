# Auth Patterns — JWT, Sessions, Refresh Tokens

Generic patterns for authentication. Check `AGENTS.md §2` for your auth library and `AGENTS.md §5` for required auth method (JWT, session, OAuth, MFA).

---

## JWT Access + Refresh Token Flow

```
┌──────────┐                         ┌─────────┐
│  Client  │                         │   API   │
└──────────┘                         └─────────┘
     │ POST /auth/login (email+pass)       │
     │────────────────────────────────────▶│
     │                              Verify credentials
     │                              Generate access token (15m)
     │                              Generate refresh token (7d)
     │                              Store refresh token hash in DB
     │◀────────────────────────────────────│
     │ { accessToken, refreshToken }       │
     │                                     │
     │ GET /api/data                       │
     │ Authorization: Bearer <accessToken> │
     │────────────────────────────────────▶│
     │                              Verify JWT signature + expiry
     │◀────────────────────────────────────│
     │ 200 OK { data }                     │
     │                                     │
     │ POST /auth/refresh                  │
     │ { refreshToken }                    │
     │────────────────────────────────────▶│
     │                              Verify refresh token against DB
     │                              ROTATE: invalidate old, issue new pair
     │◀────────────────────────────────────│
     │ { accessToken, refreshToken }       │
```

---

## Token Generation

```typescript
// auth/token.service.ts
import jwt from 'jsonwebtoken';
import { randomBytes, createHash } from 'crypto';

export class TokenService {
  generateAccessToken(payload: { sub: string; role: string }): string {
    return jwt.sign(payload, process.env.JWT_SECRET!, {
      expiresIn: '15m',
      issuer: 'myapp',
      audience: 'myapp-api',
    });
  }

  generateRefreshToken(): { token: string; hash: string } {
    const token = randomBytes(64).toString('hex'); // 128 char opaque token
    const hash = createHash('sha256').update(token).digest('hex'); // store hash, not plaintext
    return { token, hash };
  }

  verifyAccessToken(token: string): jwt.JwtPayload {
    return jwt.verify(token, process.env.JWT_SECRET!, {
      issuer: 'myapp',
      audience: 'myapp-api',
    }) as jwt.JwtPayload;
  }
}
```

---

## Refresh Token Rotation

```typescript
// auth/auth.service.ts — refresh endpoint handler
async refresh(refreshToken: string): Promise<{ accessToken: string; refreshToken: string }> {
  const hash = createHash('sha256').update(refreshToken).digest('hex');
  
  // Find and validate stored refresh token
  const stored = await this.db.refreshTokens.findOne({
    where: { hash, revokedAt: null },
    include: { user: true },
  });

  if (!stored) throw new UnauthorizedException('Invalid or expired refresh token');
  if (stored.expiresAt < new Date()) {
    await this.db.refreshTokens.update({ id: stored.id }, { revokedAt: new Date() });
    throw new UnauthorizedException('Refresh token expired');
  }

  // Detect reuse of old tokens (token theft signal)
  if (stored.usedAt) {
    // This refresh token was already used — potential theft
    // Revoke ALL tokens for this user (nuclear option)
    await this.db.refreshTokens.updateMany(
      { userId: stored.userId },
      { revokedAt: new Date() }
    );
    throw new UnauthorizedException('Token reuse detected. All sessions revoked.');
  }

  // Mark as used (rotation — old token is now invalid)
  await this.db.refreshTokens.update({ id: stored.id }, { usedAt: new Date() });

  // Issue new pair
  const newRefresh = this.tokenService.generateRefreshToken();
  const newAccess  = this.tokenService.generateAccessToken({ sub: stored.userId, role: stored.user.role });

  await this.db.refreshTokens.create({
    userId: stored.userId,
    hash: newRefresh.hash,
    expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days
    familyId: stored.familyId, // track token family for breach detection
  });

  return { accessToken: newAccess, refreshToken: newRefresh.token };
}
```

---

## Cookie vs Bearer Token

```typescript
// ✅ Web apps (browser) — HttpOnly cookies
res.cookie('refresh_token', refreshToken, {
  httpOnly: true,        // JS cannot read — prevents XSS theft
  secure: true,          // HTTPS only
  sameSite: 'strict',    // CSRF protection
  maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
  path: '/auth/refresh', // only sent to refresh endpoint
});

// Send access token in response body — store in memory only (not localStorage)
res.json({ accessToken });

// ✅ Mobile / API clients — Bearer token in Authorization header
// Client stores in secure storage (Keychain on iOS, Keystore on Android)
// Never in plaintext file or SharedPreferences
Authorization: Bearer <accessToken>
```

---

## Auth Guard Pattern

```typescript
// auth/guards/auth.guard.ts — run on every route
export class AuthGuard {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    
    const token = this.extractToken(request);
    if (!token) throw new UnauthorizedException('Missing token');

    try {
      const payload = this.tokenService.verifyAccessToken(token);
      request.user = payload; // attach to request for use in handlers
      return true;
    } catch {
      throw new UnauthorizedException('Invalid or expired token');
    }
  }

  private extractToken(request: Request): string | null {
    const auth = request.headers.authorization;
    if (auth?.startsWith('Bearer ')) return auth.slice(7);
    return request.cookies?.access_token ?? null;
  }
}

// Mark public routes explicitly (deny by default)
@Public()  // custom decorator that skips guard
@Get('health')
healthCheck() { return { status: 'ok' }; }
```

---

## Password Reset Flow

```typescript
// 1. Request reset — issue a short-lived token
async requestPasswordReset(email: string): Promise<void> {
  const user = await this.users.findByEmail(email);
  // Always return success even if user not found (prevents email enumeration)
  if (!user) return;

  const token = randomBytes(32).toString('hex');
  const hash  = createHash('sha256').update(token).digest('hex');
  
  await this.db.passwordResets.create({
    userId: user.id,
    hash,
    expiresAt: new Date(Date.now() + 15 * 60 * 1000), // 15 minutes only
  });

  await this.emailService.send({
    to: user.email,
    subject: 'Password reset',
    body: `Reset link: ${baseUrl}/reset?token=${token}`, // token in URL, hash in DB
  });
}

// 2. Complete reset — validate and consume token
async resetPassword(token: string, newPassword: string): Promise<void> {
  const hash = createHash('sha256').update(token).digest('hex');
  const record = await this.db.passwordResets.findOne({
    where: { hash, usedAt: null },
  });

  if (!record || record.expiresAt < new Date()) {
    throw new BadRequestException('Invalid or expired reset token');
  }

  await this.db.users.update({ id: record.userId }, {
    passwordHash: await bcrypt.hash(newPassword, 12),
  });
  
  // Consume token and revoke all sessions
  await this.db.passwordResets.update({ id: record.id }, { usedAt: new Date() });
  await this.db.refreshTokens.updateMany({ userId: record.userId }, { revokedAt: new Date() });
}
```
