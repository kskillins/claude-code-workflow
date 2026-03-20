---
name: building-against-plan
description: Executes approved implementation plans using strict Test-Driven Development. Builds code phase-by-phase with tests written first, automates quality gates (lint, type checks, test suites), and enforces that tests are never edited to pass. Use after the two-agent-planning skill produces an approved plan, when the user says to build or implement a plan, or when thorough TDD-based execution of a structured plan is needed.
---

# Building Against Plan

Execute approved implementation plans through strict TDD with automated quality gates. Every function gets tested, every edge case gets covered, and tests are never modified to pass -- only production code is refactored.

## Core principles

1. **Tests are immutable once written** -- never edit, delete, or skip a test to make it pass. Refactor production code until the test passes as originally written.
2. **Red-Green-Refactor** -- write a failing test, write minimal code to pass it, refactor while green. No exceptions.
3. **KISS** -- implement the simplest thing that works. No abstractions until duplication demands them. No "just in case" code.
4. **DRY** -- extract duplication only after it appears. Three similar lines are better than a premature abstraction.
5. **Real connections** -- use real databases, real APIs, real file systems in tests where possible. Mock only when a real dependency is unavailable, destructive, or non-deterministic.
6. **Quality gates are mandatory** -- every phase ends with automated checks that must pass before proceeding.
7. **No over-engineering** -- solve the stated problem, not a hypothetical general case.

## Agent delegation

Each step in the build workflow delegates to a specialized agent. Use the Task tool to launch these agents — they are experts in their domain.

| Step | Agent | Responsibility |
|------|-------|---------------|
| Environment setup | **project-bootstrapper** | Detect stack, install deps, configure tooling |
| Write tests (Red) | **qa-test-engineer** | Write failing tests from plan's testable behaviors |
| Confirm failure | **test-runner** | Run tests, verify they fail for the right reason |
| Implement (Green) | **feature-implementer** | Write minimal code to pass tests |
| Verify passing | **test-runner** | Run full suite, confirm all green |
| Fix failures | **debugger** | Diagnose and fix production code (never tests) |
| Refactor | **code-refactorer** | Improve structure while tests stay green |
| Edge case tests | **qa-test-engineer** | Write edge case tests for boundary/error/null cases |
| Quality gates | **test-runner** | Run lint, type check, format, build |
| Code review | **code-quality-reviewer** | Review for quality, KISS, DRY, security |

## Workflow

### Phase 0: Plan ingestion and environment setup

#### Plan compatibility check

Before starting any implementation, verify the plan contains the required structure:

- [ ] Each phase has **Testable Behaviors** (bulleted list with function/endpoint names, inputs, outputs, errors)
- [ ] Each phase has **Success Criteria** (concrete, verifiable conditions — not vague "it works" statements)
- [ ] Each phase has **Dependencies** (what must be true before the phase starts)
- [ ] Phases are ordered with highest-risk work first

**If the plan lacks any of these:** Do NOT guess or improvise the missing sections. Ask the user to re-run `/two-agent-planning` to produce a complete plan. Implementing against an incomplete plan leads to tests that don't match requirements and wasted effort.

**If the plan has code snippets but missing testable behaviors:** The code snippets are implementation hints, not substitutes for test specifications. Extract testable behaviors from the snippets before proceeding, or ask the user to re-plan.

#### Plan ingestion

1. Read the approved plan (from two-agent-planning output or user-provided plan)
2. Verify plan compatibility (checklist above)
3. Identify all phases, tasks, deliverables, and success criteria
4. **Delegate to project-bootstrapper agent** to:
   - Detect the project type and tech stack
   - Identify existing test frameworks and linters
   - Install missing tooling
   - Verify the test command works
4. Create the progress checklist (copy and update throughout):

```
Build Progress:
- [ ] Phase 0: Environment setup and plan ingestion
- [ ] Phase 1: [first plan phase name]
  - [ ] Tests written (Red)
  - [ ] Implementation complete (Green)
  - [ ] Refactored
  - [ ] Edge cases tested
  - [ ] Quality gates passed
- [ ] Phase 2: [second plan phase name]
  ...
- [ ] Final: Full test suite + quality gates + success criteria verified
```

### Phase N: TDD implementation (repeat for each plan phase)

For each phase defined in the plan, execute the following loop. See [references/tdd-rules.md](references/tdd-rules.md) for detailed enforcement rules.

#### Step 1: Write failing tests (Red)

Before writing any production code for this phase:

1. Read the phase's deliverables and success criteria from the plan
2. **Delegate to qa-test-engineer agent** to write tests that define the expected behavior:
   - One test per function or method being introduced
   - Use descriptive names: `test_<function>_<scenario>_<expected_outcome>`
   - Follow Arrange-Act-Assert pattern
   - Use real connections (database, API, filesystem) where available
3. **Delegate to test-runner agent** to run tests and confirm they fail for the right reason (import error, missing function, wrong result -- not syntax error in the test)

