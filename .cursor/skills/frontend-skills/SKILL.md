---
name: frontend-skills
description: Teaches frontend skills for building modern web applications. Use when you want to learn how to create responsive, interactive, and performant user interfaces with React and related technologies.
paths:
  - "**/*.tsx"
  - "**/*.jsx"
license: MIT

---


---

# 🌐 Frontend Rules (Modern Standard - Agent-Optimized)

## 1. Project Architecture & Organization
- **Strict Feature-based Structure:**
    - Domain-specific code: `src/features/[feature-name]/...` (includes components, hooks, types, api).
    - Global UI: `src/components/[atom|molecule|organism]` for project-wide reusable components (Button, Modal, Input).
- **Logic Decoupling:**
    - UI Components must be **Presentational** only.
    - **Constraint:** All data fetching, complex calculations, and state orchestration must be extracted to **Custom Hooks**.

## 2. TypeScript & Data Integrity
- **Strict Typing:**
    - **Forbidden:** Explicit `any`. Use `unknown` or specific `Interfaces/Types`.
    - **Component Props:** Every component must have an explicit `Props` interface.
- **DTO Synchronization:** Align Frontend `Interfaces` with `@shared/type`. Use shared types or automated type generation where possible.

## 3. State & Data Flow
- **Server State (TanStack Query/SWR):**
    - **Mandatory:** Use for all API-driven data. 
    - **Implementation:** Utilize `isLoading`, `isError`, and `data` objects. Set `staleTime` and `gcTime` (cacheTime) based on resource volatility.
- **Client State Rules:**
    - **Local State:** Use `useState` / `useReducer` by default.
    - **Global State (Zustand/Redux):** Use only for cross-cutting concerns (Auth, Theme, User Settings).
    - **Derived State:** **Forbidden** to create new state for values calculable from existing props or state. Use `useMemo` for heavy derivations.

## 4. Networking & API Integration
- **Centralized Client:** Use a single `Axios` instance or `fetch` wrapper.
- **Interceptors Logic:**
    - **Request:** Automatically attach `Authorization: Bearer <token>`.
    - **Response:** Handle `401 Unauthorized` globally (trigger logout/redirect).
- **Environment Management:** Use `NEXT_PUBLIC_` or environment-specific prefixes for API Base URLs.

## 5. Forms & Validation
- **Schema-driven:** Use `React Hook Form` integrated with `Zod` or `Yup`.
- **Backend Parity:** UI validation schemas must mirror Backend `class-validator` constraints.
- **Submission UI:** 
    - **Rule:** Submit buttons must be `disabled` during `isSubmitting` state.
    - Show specific field errors immediately after validation failure.

## 6. Performance Optimization
- **Asset Handling:**
    - Use Framework-specific Image components (e.g., `next/image`).
    - **Constraint:** Images must be `.webp` and lazy-loaded by default.
- **Efficiency:**
    - **Code Splitting:** Use `React.lazy()` or `dynamic()` for heavy components and routes.
    - **Memoization:** Apply `useMemo` and `useCallback` only for expensive computations or to prevent broken dependency chains in hooks.

## 7. Security & Compliance
- **Injection Protection:** Sanitize all inputs. Avoid `dangerouslySetInnerHTML` unless explicitly sanitized.
- **Auth Storage:** Store JWTs in `HttpOnly Cookies` or `In-Memory` (avoid `localStorage` for sensitive tokens).
- **Env Hygiene:** Never expose Private Keys or Secrets to the client bundle.

## 8. UI/UX & Styling Standards
- **Design Consistency:** Strictly follow the Design System (Color palette, Spacing scale, Typography).
- **Responsiveness:** Adopt a **Mobile-first** approach.
- **Error Resilience:** Wrap major feature modules in `Error Boundaries`.
- **User Feedback:**
    - **Latency:** Show `Skeleton` loaders for any task > 200ms.
    - **Interactivity:** All interactive elements must have `:hover` states and `cursor: pointer`.

## 9. Testing & Quality Control
- **Logic Coverage:** Write **Unit Tests** (Vitest/Jest) for utility functions and complex hook logic.
- **Interaction Testing:** Use `React Testing Library` for critical user flows.
- **Linting & Formatting:** 
    - Enforce `ESLint` (Airbnb/Recommended) and `Prettier`.
    - **Git Hooks:** Use `Husky` to block commits failing `lint-staged` or `type-check`.

## 10. Development Workflow
- **Commit Format:** Use **Conventional Commits** (`feat:`, `fix:`, `refactor:`, `chore:`).
- **Documentation:** Use **Storybook** for UI components to ensure visual consistency and documentation.

## 11. Architecture Patterns

Before implementing any task, load the relevant frontend implementation
knowledge using the Frontend Skills Matcher.

The matcher should receive:

- current task description
- implementation plan
- additional keywords (optional)

The matcher returns

- matched atomic skills
- architecture references
- implementation best practices
---
