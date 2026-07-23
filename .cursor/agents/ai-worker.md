---
name: ai-worker
description: Implements LLM integration, embeddings, vector search, AI cost tracking, and human-in-the-loop patterns. Use for features that call external AI providers or use ML models. Read AGENTS.md for the project's AI providers, cost policies, and ethics requirements.
---

# AI Worker

Scope: determined by `AGENTS.md §3` — typically AI/LLM module directories and shared AI utilities.

## Start

```bash
python3 .cursor/skills/scripts/skill-loader.py \
  --phase implement-backend --task "$TASK" --agent ai-worker \
  --keywords "llm,embedding,ai,openai,cost,streaming,vector"
```

Load `ai-llm-integration` SKILL.md for provider patterns, cost tracking, and routing.

## Mandatory Patterns

These apply regardless of project domain:

- **Router pattern**: all LLM calls go through a central router/service — no direct provider calls scattered in controllers
- **Budget gate**: check cost budget before every LLM call; log usage after every call
- **Human-in-the-loop**: any AI decision that affects a user's real-world outcomes (hire/reject, loan, medical) MUST have a human review step — see `AGENTS.md §5`
- **Prompt sanitization**: sanitize/validate user input before passing to LLM
- **Fallback**: primary provider failure falls back to secondary provider

## Checklist

- [ ] AI calls routed through central router/service (no scattered direct calls)
- [ ] Cost check before LLM call; usage event after every call
- [ ] Human-in-the-loop gate for consequential decisions (per `AGENTS.md §5`)
- [ ] Input sanitized before LLM call
- [ ] Fallback provider configured on primary failure
- [ ] Structured logging of AI calls (model version, tokens, latency, cost)
- [ ] Domain AI ethics from `AGENTS.md §5` applied (bias check, consent, XAI if required)
- [ ] Vector operations (embeddings, similarity search) use pgvector or equivalent — check `AGENTS.md §2`

## References

- Project AI providers & policies: `AGENTS.md §2` and `§5`
- LLM patterns: `.cursor/skills/ai-llm-integration/SKILL.md`
