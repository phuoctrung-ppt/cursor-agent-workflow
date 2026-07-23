---
name: generate-migration
description: Create a database migration with correct naming convention, up/down methods, indexes, and compliance columns — uses the project's ORM and DB from AGENTS.md
---

Act as **Database Worker**. Create a migration for: **{migration_description}**

1. Run skill-loader:
   ```bash
   python3 .cursor/skills/scripts/skill-loader.py \
     --phase database --task "{migration_description}" --agent database-worker \
     --keywords "migration,schema,index"
   ```
2. Read `AGENTS.md §2` (DB type, ORM) and `§3` (migrations path) for the correct location and file format

## Migration Location

Determined by `AGENTS.md §3` — e.g.:
- TypeORM: `<backend_path>/database/migrations/YYYYMMDDHHMMSS-{Name}.ts`
- Prisma: `prisma/migrations/YYYYMMDDHHMMSS_{name}/migration.sql`
- Alembic: `alembic/versions/YYYYMMDDHHMMSS_{name}.py`

## Rules

- Both `up()` and `down()` — never a one-way migration
- UUID or ULID primary keys (avoid auto-increment for distributed safety)
- Timestamp columns: `created_at`, `updated_at` (timezone-aware)
- `deleted_at` for soft delete where applicable
- Indexes on all foreign keys and high-cardinality filter columns
- `CHECK` constraints on logical business rules
- Never enable ORM auto-sync (`synchronize: false` or equivalent)
- Apply compliance columns from `AGENTS.md §5` (e.g. `tenant_id` for multi-tenancy, encrypted fields for PII)

Load `databases` SKILL.md. Output complete migration file.
