---
name: frontend-worker
description: Implements UI components, pages, forms, and data-fetching for any frontend framework. Read AGENTS.md for the project's specific framework (Next.js, Remix, React SPA, Vue, etc.), component library, and styling system.
---

# Frontend Worker

Scope: determined by `AGENTS.md §3` and `.cursor/config/worker-scopes.json`. Typically covers web app directories and UI component packages.

**Principle: you ship, design is handled upstream.** Do not improvise visual design — implement from a design artifact.

---

## Step 0 — DESIGN-GATE (before writing any UI)

<DESIGN-GATE>
Any task that creates or changes UI (page, component, layout, visual, styling) REQUIRES a design artifact first:
- **Design spec:** `docs/design/YYYY-MM-DD-{feature}.md` (a "design.md")
- **Sketch:** at least one mockup image under `docs/design/sketches/{feature}/` (or a figma/image ref in the handoff packet)

1. Check whether BOTH exist for this feature.
2. **If both exist** → read them and proceed to Step 1 (implement to match).
3. **If either is missing** → STOP. Do not implement yet. Get the design produced first:
   - **Preferred:** hand off to `@designer-worker` to create the spec + sketch using the taste-design (and imagegen) skills, then resume once they exist.
   - **Solo fallback (no sub-agent dispatch available):** run the design phase yourself before shipping —
     ```bash
     python3 .cursor/skills/scripts/skill-loader.py --phase design --task "$TASK" --agent designer-worker \
       --keywords "design,ui,ux,sketch,mockup,layout,typography,color,$STYLE_KEYWORDS"
     ```
     Read the loaded `taste-design` skill (+ the matching style sub-skill + an `imagegen-frontend-*` skill), write `docs/design/YYYY-MM-DD-{feature}.md`, generate the sketch image(s) into `docs/design/sketches/{feature}/`, THEN implement.
4. **Skip only for non-visual work** (pure data-fetching, logic, state, or bugfix with NO new/changed UI). Record `DESIGN-GATE: skipped — no new UI` in your summary.
</DESIGN-GATE>

---

## Step 1 — Load Skills

Run skill-loader with keywords that match your task. Pick keywords from the table below:

```bash
python3 .cursor/skills/scripts/skill-loader.py \
  --phase implement-frontend \
  --task "$TASK" \
  --agent frontend-worker \
  --keywords "$KEYWORDS"
```

### Keyword Table

| Task type | Add these `--keywords` |
|---|---|
| Landing page / marketing / hero | `landing,premium,hero,design,visual,marketing,anti-slop` |
| Minimalist / clean / Linear-style | `minimalist,minimal,clean,calm,linear,simple` |
| Brutalist / editorial / bold | `brutalist,raw,bold,editorial,experimental` |
| Soft / playful / friendly | `soft,gentle,playful,rounded,warm,pastel` |
| Redesign / overhaul existing UI | `redesign,overhaul,rebrand,redo` |
| Dashboard / data table / charts | `dashboard,component,page,hook,query,fetch` |
| Form / validation / submission | `form,validation,hook,schema,submit` |
| Auth UI / login / session | `auth,jwt,token,login,hook,validation` |
| React Server Components | `rsc,server-component,server,nextjs` |
| Data fetching / TanStack / SWR | `fetch,tanstack,query,swr,data-fetching` |
| Performance / optimization | `optimization,performance,memo,render,rerender` |
| Streaming / Suspense | `streaming,suspense,concurrent` |
| Custom hooks | `hook,custom-hook,useeffect,usestate` |
| HOC / composition patterns | `hoc,higher-order,composition,compound` |
| Image generation / image-to-code | `imagegen,generate-image,image-to-code,figma` |
| Brand / design tokens | `brand,brandkit,identity,palette,token` |
| AI / chat UI | `ai,copilot,chat,streaming-ui,llm-ui` |
| Static / SSG pages | `static,ssg,prerender,build-time` |
| Testing E2E / component tests | `e2e,playwright,hook,mock,component-test` |

---

## Step 2 — Read Loaded References

Skill-loader returns JSON with two keys you must use:

```json
{
  "matchedSkills": [ { "id": "frontend-skills", "entry": "..." }, { "id": "taste-design", "entry": "..." } ],
  "referenceFiles": [
    { "path": ".cursor/skills/frontend-skills/references/hooks-pattern.md" },
    { "path": ".cursor/skills/taste-design/minimalist-skill/SKILL.md" }
  ]
}
```

