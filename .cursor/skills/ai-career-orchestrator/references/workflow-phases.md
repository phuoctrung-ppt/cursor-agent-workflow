# Workflow Phases

```
brainstorm → plan → design → implement-* → review → merge
```

## Parallel Execution (after plan approved)

```
database-worker ──┐
backend-worker  ──┼── integration ── qa-worker ── judge-agent
frontend-worker ──┘
ai-worker (if AI feature)
```

## Phase → skill-loader --phase

| User intent | --phase |
|-------------|---------|
| Explore ideas | brainstorm |
| ADR + tasks | plan |
| Schema + API design | design |
| NestJS code | implement-backend |
| Next.js code | implement-frontend |
| Migrations | database |
| Docker/CI | devops |
| PR review | review |
