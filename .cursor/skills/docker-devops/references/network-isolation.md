# Network Isolation — Docker Compose Patterns

Proper network isolation prevents internal services (databases, caches, workers, admin APIs) from being accidentally exposed on the public internet.

---

## The Two-Network Model

```
Internet
    │
    ▼
┌─────────┐   public network   ┌─────────┐
│  nginx  │ ◄──────────────── │   api   │
└─────────┘                    └─────────┘
                                    │
                              internal network
                 ┌──────────────────┼──────────────────┐
                 ▼                  ▼                   ▼
            ┌────────┐        ┌──────────┐         ┌────────┐
            │   db   │        │  cache   │         │ worker │
            └────────┘        └──────────┘         └────────┘

Public network:   nginx, api (only services that need internet access)
Internal network: api, db, cache, worker (service-to-service only)
```

---

## Compose Network Definition

```yaml
# docker-compose.yml

services:
  nginx:
    networks:
      - public           # exposes 80/443 to internet via ports:
    ports:
      - "80:80"
      - "443:443"

  api:
    networks:
      - public           # nginx can reach api
      - internal         # api can reach db, cache

  worker:
    networks:
      - internal         # workers ONLY on internal — never expose ports
    # no ports: defined — workers are unreachable from outside

  db:
    networks:
      - internal         # db ONLY on internal
    # no ports: defined — never expose DB port on host in production

  cache:
    networks:
      - internal
    # no ports: defined — Redis only reachable internally

networks:
  public:                # Docker creates bridge network automatically
  internal:
    internal: true       # 'internal: true' blocks all external egress too
```

---

## Admin Service Isolation

```yaml
services:
  admin-api:
    networks:
      - internal         # admin API is NOT on public network
    # Access only via VPN, SSH tunnel, or bastion host
    # Or expose on a non-public port with IP allowlist at nginx level

  nginx:
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    # nginx.conf routes /api/* to api service
    # admin endpoint: only accessible from VPN CIDR
```

```nginx
# docker/nginx/nginx.conf
upstream api {
    server api:3001;
}

upstream admin {
    server admin-api:3002;
}

server {
    listen 80;

    location /api/ {
        proxy_pass http://api/;
    }

    # Admin: restrict by IP at nginx level
    location /admin/ {
        allow 10.0.0.0/8;      # internal VPN range
        deny all;
        proxy_pass http://admin/;
    }
}
```

---

## Service Discovery

Services find each other by **service name** (Docker's internal DNS), not by IP or `localhost`.

```yaml
# ✅ Correct — use service name as hostname
DATABASE_URL: postgresql://postgres:password@db:5432/mydb
#                                               ^^^ service name
REDIS_URL: redis://cache:6379
#                  ^^^^^ service name

# ❌ Wrong — localhost means the container itself
DATABASE_URL: postgresql://postgres:password@localhost:5432/mydb
```

---

## Port Exposure Rules

```yaml
# ✅ Only expose ports that external clients need
nginx:
  ports:
    - "80:80"
    - "443:443"

# ✅ Internal services: no ports: key at all
db:
  # no ports — unreachable from host or internet

# ⚠️ Local dev only — expose DB port for debugging tools
# Use docker-compose.override.yml (not committed to main compose):
# db:
#   ports:
#     - "5432:5432"   # only for local dev, never in production compose

# ✅ Explicit port binding to localhost only (not 0.0.0.0)
api:
  ports:
    - "127.0.0.1:3001:3001"  # only localhost can reach this, not all interfaces
```

---

## Verification Checklist

```bash
# List networks
docker network ls

# Inspect which services are on which network
docker network inspect <project>_public
docker network inspect <project>_internal

# Verify a service cannot reach another across network boundary
docker compose exec worker ping nginx   # should fail if worker is internal-only

# Scan exposed ports on host
ss -tlnp | grep LISTEN
# or: netstat -tlnp

# Verify no DB port exposed on host
ss -tlnp | grep 5432   # should show nothing in production
```

---

## Common Mistakes

| Mistake | Impact | Fix |
|---|---|---|
| Exposing `db` port (`5432:5432`) in production | DB accessible from internet | Remove `ports:` from DB service |
| Using `network_mode: host` | Container shares host network stack — no isolation | Never use in production |
| No `internal: true` on internal network | Containers can make outbound internet calls | Add `internal: true` for data-layer network |
| Hardcoding IP addresses | Breaks when containers restart | Use service names (Docker DNS) |
| Exposing admin API on public network | Admin bypasses security controls | Admin must be on internal or VPN-only |
