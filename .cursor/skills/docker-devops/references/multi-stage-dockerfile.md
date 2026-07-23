# Multi-Stage Dockerfile — Generic Patterns

Multi-stage builds: smaller final images, faster CI, no dev dependencies in production. Adapt language/runtime to your stack.

---

## Node.js Pattern (API / Web App)

```dockerfile
# Dockerfile
ARG NODE_VERSION=20-alpine

# ── Stage 1: deps ────────────────────────────────────────────────────────
FROM node:${NODE_VERSION} AS deps
WORKDIR /app

# Copy only manifests first — Docker caches this layer if they don't change
COPY package.json package-lock.json ./
# If monorepo with workspaces:
# COPY packages/*/package.json ./packages/
RUN npm ci --frozen-lockfile

# ── Stage 2: builder ─────────────────────────────────────────────────────
FROM node:${NODE_VERSION} AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN npm run build          # compiles TypeScript / bundles

# ── Stage 3: runner (production) ─────────────────────────────────────────
FROM node:${NODE_VERSION} AS runner
WORKDIR /app

ENV NODE_ENV=production

# Non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Only copy what's needed at runtime
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

USER appuser

EXPOSE 3001

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=15s \
  CMD node -e "require('http').get('http://localhost:3001/health', r => process.exit(r.statusCode === 200 ? 0 : 1))"

CMD ["node", "dist/main.js"]

# ── Stage 4: dev (local only, not pushed to registry) ────────────────────
FROM deps AS dev
WORKDIR /app
COPY . .
ENV NODE_ENV=development
CMD ["npm", "run", "start:dev"]
```

---

## Python Pattern (FastAPI / Django)

```dockerfile
ARG PYTHON_VERSION=3.12-slim

FROM python:${PYTHON_VERSION} AS deps
WORKDIR /app

# Install build tools only in this stage
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:${PYTHON_VERSION} AS runner
WORKDIR /app

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Only the installed packages, not the build tools
COPY --from=deps /install /usr/local
COPY --src/. .

USER appuser

EXPOSE 8000

HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## .dockerignore (Always Include)

```
node_modules
.git
.gitignore
dist
*.log
.env
.env.*
!.env.example
coverage
.nyc_output
*.md
docs
tests
**/*.spec.ts
**/*.test.ts
Dockerfile*
docker-compose*
.github
.cursor
```

A proper `.dockerignore` prevents secrets and dev files from leaking into the image build context and makes builds faster.

---

## Build Arguments & Secrets

```dockerfile
# Build-time args (safe for non-secret config)
ARG APP_VERSION=unknown
ARG BUILD_DATE=unknown
LABEL version="${APP_VERSION}" build-date="${BUILD_DATE}"

# Runtime secrets: NEVER bake into image layers
# Pass via environment variables at runtime:
# docker run -e DATABASE_URL=... myapp
# Or via Docker secrets / Kubernetes secrets at deploy time

# ❌ Never do this:
# RUN echo "SECRET_KEY=abc123" >> /etc/environment
```

---

## Layer Caching — Key Principles

```dockerfile
# ✅ Copy dependency manifests BEFORE source code
COPY package.json package-lock.json ./   # cached if unchanged
RUN npm ci                                # only re-runs when manifests change
COPY . .                                  # source changes don't bust dep cache

# ✅ Order FROM most stable to most frequently changing:
# 1. Base image (rarely changes)
# 2. System dependencies (occasionally changes)
# 3. App dependencies (changes on dep updates)
# 4. App source (changes on every commit)
```

---

## Size Optimization Tips

| Technique | Savings |
|---|---|
| Alpine base images (`-alpine` tag) | ~80% smaller than full Debian |
| Multi-stage — no dev deps in runner | Removes node_modules/test deps |
| `.dockerignore` exclusions | Excludes source, docs, tests |
| `npm ci` instead of `npm install` | Reproducible, no lockfile drift |
| `RUN` command cleanup (`rm -rf /var/lib/apt/lists/*`) | Removes apt cache from image |
| Non-root user | Security best practice, also avoids running as root |

---

## Verifying Image Size

```bash
# Build and check size
docker build -t myapp:local .
docker images myapp:local

# Inspect layer sizes
docker history myapp:local

# Scan for vulnerabilities
docker scout cves myapp:local
# or: trivy image myapp:local
```
