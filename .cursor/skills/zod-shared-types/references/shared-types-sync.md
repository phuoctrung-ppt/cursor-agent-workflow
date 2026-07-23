# Shared Types Sync

1. Add schema to `packages/shared-types/src/schemas/`
2. Export from `packages/shared-types/src/index.ts`
3. Backend: `createZodDto()` in module dto/
4. Frontend: import schema + inferred type
5. Run `pnpm build --filter=shared-types` before dependent apps

Never duplicate validation logic in frontend-only Zod files.
