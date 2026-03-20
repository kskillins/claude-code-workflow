---
name: small-feature
description: >
  TDD-based workflow for small-to-medium features, bug fixes, and updates that don't warrant
  full two-agent-planning. Enforces Red-Green-Refactor discipline with project-specific guardrails
  derived from historical bug analysis. Use when the change touches 1-3 files, adds a single
  feature or fixes a bug, and doesn't require architectural decisions. If the scope grows beyond
  this during implementation, escalate to /two-agent-planning.
---

# Small Feature Implementation

Disciplined workflow for changes too small for `/two-agent-planning` but too important to wing. Enforces TDD and runs targeted checks based on what you're changing.

## When to use

- Bug fixes (single root cause)
- Adding a field, endpoint, or UI element
- Wiring up a new API call
- Adjusting layouts, formats, or display logic
- Changes touching 1-3 files

## When to escalate to /two-agent-planning

- Scope grows beyond 3 files during implementation
- You discover an architectural decision is needed
- Multiple phases of work emerge
- The change affects more than one user flow end-to-end

## Workflow

### Step 1: Scope check (30 seconds)

Before writing any code, answer these:

1. **What changes?** List every file you expect to touch.
2. **Backend, frontend, or both?**
3. **Which role uses this?** Technician, Office Staff, Admin, or all?
4. **Mobile-relevant?** Will a technician see this on a phone?

5. **Preparatory refactoring check**: Before writing new code, assess the structural
   readiness of the code you're about to modify:
   - **3x consolidation**: Search for existing functions that do something similar. If
     2+ exist, extract a shared helper first (separate commit), then build on it.
   - **Long function**: If the function you're modifying is >50 lines, Extract Method
     to isolate the section you'll change.
   - **Growing parameters**: If you'd add a 4th+ parameter, Introduce Parameter Object first.
   - **Unclear naming**: If adding your feature would create confusing variants, rename
     the original first.
   If any preparatory refactoring would touch 4+ files, escalate to `/two-agent-planning`.

If you can't answer these clearly, ask the user before proceeding.

### Step 2: Identify hazards

Based on the scope check, flag applicable hazards from this checklist:

- [ ] **Pydantic model change** — Are you adding/changing a field? Verify the Update model, Create model, AND the frontend form config all include it.
- [ ] **New or modified FK join** — Does any `.select()` call join a table with multiple FK paths? Use explicit `!fk_name` hint syntax.
- [ ] **DELETE endpoint** — Have you audited ALL inbound FK references to the target table? Check for ON DELETE RESTRICT constraints.
- [ ] **Date/time logic** — Are you using `dayjs().tz('America/New_York')` and NOT `new Date()`?
- [ ] **Form submission** — Are empty strings converted to null before sending to the API? UUID fields reject `""`.
- [ ] **TanStack Query** — If the query is conditional/disabled, are you checking `isFetching` or `isEnabled` alongside `isPending`?
- [ ] **Optimistic updates** — Using `onMutate` with snapshot + `onError` rollback? (NOT `onSuccess` with `setQueryData`)
- [ ] **Cache invalidation** — Does your mutation affect data displayed by other queries? (e.g., editing users affects TechnicianCell cache)
- [ ] **Mobile layout** — Any new flex containers, buttons, or text that could overflow at 375px width?

### Step 3: Write failing test (Red)

Write ONE focused test that defines the expected behavior. Follow the project's testing patterns:

**Backend:** Use `make_db_mock()` from `tests/conftest.py`. Patch `get_db` at the router level. Use `auth_headers(role, sub)` for auth.

**Frontend:** Use Vitest + React Testing Library. Tests in `frontend/src/__tests__/`.

The test MUST fail before you write implementation code. If it passes immediately, your test isn't testing the new behavior.

### Step 4: Implement (Green)

Write the minimum code to make the test pass. No extras, no cleanup, no "while I'm here" changes.

**Checkpoint after Green:**
- Run the full test suite (not just your new test) to catch regressions
- If any existing test breaks, fix your implementation — never edit the existing test

### Step 5: Boy Scout Rule (mandatory scan)

After Green, examine the code you touched in Step 4. This is a mandatory scan — though
the outcome may be "nothing to clean."

1. **Scan the modified functions** for:
   - Unused imports in files you touched
   - Misleading names in code you just wrote or modified
   - Duplication you introduced or discovered (3x rule — only extract if 3+ occurrences)
   - TODO/FIXME comments you can resolve right now

2. **If Boy Scout findings were provided by /build**, apply them now as micro-steps.

3. **Each cleanup is one micro-step**:
   - Make one named change (Rename, Remove Import, Extract Method)
   - Run tests
   - If red, undo immediately
   - If green, continue to next cleanup

4. **Scope-bounded, not time-bounded**: Scan only the files you touched. Do not expand
   into unrelated files. But within the files you touched, be thorough — take the time
   to do it right.

5. **Skip criteria**: Only skip if the scan finds nothing AND no Boy Scout findings
   were provided.

6. **Commit discipline**: Cleanups go in a SEPARATE commit from the feature change
   (Two Hats Rule). Feature commit first, then cleanup commit.

### Step 6: Mandatory verification gates

Run ALL applicable gates before marking done:

#### Always run:
- [ ] Full backend test suite passes
- [ ] Frontend build passes (catches type errors)
- [ ] Frontend tests pass

#### If you touched frontend UI:
- [ ] **Mobile viewport check**: Verify the change at 375px width in Chrome DevTools mental model. Ask yourself: "Does this overflow? Are touch targets >= 44px? Does text truncate correctly?"
- [ ] **UI state enumeration**: For the component you changed, verify rendering in ALL states: empty, loading, error, single item, many items, disabled
- [ ] **3-scenario walkthrough**:
  - Happy path: user interacts normally and saves
  - Empty path: user opens UI, changes nothing, saves/closes
  - Sidecar path: user only interacts with the new element, then saves

#### If you touched a Pydantic model:
- [ ] All fields in the Update model match what the frontend can send
- [ ] Empty string handling: optional FK fields coerce `""` to `None`

#### If you touched a `.select()` join:
- [ ] No FK ambiguity (use `!fk_name` hint if table has multiple FK paths to same target)
- [ ] Nested joins return data (PostgREST silently returns null for unsupported multi-hop joins)

#### If you touched date logic:
- [ ] No `new Date()` for date calculations — use `dayjs().tz('America/New_York')`
- [ ] Date strings sent to API are in the format the backend expects (usually `YYYY-MM-DD`)

### Step 7: Commit

Write a descriptive commit message. Separate refactoring commits from behavior-change commits (Two Hats Rule).

## Escalation triggers

Stop and escalate to `/two-agent-planning` if:
- You're on your 3rd file and the change is growing
- A test reveals a deeper issue that requires architectural changes
- You realize the "small" change actually needs a migration, new table, or new API pattern
- You've been debugging for > 30 minutes without progress

## Anti-patterns

- Skipping the test because "it's just a one-liner" — one-liners have caused multi-commit bug chains
- Fixing the test instead of the implementation
- Adding error handling for impossible scenarios
- "Improving" adjacent code while you're in the file (wear one hat at a time)
- Committing without running the full test suite
- Assuming mobile works because it looks fine on desktop
