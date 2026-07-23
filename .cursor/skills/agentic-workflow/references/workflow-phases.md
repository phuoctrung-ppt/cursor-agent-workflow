# Generic Workflow Phases

## Standard Phase Chain

```text
classify → plan → execute → verify → review → loop-or-complete
```

## Per-Module Development Loop (`/dev-module`)

```text
brainstorm → plan ⏸️ → execute → test → verify
                                          │
                              APPROVED ───┘──────────────▶ done ✅
                              CHANGES_REQUESTED (loop < 3) ──▶ fix → test → verify
                              CHANGES_REQUESTED (loop ≥ 3) ───▶ escalate ⏸️
```

## Phase Routing

| User intent | Loader phase | Typical owner |
|---|---|---|
| Explore options, prior art | `brainstorm` | architect-planner |
| Create task breakdown, ADR | `plan` | architect-planner |
| Define contracts / schema | `design` | planner + specialist |
| Implement backend / server | `implement-backend` | backend-worker |
| Implement frontend / UI | `implement-frontend` | frontend-worker |
| Database / storage change | `database` | database-worker |
| Infrastructure / release | `devops` | devops-worker |
| Run tests, write coverage | `test` | qa-worker |
| Fix failing tests / issues | `fix` | responsible worker |
| Quality gate / review | `review` | judge-agent / qa-worker / security-worker |
| Full module from scratch | `dev-module` | orchestrator → all workers |

## Loop State File

Per-module loop state: `.cursor/state/module-{name}-loop.json`

```json
{
  "feature": "feature-name",
  "phase": "brainstorm | plan | execute | test | verify | fix | done | escalate",
  "loopCount": 0,
  "planPath": "docs/plans/YYYY-MM-DD-feature.md",
  "reviewPath": "docs/reviews/YYYY-MM-DD-feature-review.md"
}
```

## Protected Change Rule

Protected status comes from `.cursor/config/protected-paths.json`. If protected, require current plan and review artifacts unless a logged override is approved.
