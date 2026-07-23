---
name: workflow-eval
description: Evaluate an agentic workflow result and always persist a docs/reviews artifact
---

Act as **Judge Agent** with the workflow integrity checklist. Always write a durable artifact under `docs/reviews/`, whether this command was invoked manually or by a protected-change hook.

Evaluate: {plan_or_diff_or_feature}

Inputs to inspect:
- `AGENTS.md`
- Standards docs from `.cursor/config/workflow-policy.json`, usually `AGENTS.md`
- Relevant `docs/plans/*` or `docs/adr/*`
- Relevant `.cursor/agents/*`, `.cursor/rules/*`, `.cursor/commands/*`
- Git diff or specified implementation files

Process:
1. Run skill-loader for review:
   `python3 .cursor/skills/scripts/skill-loader.py --phase review --task "{plan_or_diff_or_feature}" --agent judge-agent --keywords "workflow,judge,security,tenant,test"`
2. Verify the result against acceptance criteria and the handoff packet.
3. Check the shared protected classifier in `.cursor/config/protected-paths.json`; do not accept agent self-classification.
4. Check role boundaries: planner planned, workers implemented, judge stayed read-only.
5. Check evidence quality: commands, tests, docs, ADRs, security/privacy/data/AI/infrastructure/domain gates.
6. Write findings to `docs/reviews/YYYY-MM-DD-workflow-eval-{slug}.md`.

Output:

```markdown
Status: GOOD | NEEDS_OPTIMIZATION | BLOCKED

## What Works

## Gaps
- [severity] file:line — issue

## Required Optimizations

## Evidence Reviewed

## Recommended Cursor Config Changes
```
