---
name: ai-llm-integration
description: Domain skill for LLM/AI integration — covers provider routing, streaming, embeddings, vector search, AI cost tracking, and human-in-the-loop patterns. Activate when AGENTS.md §2 AI/LLM is not 'none'. Use for any LLM calls, embedding generation, or AI-driven features.
---

# AI/LLM Integration

> **Domain skill**: project-specific AI provider names, use-cases, and patterns come from `AGENTS.md §2` and `§5`. This skill covers the universal patterns — adapt names to match your project.

## When to Use

- Features that call external AI providers (OpenAI, Anthropic, etc.)
- Embedding generation + vector similarity search
- AI cost tracking and budget enforcement
- Any AI decision requiring human-in-the-loop review (per `AGENTS.md §5`)

## Mandatory Patterns

1. **Central router/service** — all LLM calls route through a single service; budget check before each call
2. **Usage event** — emit after every call with tokens, cost_usd, latency_ms (log to your project's usage table/service)
3. **Cost calculation** — centralized cost utility shared across the codebase
4. **Fallback provider** — on primary failure, fall back to secondary provider
5. **Prompt sanitization** — sanitize user input before passing to LLM
6. **XAI** — for consequential decisions: return `explanation` with confidence, key factors, counterfactuals
7. **Human-in-the-loop** — no auto-action on high-stakes decisions without explicit user confirmation (see `AGENTS.md §5`)

## References (load on demand)

- [llm-router-pattern.md](references/llm-router-pattern.md) — router service template
- [embedding-operations.md](references/embedding-operations.md) — vector similarity queries
- [cost-tracking.md](references/cost-tracking.md) — usage event schema

## Related Rules

`.cursor/rules/003-ai-ethics-compliance.mdc`

## Agent

Use with `@ai-worker` and `/ai-cost-check` command.