#### Step 2: Implement minimal code (Green)

1. **Delegate to feature-implementer agent** to write the simplest production code that makes all tests from Step 1 pass
2. **Delegate to test-runner agent** to run the full test suite (not just new tests) to catch regressions
3. If any test fails:
   - **DO NOT edit the test**
   - **Delegate to debugger agent** to diagnose and fix the production code
   - **Delegate to test-runner agent** to verify the fix
   - Repeat until all tests are green

#### Step 3: Refactor (while green)

**The Two Hats Rule:** This step wears the refactoring hat ONLY. No new behavior, no new tests for new features. Only structural improvements while all tests stay green.

1. **Delegate to code-refactorer agent** with these priorities (in order):
   - Duplicate code that has appeared 3+ times (the 3x rule)
   - Unclear variable or function names (comprehension refactoring)
   - Functions longer than ~30 lines (Extract Method)
   - Deeply nested conditionals, 3+ levels (Replace Conditional with Polymorphism or early returns)
   - 5+ parameter functions (Introduce Parameter Object)
2. **Micro-steps only**: Each change must be a single, named transformation from Fowler's catalog (Extract Method, Rename, Inline, Move). If you can't name it, reconsider.
3. **Delegate to test-runner agent** after EACH micro-step, not after a batch
4. If any test fails after a refactoring change:
   - **Immediately undo** to last green state (one change away)
   - Try a different refactoring approach
   - If multiple approaches fail, **leave the code as-is** — working beats elegant
5. **Do NOT refactor:**
   - Code that works and is readable (no gold-plating)
   - Code in other parts of the codebase not related to the current phase
   - Stable, rarely-changed code (hotspot priority — focus on high-change areas)
6. **One-hour rule**: If refactoring has consumed more than one hour without making the actual behavior change, stop and reassess scope
7. **AI output review**: If the refactored code is longer or more complex than the original, question whether it improved anything. AI tends to produce ~2x more code — simplify before accepting
8. **Commit discipline**: Refactoring commits must be separate from behavior-change commits. Never mix structural and behavioral changes in one commit

#### Step 4: Edge case tests

1. **Delegate to qa-test-engineer agent** to write tests for every function or method in this phase:
   - Boundary values (zero, empty, null, max values)
   - Error conditions (invalid input, missing data, connection failures)
   - Concurrency concerns (if applicable)
   - Type edge cases (wrong types, unexpected formats)
2. **Delegate to test-runner agent** -- edge case tests should fail initially (Red)
3. **Delegate to debugger agent** to refactor production code to handle edge cases (Green)
4. **DO NOT edit the edge case tests to make them pass**

#### Step 5: Quality gates

**Delegate to test-runner agent** to run all quality gates for the current phase. See [references/quality-gates.md](references/quality-gates.md) for the full gate list.

1. Run the full test suite
2. Run the linter
3. Run the type checker (if applicable)
4. Run the formatter check (if applicable)
5. If failures, **delegate to debugger agent** to fix production code only
6. **Delegate to test-runner agent** again to verify -- repeat until all gates pass

#### Step 6: Phase verification

1. **Delegate to code-quality-reviewer agent** to review the phase's code for quality, KISS, DRY, and security
2. If the reviewer identifies issues, **delegate to debugger agent** or **feature-implementer agent** to fix them, then **delegate to test-runner agent** to verify
3. **UI walkthrough (mandatory for any frontend changes):** Before checking off success criteria, mentally trace through these 3 scenarios:
   - **Happy path** -- user fills in fields / interacts normally and saves
   - **Empty path** -- user opens the UI, changes nothing, saves or closes
   - **Sidecar path** -- user only interacts with the newly added element (not existing fields), then saves
   - For each scenario, trace the full execution: what gets called, what gets sent to the backend, what happens on success/failure. If any scenario produces an error, empty payload, or unhandled state -- fix it before proceeding.
4. Check off each success criterion from the plan for this phase
5. If a success criterion requires running a server, connecting to a database, making an API call, or executing a user-facing action -- do it and verify the result
6. Document any deviations from the plan and why they occurred
7. If a phase success criterion cannot be met, stop and report the issue to the user before continuing

#### Step 7: Boy Scout check (after each phase)

Before advancing to the next phase, scan files modified in this phase for problems
introduced or revealed by this phase's work:

