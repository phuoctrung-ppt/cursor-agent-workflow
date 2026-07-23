# Schema Design Patterns

- Co-locate related schemas: `auth.schema.ts`, `job.schema.ts`
- Use `.refine()` for cross-field validation (password match, salary range)
- HR-only fields: `.refine()` on `role === 'hr'`
- Enums: `z.enum(['draft', 'active', 'paused', 'closed'])`
- Pagination: shared `PaginationSchema` with page, limit, sort, order
