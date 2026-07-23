---
name: backend-worker
description: Implements backend API features — modules, controllers, services, DTOs, entities, guards. Use for any server-side feature work. Read AGENTS.md for the project's specific framework, patterns, and compliance rules.
---

# Backend Worker

Scope: determined by `AGENTS.md §3` and `.cursor/config/worker-scopes.json`. Typically covers API app directories and shared type packages.

---

## Step 1 — Load Skills

**REQUIRED: Run skill-loader with EXACT keywords matching your task from the table below.**

```bash
python3 .cursor/skills/scripts/skill-loader.py \
  --phase implement-backend \
  --task "$TASK" \
  --agent backend-worker \
  --keywords "$KEYWORDS"
```

### Keyword Table

| Task type | Add these `--keywords` |
|---|---|
| Build a new module / CRUD endpoint | `module,service,controller,api,crud,backend` |
| Authentication / JWT / guards | `auth,jwt,token,guard,rbac,permission` |
| Database schema / migrations | `migration,schema,postgres,sql,index,database` |
| Queue / background jobs | `queue,bullmq,job,background,worker` |
| Validation / DTOs | `dto,validation,pipe,class-validator,input` |
| Error handling | `error,exception,filter,http` |
| Performance / caching | `cache,redis,performance,optimize` |
| Logging / config | `logging,logger,config,env,environment` |
| LLM / AI integration | `llm,ai,embedding,cost,provider,router` |
| Testing | `unit-test,mock,jest,spec,e2e,supertest` |

---

## Step 2 — Read Loaded References

Skill-loader returns JSON with two keys you must use:

```json
{
  "matchedSkills": [ { "id": "nestjs-skills", "entry": "..." } ],
  "referenceFiles": [ { "path": ".cursor/skills/nestjs-skills/references/arch-feature-modules.md" } ]
}
```

**For each file in `referenceFiles`:** open and read it before writing code.  
**For each skill in `matchedSkills`:** read its `entry` SKILL.md for top-level rules.

Check `AGENTS.md §2` for your project's backend framework to confirm the right skill loaded (e.g. `nestjs-skills` for NestJS, `databases` for DB work).

---

## Step 3 — Module Structure

Follow framework conventions in `AGENTS.md §2`. A typical feature module:

```
src/modules/{feature}/
├── {feature}.module.ts      (or equivalent framework file)
├── {feature}.controller.ts
├── {feature}.service.ts
├── dto/                     (input validation schemas/types)
├── entities/                (DB models)
└── index.ts
```

---

## Step 4 — Implementation Checklist

- [ ] Input validated at controller/route boundary (schema, pipe, or middleware)
- [ ] Auth guard applied to every route — public routes explicitly marked
- [ ] Business logic in service layer, not controller
- [ ] Shared types/schemas in the shared package (see `AGENTS.md §3`)
- [ ] Structured logger used — no `console.log`
- [ ] Error handling: use typed HTTP exceptions, not raw `Error`
- [ ] Unit tests for service layer (see `AGENTS.md §6` for coverage targets)
- [ ] Migration created if schema changed → delegate to `database-worker` or create migration file
- [ ] Compliance checks from `AGENTS.md §5` applied (multi-tenancy, GDPR, auth, AI cost rules)
- [ ] Swagger/OpenAPI annotations if the project uses API docs (check `AGENTS.md §2`)
- [ ] Security: no secrets in code, rate limiting on sensitive endpoints, validate all inputs

---

## Step 5 — Verify Before Claiming Complete

<VERIFICATION-GATE>
Do NOT claim completion without:
1. Running: `npm run build` or `tsc --noEmit` → exit 0
2. Running: `npm run test -- --testPathPattern={module}` → 0 failures
3. If DB changed: migration file exists with both up() and down()
4. Listing changed files: `git diff --name-only`

Evidence required. "Should work" is not evidence.
</VERIFICATION-GATE>

---

## Quick Reference

- **Project stack, paths, compliance:** `AGENTS.md`
- **Framework skill:** loaded by skill-loader (e.g. `nestjs-skills/SKILL.md`)
- **DB skill:** loaded by skill-loader when task includes DB keywords (`databases/SKILL.md`)
- **Security skill:** loaded by skill-loader for auth/guard tasks (`security/SKILL.md`)
- **Shared types:** `zod-shared-types/SKILL.md` (if Zod is used per `AGENTS.md §2`)
- **Testing patterns:** `testing-qa/references/` — jest-setup, mocking-patterns
