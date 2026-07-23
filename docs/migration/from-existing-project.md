# Migration Guide: From Existing Project

1. Copy `.cursor/` and `AGENTS.md` into the existing repository.
2. Map your real folders in `AGENTS.md` §3 and tighten worker scopes.
3. Add protected app paths in `.cursor/config/protected-paths.json`.
4. Run `/architecture-plan brainstorming "stabilize and scale existing project"`.
5. Run `/architecture-plan` for phased task breakdown.
6. Migrate module-by-module with `/dev-module <module>`.
