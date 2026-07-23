---
name: docker-devops
description: Creates multi-stage Dockerfiles, docker-compose with network isolation, nginx reverse proxy, and health checks. Use for any project that needs Docker containerization or CI/CD pipeline setup. Read AGENTS.md for the project's specific service names and infra layout.
---

# Docker & DevOps

## Service Architecture

Document your services in `AGENTS.md §3` (infra layout) and `docker-compose*.yml`. Typical structure:

- **Public services** — reachable from internet (web, API gateway, nginx)
- **Internal-only services** — databases, cache (Redis), workers, admin APIs

## Networks

- `public`: services that need external access (web, API, nginx)
- `internal`: everything else (DB, cache, workers, admin — no external exposure)

See `AGENTS.md §2` (Containerization) for your project's service names.

## References

- [docker-compose-pattern.md](references/docker-compose-pattern.md)
- [multi-stage-dockerfile.md](references/multi-stage-dockerfile.md)
- [network-isolation.md](references/network-isolation.md)