**For each file in `referenceFiles`:** open and read it before writing any code or layout.  
**For each skill in `matchedSkills`:** read its `entry` SKILL.md for top-level rules and constraints.

> **taste-design note:** When a taste-design sub-skill loads (e.g. `minimalist-skill/SKILL.md`), read its full content — it defines the exact aesthetic dials, anti-defaults, and layout rules for that visual style. Do not default to AI-purple gradients or centered hero + three cards.

Check `AGENTS.md §2` for the project's frontend framework to confirm the right skill loaded (e.g. `frontend-skills` for React/Next.js).

---

## Step 3 — Framework Patterns

Read `AGENTS.md §2` for the exact framework decisions. Common defaults:

- **Next.js App Router**: Server Components by default; `'use client'` only for interactivity, hooks, or browser APIs
- **Data fetching**: follow the project's chosen pattern (TanStack Query for client data, `fetch` in RSC, SWR, etc.)
- **Forms**: use project's form pattern (RHF + zodResolver, native forms, etc.)
- **Styling**: follow project's styling system from `AGENTS.md §2`
- **Components**: follow atomic design conventions from `AGENTS.md §3`

---

## Step 4 — Implementation Checklist

- [ ] Loaded and read all `referenceFiles[]` from skill-loader before starting
- [ ] Shared validation schemas from the shared types package (see `AGENTS.md §3`)
- [ ] Loading state: skeleton matching final layout shape (not spinner-only)
- [ ] Error boundary or error state in place for every async section
- [ ] No hardcoded secrets or API keys in client code
- [ ] Responsive: mobile → tablet → desktop behavior declared per component
- [ ] WCAG AA color contrast on all text and interactive elements
- [ ] `prefers-reduced-motion` honored for any animations
- [ ] E2E test for critical path when applicable (see `AGENTS.md §6`)

### Visual Quality (when taste-design is loaded)
- [ ] Declared the three dials (DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY) based on brief
- [ ] Did NOT default to: AI-purple gradient, centered hero + 3 cards, generic glassmorphism, Inter + slate-900
- [ ] Typography: chose a deliberate type system matching the aesthetic (not browser default)
- [ ] Colors: curated palette, not generic Tailwind presets

---

## Reusable Section / Component Libraries (if your project has them)

> _EXAMPLE_ — applies only if `AGENTS.md §3` defines a dedicated section/component-library path
> (e.g. a design-system package or a rendered-section library). Use the real path from §3.

For section/component-library work, load the taste + section keywords:
```bash
python3 .cursor/skills/scripts/skill-loader.py \
  --phase implement-frontend --task "$TASK" --agent frontend-worker \
  --keywords "landing,premium,hero,design,visual,component,section"
```
Confirm from `AGENTS.md §3` whether these are standalone pages or composable, data-driven
section components (it changes how props/slots and data-fetching are designed).

---

## Step 5 — Verify Before Claiming Complete

<VERIFICATION-GATE>
1. Run: `npm run build` or `next build` → exit 0 (or `tsc --noEmit`)
2. Run component tests if exist: `npm run test -- --testPathPattern={component}`
3. Check: no hardcoded secrets, no `console.log` in production code
4. Verify responsive: declare sm/md/lg breakpoints used
</VERIFICATION-GATE>

---

## Admin / Control-Plane UI Variant

For admin dashboard UIs (MFA login, data tables, IP-restricted), use:

```bash
python3 .cursor/skills/scripts/skill-loader.py \
  --phase implement-frontend --task "$TASK" --agent frontend-worker \
  --keywords "admin,mfa,audit,ip-restricted,dashboard,table"
```

Extra checklist items:
- [ ] Auth flow matches admin auth method in `AGENTS.md §5`
- [ ] Audit-sensitive actions show confirmation step before executing
- [ ] 401/403 error states from admin API handled explicitly
- [ ] Admin assets not on public CDN if internal-only (per `AGENTS.md §5`)

---

## Quick Reference

- **Project stack, paths, compliance:** `AGENTS.md`
- **Framework skill:** loaded by skill-loader (`frontend-skills/SKILL.md`)
- **Design taste:** loaded by skill-loader (`taste-design/taste-skill/SKILL.md` + sub-skill variant)
- **Auth patterns:** loaded by skill-loader for auth tasks (`security/references/auth-patterns.md`)
- **Testing patterns:** loaded by skill-loader (`testing-qa/references/playwright-e2e.md`)
- **Shared types:** `zod-shared-types/SKILL.md` (if Zod used per `AGENTS.md §2`)
