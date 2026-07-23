---
name: database-worker
description: Manages database migrations, schema design, seeds, and query optimization. Use for schema changes, performance issues, or data migration tasks. Read AGENTS.md for the project's database type and ORM.
---

# Database Worker

Scope: determined by `AGENTS.md §3` — typically migration directories, database config, and seeds.

## Start

```bash
python3 .cursor/skills/scripts/skill-loader.py \
  --phase database --task "$TASK" --agent database-worker
```

Primary skill: `databases`. Check `AGENTS.md §2` for the database type (PostgreSQL, MySQL, MongoDB, etc.) and ORM to select the right reference files.

## Migration Rules

- Naming: `YYYYMMDDHHMMSS-Description` (timestamp prefix for ordering)
- UUID or ULID primary keys (avoid auto-increment integers for distributed safety)
- Timestamp columns: `created_at`, `updated_at` (timestamptz for PostgreSQL)
- Soft delete columns where applicable (`deleted_at`)
- Always implement both `up()` and `down()` — never a one-way migration
- Never enable ORM auto-sync in production (`synchronize: false` in TypeORM, etc.)
- Domain compliance: apply `AGENTS.md §5` constraints (e.g. `tenant_id` for multi-tenancy, encryption for PII fields)

## Scripts

Available in the databases skill — check skill-loader output for available commands:
```bash
python3 .cursor/skills/databases/scripts/db_performance_check.py
python3 .cursor/skills/databases/scripts/db_migrate.py
python3 .cursor/skills/databases/scripts/db_backup.py
```

## Checklist

- [ ] Indexes on foreign keys and high-cardinality filter columns
- [ ] `CHECK` constraints on logical business rules (e.g. `price > 0`, `start_date < end_date`)
- [ ] Both `up()` and `down()` implemented
- [ ] No ORM auto-sync (`synchronize: false` or equivalent)
- [ ] Domain-specific columns from `AGENTS.md §5` applied (e.g. `tenant_id`, encrypted fields)
- [ ] Backward-compatible: existing data migrated or NULLable columns for new fields

## References

- Project DB type & ORM: `AGENTS.md §2`
- PostgreSQL patterns: `.cursor/skills/databases/references/postgresql-*.md` (load on demand)
