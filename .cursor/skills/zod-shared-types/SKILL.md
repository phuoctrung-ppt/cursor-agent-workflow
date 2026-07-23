---
name: zod-shared-types
description: Designs Zod schemas in packages/shared-types for API contracts shared between NestJS and Next.js. Use for DTOs, forms, schema versioning with createZodDto and zodResolver.
---

# Zod Shared Types

## Single Source of Truth

All schemas: `packages/shared-types/src/schemas/`

Export: `export const XSchema = z.object(...)` + `export type XDto = z.infer<typeof XSchema>`

## NestJS

```typescript
import { createZodDto } from 'nestjs-zod';
export class CreateJobDto extends createZodDto(CreateJobSchema) {}
```

## Next.js

```typescript
useForm({ resolver: zodResolver(CreateJobSchema) })
```

## Versioning

Breaking changes: `CreateJobSchemaV2`; API `/api/v1` vs `/api/v2`

## References

- [schema-design-patterns.md](references/schema-design-patterns.md)
- [shared-types-sync.md](references/shared-types-sync.md)

Zero runtime deps except `zod` in shared-types package.
