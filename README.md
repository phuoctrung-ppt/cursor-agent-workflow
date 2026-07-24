# Cursor Agent Workflow

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/phuoctrung-ppt/ai-sdlc-workflow)](https://github.com/phuoctrung-ppt/ai-sdlc-workflow/commits)
[![Repo Stars](https://img.shields.io/github/stars/phuoctrung-ppt/ai-sdlc-workflow?style=social)](https://github.com/phuoctrung-ppt/ai-sdlc-workflow/stargazers)

> **A production-oriented AI Software Development Lifecycle (AI SDLC) for Cursor.**
>
> Build production-ready software with AI by following a structured engineering workflow instead of relying on giant prompts.

---

## Why?

Most AI coding workflows focus on improving prompts or providing more context.

This project takes a different approach.

Instead of asking AI to "write better code", it guides AI through a structured software engineering lifecycle inspired by how experienced engineering teams build software.

The goal is simple:

> **Turn vibe coding into production-quality software engineering.**

---

## Philosophy

AI shouldn't replace software engineering.

It should follow it.

This workflow assumes AI will make mistakes.

Instead of relying on perfect prompts, it introduces engineering practices such as:

- Architecture-first development
- Specialized AI workers
- Planning before implementation
- Review before completion
- Controlled repair loops
- Governance and protected changes
- Persistent workflow state
- Scoped responsibilities

---

## AI Software Development Lifecycle

```text
Requirement
      │
      ▼
Architecture Planning
      │
      ▼
Module Planning
      │
      ▼
Implementation
      │
      ▼
Code Review
      │
      ▼
Fix
      │
      ▼
Production Ready
```

Every feature follows the same engineering lifecycle instead of jumping directly into implementation.

---

# Core Principles

## 🏗 Architecture First

Every feature begins with architecture and planning.

No implementation starts before a clear design exists.

---

## 👥 Specialized Workers

Each AI Worker has a single responsibility.

- Frontend Worker builds UI.
- Backend Worker implements APIs.
- Database Worker manages schema changes.
- Judge reviews changes.
- Security Worker validates risks.

Workers stay within their assigned scope.

---

## 🧠 Skill-Driven Development

Workers only load the skills required for the current task.

Instead of loading every prompt and document, the workflow dynamically selects the relevant engineering knowledge.

Benefits:

- Lower token usage
- Better focus
- Less context pollution
- Faster execution

---

## 🔒 Engineering Governance

Quality is enforced, not suggested.

The workflow includes:

- Protected paths
- Worker scopes
- Review gates
- Workflow policies
- Safe execution hooks

This reduces accidental changes outside a worker's responsibility.

---

## 🔁 Controlled Repair

AI is allowed to make mistakes.

AI is **not** allowed to retry forever.

Every repair loop has a bounded retry count, ensuring predictable execution while preventing endless token consumption.

---

## 💾 Persistent State

Long-running development sessions shouldn't restart from scratch.

Workflow state allows interrupted tasks to resume safely with execution history preserved.

---

# Workflow

```text
Idea
      │
      ▼
/architecture-plan
      │
      ▼
/plan-module
      │
      ▼
/dev-module
      │
      ▼
Judge Review
      │
      ▼
Fix (if required)
      │
      ▼
Done
```

The workflow focuses on engineering discipline rather than prompt engineering.

---

# Repository Structure

```text
.cursor/
├── agents/        # Specialized AI workers
├── commands/      # Workflow entry points
├── config/        # Workflow configuration
├── docs/          # Documentation
├── hooks/         # Governance & safety hooks
├── rules/         # Development policies
├── skills/        # Reusable engineering knowledge
├── state/         # Workflow persistence
└── AGENTS.md      # Project overview
```

---

# Why This Workflow?

Unlike traditional AI coding setups, this workflow emphasizes:

- Architecture before implementation
- Engineering process over prompt engineering
- Role-based AI collaboration
- Production-oriented governance
- Quality review before completion
- Scoped workers with minimal context
- Resumable execution

Instead of making AI "smarter", it makes AI follow a better engineering process.

---

# What This Project Is NOT

This project is **NOT**:

- ❌ Another prompt collection
- ❌ An AI Agent Framework
- ❌ An LLM Runtime
- ❌ A Cursor replacement

Cursor already provides an excellent execution environment.

This project provides the **engineering workflow** that runs on top of Cursor.

---

# Vision

The long-term vision is to build an opinionated AI Software Development Lifecycle that helps developers create maintainable, reviewable, and production-ready software with AI.

Today the project targets **Cursor** and primarily focuses on **JavaScript / TypeScript** ecosystems.

Future versions will expand to additional languages, engineering domains, and AI coding platforms.

---

# Documentation

For installation, setup, configuration, and usage guides, please refer to the existing documentation:

- 🚀 [Getting Started](./HOW_TO_USE.md)

> Existing documentation has been preserved. This README focuses on explaining **what the workflow is** and **why it exists**, while the detailed usage remains in the documentation.

---

# Contributing

Contributions, discussions, issues, and pull requests are always welcome.

If you find this workflow useful, please consider giving the repository a ⭐ to support future development.

---

## Acknowledgements

This project was inspired by many great open-source projects and discussions from the AI engineering community.

Special thanks to the creators of:

- **Taste** – https://github.com/Leonxlnx/taste-skill
- **Superpower** – https://github.com/obra/superpowers

...and many other repositories, articles, and engineering discussions that helped shape the ideas behind this workflow.

This repository does not copy a single project. Instead, it combines, adapts, and extends ideas from multiple sources into a production-oriented AI Software Development Lifecycle (AI SDLC).

Thank you to everyone who shares knowledge with the community. ❤️

# License

MIT License