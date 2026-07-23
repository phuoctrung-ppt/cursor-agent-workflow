# Starter Kit: AI App

## Use this when
- You are building LLM-assisted features with prompt, retrieval, or agent flows.

## First customizations
1. Set AI/LLM provider details in `AGENTS.md` §2 and §6.
2. Keep `ai-worker` enabled and tune relevant skills in `skills-manifest.json`.
3. Define prompt safety + output validation requirements in `AGENTS.md` §6.
4. Add AI-risk paths to `.cursor/config/protected-paths.json` if needed.

## Suggested first module
- Prompt pipeline + response validation + usage logging.
