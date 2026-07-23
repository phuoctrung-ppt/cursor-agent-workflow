# Agentic Planner-Worker-Judge Workflow

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/phuoctrung-ppt/cursor-agent-workflow)](https://github.com/phuoctrung-ppt/cursor-agent-workflow/commits)
[![Repo Stars](https://img.shields.io/github/stars/phuoctrung-ppt/cursor-agent-workflow?style=social)](https://github.com/phuoctrung-ppt/cursor-agent-workflow/stargazers)

A portable, domain-neutral Cursor workflow for building software with coordinated AI agents.

## Problem

Most agentic coding flows break down at scale because they lack:
- clear role boundaries,
- artifact-driven quality gates,
- and repeatable review loops.

Result: inconsistent outputs, hidden risks, and hard-to-review changes.

## Solution

This repo provides a **Planner → Worker → Judge** workflow with:
- strict role separation,
- scoped editing permissions,
- protected-path review gates,
- and durable planning/review artifacts under `docs/`.

## Demo (GIF/Video)

- 60–90s demo GIF/video: `docs/design/sketches/demo/README.md` (replace with your recording link)
- Suggested flow to demo:
  1. `/architecture-plan brainstorming "<idea>"`
  2. `/architecture-plan`
  3. `/dev-module <module-name>`
  4. Show generated artifacts in `docs/plans/` and `docs/reviews/`

## 3-minute Quick Start (copy-paste)

```bash
# 1) Copy .cursor and AGENTS.md into your project root
# 2) Start Cursor in that project

# 3) Run the planning flow
/architecture-plan brainstorming "Build <your product idea>"
/architecture-plan

# 4) Build one module end-to-end
/dev-module <module-name>
```

## Golden Path (<10 minutes to first "aha")

1. Run `/architecture-plan brainstorming "<your app idea>"`.
2. Approve the brainstorm output.
3. Run `/architecture-plan` to generate executable tasks.
4. Run `/dev-module <first-module>`.
5. Observe concrete artifacts in:
   - `docs/plans/`
   - `docs/adr/`
   - `docs/reviews/`

## Who is this for?

- Teams that want **process-backed** AI development, not ad-hoc prompting.
- Projects requiring traceability (plans, ADRs, review logs).
- Leads who want guardrails for protected changes (auth, infra, migrations).

## When NOT to use

- Very small throwaway prototypes where process overhead is unnecessary.
- Solo experiments needing speed over governance.
- Teams unwilling to maintain planning/review artifacts.

## Starter Kits

Use starter adaptation guides:
- SaaS app: `docs/starter-kits/saas.md`
- AI app: `docs/starter-kits/ai-app.md`
- E-commerce: `docs/starter-kits/e-commerce.md`

## Migration Guides

- From scratch: `docs/migration/from-scratch.md`
- Existing project: `docs/migration/from-existing-project.md`

## Trust & Measurement

Use `docs/benchmark-template.md` to track before/after quality metrics:
- review cycle time,
- post-merge bug rate,
- protected-change compliance.

## Community & Growth

- Changelog: `CHANGELOG.md`
- Growth loop plan: `docs/growth-loop.md`
- Contribution guide: `CONTRIBUTING.md`
- Roadmap template: `docs/roadmap.md`

## Core Workflow Docs

- Domain config hub: `AGENTS.md`
- Development rules: `docs/development-rules.md`
- Workflow config:
  - `.cursor/config/workflow-policy.json`
  - `.cursor/config/worker-scopes.json`
  - `.cursor/config/protected-paths.json`

---

If this template helps, please ⭐ the repo and share your adaptation with the community.