1. **Scan for** (new issues only — not pre-existing debt):
   - New unused imports (from refactoring that removed usages)
   - New naming inconsistencies (a renamed function that left callers with old name style)
   - New duplication (copy-paste from another phase's code)
   - Long functions created or grown by this phase (>50 lines — Extract Method)
   - Growing parameter lists (4+ params — Introduce Parameter Object)
2. **If found**: Apply as micro-steps with test verification. Commit separately.
3. **Scope-bounded, not time-bounded**: Scan only files modified in this phase.
   Be thorough within that scope — take the time to produce clean code.
4. **Do NOT**: Scan unrelated files. Refactor code not touched in this phase.
   Spend time on subjective style preferences.

#### Project-specific verification gates

Add your own project-specific gates here based on historical bug analysis. Common categories:

**After any backend phase:**
- Model/schema alignment (e.g., Pydantic models match frontend form fields)
- FK join ambiguity checks
- DELETE cascade audit
- Date/time format consistency between frontend and backend
- Auth role coverage (every allowed/disallowed role tested)
- State machine transition coverage
- Idempotency verification for state-changing endpoints

**After any frontend phase:**
- Mobile viewport verification (375px width)
- Timezone handling (consistent library usage, no raw `new Date()`)
- Empty string → null conversion for optional fields
- Cache invalidation coverage for mutations
- Test coverage for API-calling components

### Final validation

After all phases are complete:

1. **Delegate to test-runner agent** to run the full test suite and all quality gates across the entire codebase
2. **Delegate to code-quality-reviewer agent** for a final review of the complete implementation
3. Verify every success criterion from every phase of the plan
4. Verify the plan's overall verification strategy
5. **Delegate to claude-md-updater agent** to update CLAUDE.md with the new implementation context
8. **Test suite health (optional):** If the build added 10+ new tests, consider
   recommending `/testing-suite-refactor` to the user as a follow-up to check for
   overlap with existing tests.
6. Report results:

```
Build Complete:
- Total tests: [count]
- Tests passing: [count]
- Code coverage: [percentage if available]
- Lint issues: [count, should be 0]
- Type errors: [count, should be 0]
- Plan phases completed: [X/Y]
- Success criteria met: [X/Y]
- Project-specific gate issues: [count, should be 0]
- Deviations from plan: [list or "none"]
```

## Critical rules

These rules override all other guidance when there is a conflict:

1. **NEVER edit a test to make it pass.** If a test is failing, the production code is wrong. Fix the production code.
2. **NEVER delete a test.** If a test seems wrong, ask the user before removing it. Even then, prefer fixing the production code.
3. **NEVER skip a quality gate.** If a gate is failing, fix the code. Do not disable the gate.
4. **NEVER mock what you can test for real.** If a database is available, test against it. If an API is reachable, call it. Mock only as a last resort.
5. **STOP on plan failure.** If a phase's success criteria cannot be met, stop and report to the user. Do not silently skip criteria.
6. **NEVER skip project-specific gates.** If you've defined project-specific gates, they exist because of real bugs. They are not optional polish.

## Conditional workflow

**Frontend projects** (React, Vue, Angular, etc.):
- Start a dev server to verify rendering and interactions
- Run component tests with a real DOM (jsdom or similar)
- Verify user-facing behavior by executing the actions the interface would trigger

**Backend projects** (APIs, services, workers):
- Start the server and make real HTTP requests in tests
- Test against real databases when available (use test database/schema)
- Verify API contracts match the plan's specifications

**Full-stack projects**:
- Build and test backend first (it's the dependency)
- Build and test frontend against the real backend
- Run end-to-end tests that exercise the full stack

**Data/ML projects**:
- Test data transformations with real data samples
- Validate model inputs/outputs with concrete examples
- Test SQL queries against a real database connection

## When to re-plan

If during execution:
- A phase consistently fails and refactoring cannot resolve it
- A fundamental assumption in the plan proves wrong
- New requirements emerge that invalidate the plan

**Stop building. Report the issue to the user.** Suggest re-running the two-agent-planning skill with the new information incorporated.

## Anti-patterns to avoid

**TDD anti-patterns:**
- Writing implementation code before tests exist for it
- Editing tests to match buggy implementation instead of fixing the implementation
- Adding "temporary" workarounds that bypass quality gates
- Mocking something that could be tested with a real connection
- Skipping edge case tests because "the happy path works"

**Refactoring anti-patterns:**
- Building abstractions before duplication exists (wait for 3x rule)
- Mixing refactoring and feature work in the same commit (Two Hats Rule)
- Refactoring without test coverage (write characterization tests first)
- Big-bang rewrites disguised as refactoring (must keep tests green throughout)
- Over-extracting into too many tiny functions (each extraction must improve readability, not just reduce line count)
- Design-pattern stuffing (Strategy, Factory, Observer when a simple function suffices)
- Refactoring stable, rarely-changed code that nobody needs to modify (hotspot priority)
- Accepting AI-generated refactoring that's more verbose than the original without simplifying
- Refactoring for more than one hour without making the actual behavior change (Kent Beck's one-hour rule)
- Gold-plating during refactor (adding "improvements" that are actually new features)

**General anti-patterns:**
- Adding error handling for impossible scenarios
- Writing more code than the plan requires

## References

- **TDD enforcement rules**: See [references/tdd-rules.md](references/tdd-rules.md) for the detailed Red-Green-Refactor protocol and test immutability rules
- **Quality gate automation**: See [references/quality-gates.md](references/quality-gates.md) for per-stack quality gate commands and failure handling
