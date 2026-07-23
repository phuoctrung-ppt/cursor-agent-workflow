# Codebase Understanding Phase

**When to skip:** If provided with scout reports, skip this phase.

## Core Activities

### Parallel Scout Agents
- Each scout locates files needed for specific task aspects
- Wait for all scout agents to report back before analysis
- Efficient for finding relevant code across large codebases

### Essential Documentation Review
ALWAYS read these files first:

1. **`./docs/development-rules.md`** (IMPORTANT)
   - File Name Conventions
   - File Size Management
   - Development rules and best practices
   - Code quality standards
   - Security guidelines

2. **`AGENTS.md` (canonical hub) + any project overview doc if present** (e.g. `./docs/architecture.md` or `./docs/codebase-summary.md` — these are optional and may not exist)
   - Project structure and current status
   - High-level architecture overview
   - Component relationships
   - **If planning changes the system:** capture the decision in the plan and, if the project keeps a living overview (`docs/architecture.md`), update it in the Domain Config Sync phase (create it if the project uses one). Never leave architecture decisions only in chat.
   - **If `AGENTS.md` sections are still `<PLACEHOLDER>` template values:** treat those facts as unknown — gather from the code or ask the orchestrator. Do not plan from placeholder/example content.

### Environment Analysis
- Review development environment setup
- Analyze dotenv files and configuration
- Identify required dependencies
- Understand build and deployment processes

### Pattern Recognition
- Study existing patterns in codebase
- Identify conventions and architectural decisions
- Note consistency in implementation approaches
- Understand error handling patterns

### Integration Planning
- Identify how new features integrate with existing architecture
- Map dependencies between components
- Understand data flow and state management
- Consider backward compatibility

## Best Practices

- Start with documentation before diving into code
- Use scouts for targeted file discovery
- Document patterns found for consistency
- Note any inconsistencies or technical debt
- Consider impact on existing features
