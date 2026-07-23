---
name: ai-cost-check
description: "[DOMAIN — AI/LLM only] Verify LLM cost tracking, budget enforcement, central router usage, and human-in-the-loop for projects using AI/LLM features. Read AGENTS.md §2 and §5 for project-specific AI patterns."
---

> **Domain command** — only relevant when `AGENTS.md §2` AI/LLM ≠ `none`. Skip for projects with no LLM features.

Act as **AI Worker** compliance review.

Review: {ai_code_path}

Read `AGENTS.md §2` (AI/LLM providers, cost policy) and `§5` (AI ethics requirements) before auditing.

Verify:
1. All LLM calls route through a central router/service — no direct provider calls scattered in controllers or routes
2. Budget check performed before every LLM call; cost usage logged after every call
3. Usage event emitted after each call with: provider, model, tokens in/out, cost_usd, latency_ms (and any project-specific dimensions from `AGENTS.md §2`)
4. Fallback provider configured on primary failure
5. Cost calculation uses a shared utility (not duplicated per caller)
6. Human-in-the-loop gate for consequential AI decisions (per `AGENTS.md §5` — e.g. hire/reject, loan, medical)
7. XAI explanation returned for AI decisions that affect users (confidence score, key factors)
8. User input sanitized before passing to LLM

Output: PASS/FAIL with specific issues and file:line references.
