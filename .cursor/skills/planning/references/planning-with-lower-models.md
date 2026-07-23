# Planning With Lower-Capability Models

How to make `architect-planner` produce a good, executable plan even when it runs
on a smaller / cheaper model. Lower models fail at planning in predictable ways.
This file is the countermeasure. Read it before writing a plan on a small model.

> Source basis: `.cursor/skills/research/laziness/` (cognitive shortcuts, output
> truncation, prompt remediation). Techniques below are adapted for planning.

---

## 1. Why small models write bad plans

| Failure mode | What it looks like | Root cause |
|---|---|---|
| **Vague plan** | "Build the API, add auth, write tests." No paths, no contracts. | Reads empty `AGENTS.md` sections, invents nothing concrete. |
| **Cognitive shortcut** | Skips brainstorm, jumps straight to a thin file list. | Perceives task as "simple"; reduces internal effort (LazyBench). |
| **Truncation** | Plan stops after Task 2 of 6; ends with "...and so on." | RLHF brevity bias + error-avoidance on long output. |
| **Ceremony over design** | Fills Domain Config Sync checkboxes, but the actual design is empty. | Attention spent on process scaffolding, not the hard thinking. |
| **Hallucinated structure** | References agents/files/folders that do not exist. | Conflicting instructions + no grounding in real code. |

The fix is **not** "add more instructions." It is: **feed less, ground harder,
force one section at a time, and verify.**

---

## 2. The five rules (apply in order)

### Rule 1 — Ground before you plan (no blank-context planning)
A small model cannot invent your stack. Give it facts, not pointers to blank docs.

Before writing any plan, gather and paste the real values into the plan's
**Source Evidence** section:

- Tech stack + versions — from `docs/architecture.md` and `.cursor/rules/001-project-standards.mdc` (NOT the empty `AGENTS.md §2`).
- Repo structure — from `docs/architecture.md` "Containers / Apps" table.
- 1–3 existing similar files (read them, quote 5–10 lines each).
- The exact compliance rules that apply — from `.cursor/rules/*.mdc`.

> If `AGENTS.md §2/§3` are still placeholder templates, treat
> `docs/architecture.md` + `.cursor/rules/` as the source of truth and say so
> explicitly in the plan. Never plan from a blank section.

### Rule 2 — One section at a time (defeat truncation)
Do NOT ask a small model for the whole plan in one shot. Produce the plan
**section by section**, in this fixed order, finishing each before the next:

1. Goal + Source Evidence (grounded facts)
2. Acceptance Criteria (concrete, testable)
3. Database / API contract
4. Files to Create/Modify table
5. Task Breakdown (one task block at a time)
6. Domain Config Sync + Risks

After each section, the model must literally write `SECTION N COMPLETE` before
starting the next. This converts one long, truncation-prone output into several
short, reliable ones.

### Rule 3 — Fill the template, never redesign it
Small models waste budget re-deriving structure. The structure is already fixed
in `.cursor/agents/architect-planner.md` → **Plan Template**. The model's only
job is to *fill each field with concrete content*. Forbid it from reformatting,
summarizing, or "improving" the template.

### Rule 4 — Ban placeholders (anti-laziness contract)
Paste this contract at the top of the planning prompt:

```
You are writing an EXECUTABLE plan, not a summary.
- Every "Files" entry MUST be a real, full path (e.g. apps/api/src/modules/x/x.service.ts).
- Every acceptance criterion MUST be testable (not "API works").
- FORBIDDEN: "etc.", "and so on", "similar to above", "// TODO", "[continue]".
- If you approach the output limit, stop at a section boundary and write
  [PAUSED - section N of 6]. On "continue", resume with no recap.
- A worker with no memory of this chat must be able to execute the plan from the file alone.
```

### Rule 5 — Self-verify before handoff (cheap quality gate)
Before declaring the plan done, the model answers these against its own plan.
Any "no" ⇒ fix that section, do not hand off:

- [ ] Every task has real file paths and a testable acceptance line?
- [ ] Every task names its owner agent + skill (from `skills-manifest.json`)?
- [ ] Contracts (DB columns, API shapes, shared types) are concrete, not "TBD"?
- [ ] Multi-tenancy respected where required (`workspace_id` / tenant filter)?
- [ ] No placeholder tokens anywhere?
- [ ] Domain Config Sync items each resolved (done or `N/A — reason`)?

---

## 3. Scale the ceremony to the task (KISS)

Small models drown in process. Match rigor to size:

| Task size | Brainstorm | Plan depth | Domain Config Sync |
|---|---|---|---|
| 1 file / < 50 lines | Skip | 1-paragraph rationale, no file | Skip |
| Single module | Short (options in chat) | Full template, 2–5 tasks | Only changed items |
| Multi-module / protected | Full HARD-GATE, 2–3 options | Full template + ADR | Full checklist |

For a small model, **cutting ceremony on small tasks is a quality win** — it
frees the whole attention budget for the actual design.

---

## 4. Ready-to-use planning prompt (copy/paste)

```
ROLE: architect-planner on a lower-capability model. Follow
.cursor/skills/planning/references/planning-with-lower-models.md exactly.

TASK: <one-line objective>

GROUNDING (read + quote real content, do not summarize blanks):
- docs/architecture.md
- .cursor/rules/001-project-standards.mdc (+ any domain rule that applies)
- 1–3 existing similar files: <paths>

OUTPUT CONTRACT:
- Fill the architect-planner Plan Template field-by-field. Do not restructure it.
- Produce sections 1→6 IN ORDER. After each, write "SECTION N COMPLETE".
- Real full paths only. Testable acceptance only. No placeholders / "etc." / TODO.
- If near the output limit: stop at a section boundary, write [PAUSED - section N of 6].

FINISH: run the Rule 5 self-verify checklist. Report the plan path + which
checklist items passed. Do NOT dispatch workers until every item passes.
```

---

## 5. Anti-patterns (do the opposite)

- ❌ "Read AGENTS.md §2 and plan" — those sections are blank; model invents.
- ❌ One giant "write the whole plan" prompt — truncates mid-way.
- ❌ Letting the model paraphrase the template — wastes budget, loses fields.
- ❌ Enforcing full Domain Config Sync on a 1-file change — ceremony smothers design.
- ❌ Accepting "API works" / "add tests" as acceptance criteria — untestable.
- ❌ Handoff without the self-verify pass — pushes vagueness onto the worker.
