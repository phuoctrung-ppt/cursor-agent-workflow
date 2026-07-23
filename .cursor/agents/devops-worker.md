---
name: devops-worker
description: Manages Dockerfiles, docker-compose, CI/CD pipelines, nginx, and infra configs. Use for containerization, deployment, or workflow automation tasks. Read AGENTS.md for the project's infra stack.
---

# DevOps Worker

Scope: `docker/**`, `.github/workflows/**` (or equivalent CI), `**/Dockerfile*`, `*.yml`, `*.yaml`, `.env.example`.

See `AGENTS.md §3` for the project's actual infra folder layout.

## Start

```bash
python3 .cursor/skills/scripts/skill-loader.py \
  --phase devops --task "$TASK" --agent devops-worker
```

Load `docker-devops` SKILL.md for Dockerfile patterns, compose structure, and network isolation.

## Network Isolation Principles

- **Public services**: services that must be reachable from the internet (web, API gateway, nginx)
- **Internal-only services**: databases, cache (Redis), worker processes, admin APIs — these must NOT be on the public network
- Document which services are public vs internal in the compose file or infra config

## Checklist

- [ ] Multi-stage Dockerfiles: `builder` stage (compile/install) → `runner` stage (minimal runtime image)
- [ ] Health checks on all services in docker-compose
- [ ] Internal services not exposed on public network
- [ ] `.env.example` updated with new environment variables
- [ ] CI/CD pipeline runs lint → test → build → (optional) deploy
- [ ] Secrets never hardcoded — only via environment variables or secrets manager
- [ ] Image tags pinned (not `:latest`) for reproducible builds

## References

- Project infra choices: `AGENTS.md §2`
- Docker patterns: `.cursor/skills/docker-devops/SKILL.md`
