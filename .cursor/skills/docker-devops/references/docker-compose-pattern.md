# Docker Compose — Generic Patterns

Adapt service names and ports to your project (see `AGENTS.md §3`). The structural patterns below apply to any stack.

---

## Full Compose Template

```yaml
# docker-compose.yml
version: '3.9'

services:

  # ── API / Backend ────────────────────────────────────────────────────
  api:
    build:
      context: .
      dockerfile: apps/api/Dockerfile
      target: runner          # use the minimal runtime stage
    env_file: .env
    environment:
      NODE_ENV: production
      DATABASE_URL: postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      REDIS_URL: redis://cache:6379
    ports:
      - "3001:3001"           # expose only on public network
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 15s
    networks:
      - public
      - internal
    restart: unless-stopped

  # ── Worker / Background Jobs ─────────────────────────────────────────
  worker:
    build:
      context: .
      dockerfile: apps/worker/Dockerfile
      target: runner
    env_file: .env
    environment:
      REDIS_URL: redis://cache:6379
      DATABASE_URL: postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
    depends_on:
      db:    { condition: service_healthy }
      cache: { condition: service_healthy }
    networks:
      - internal              # workers are NEVER on public network
    restart: unless-stopped

  # ── Database ─────────────────────────────────────────────────────────
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - internal              # DB is NEVER on public network
    restart: unless-stopped

  # ── Cache ────────────────────────────────────────────────────────────
  cache:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - internal
    restart: unless-stopped

  # ── Reverse Proxy ────────────────────────────────────────────────────
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/nginx/certs:/etc/nginx/certs:ro
    depends_on:
      - api
    networks:
      - public
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  public:                     # internet-facing services only
  internal:                   # service-to-service only, no external access
```

---

## Environment Variables Pattern

```bash
# .env.example — commit this (no real secrets)
POSTGRES_PASSWORD=changeme
POSTGRES_DB=myapp
REDIS_PASSWORD=changeme
JWT_SECRET=changeme
API_PORT=3001

# .env — never commit, in .gitignore
POSTGRES_PASSWORD=real_strong_password_here
POSTGRES_DB=myapp_prod
REDIS_PASSWORD=real_redis_password
JWT_SECRET=very_long_random_secret_here
```

---

## depends_on Conditions

```yaml
depends_on:
  db:
    condition: service_healthy    # wait until healthcheck passes
  migrations:
    condition: service_completed_successfully  # wait for one-shot task to finish
  other_service:
    condition: service_started    # just wait for container to start (no healthcheck)
```

---

## Override Files

```yaml
# docker-compose.override.yml — local dev overrides (not committed)
services:
  api:
    build:
      target: dev             # use the dev stage with hot-reload
    volumes:
      - ./apps/api/src:/app/src  # mount source for hot-reload
    environment:
      NODE_ENV: development
    ports:
      - "9229:9229"           # Node.js debugger port

# docker-compose.test.yml — CI test environment
services:
  api:
    environment:
      DATABASE_URL: postgresql://postgres:test@db:5432/test
      NODE_ENV: test
```

```bash
# Use override files explicitly
docker compose -f docker-compose.yml -f docker-compose.override.yml up
docker compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit
```

---

## Common Pitfalls

| Issue | Fix |
|---|---|
| Service starts before DB is ready | Use `condition: service_healthy` with a proper `healthcheck` |
| `depends_on` doesn't wait for app readiness | `depends_on` only waits for container start by default — always add `healthcheck` |
| Secrets in compose file | Move to `.env` file, never hardcode in compose |
| Image rebuilds not picked up | `docker compose up --build` to force rebuild |
| Port conflicts on CI | Use internal-only networking; only expose necessary ports |
