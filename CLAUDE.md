# CLAUDE.md — Build Workflow Configuration

Add the sections below to your project's or global `~/.claude/CLAUDE.md` to activate the workflow.

## Core Principles

**Simplicity above all.** Every line of code must justify its existence with a clear functional requirement.

- **Minimum viable code**: Implement only what's needed now. No speculative features, no "just in case" abstractions.
- **3x rule**: Don't extract/abstract until you see the same pattern 3+ times.
- **Functions over classes**: Before adding a class, ask "Can a function do this?" Before adding an abstraction, ask "Will this hurt readability?"
- **Propose simplest solution first**, then ask if more complexity is needed.
- **No laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal impact**: Changes should only touch what's necessary. Avoid introducing bugs.

### Demand Elegance (Balanced)

For non-trivial changes, pause and ask: "Is there a more elegant way?" If a fix feels hacky, step back and implement the solution you'd write starting fresh with everything you know now. **Skip this for simple, obvious fixes** — don't over-engineer a one-line change. Challenge your own work before presenting it, but don't let perfect be the enemy of good.

### Refactoring Discipline

Refactoring is changing internal structure without changing external behavior. It is a disciplined, micro-step process — not a rewrite.

**The Two Hats Rule (MANDATORY):** Never mix refactoring with feature work. Each commit is either a structural change (refactoring) or a behavioral change (feature/fix), never both. When wearing the refactoring hat: no new behavior, no new tests for new features. When wearing the feature hat: no renaming, extracting, or reorganizing.

**Micro-Steps:** Every refactoring operation must be a single, named transformation (Extract Method, Rename, Inline, Move). Run all tests after each step. If any test goes red, undo immediately to last green state. Commit after each successful step.

**Safety Net First:** Never refactor code without test coverage. If coverage is insufficient, write characterization tests first — tests that capture current behavior as a baseline. Refactoring without tests is gambling, not engineering.

**When to Refactor (Fowler's Four Workflows):**
- **Preparatory:** Before adding a feature — "make the change easy, then make the easy change" (Kent Beck)
- **Comprehension:** When you struggle to understand code — encode your understanding into better names and structure
- **Litter-Pickup:** When you encounter mess during normal work — leave code cleaner than you found it
- **Planned:** Deliberate campaigns against known hotspots (high change frequency + low quality)

**When NOT to Refactor:**
- No test coverage exists (add characterization tests first)
- Code that never changes (stable, rarely-touched code regardless of ugliness)
- More than one hour of tidying before a behavior change (Kent Beck's rule — reassess scope)
- You can't keep tests passing throughout (that's a rewrite, not a refactoring — needs its own plan)

**Hotspot Priority:** Prioritize by `change_frequency * code_quality_issues * business_impact`. The top 5% of frequently-changed code receives 90% of changes — focus refactoring there, not on stable legacy code.

**AI-Specific Rules:**
- After AI-generated refactoring, verify the result is not more verbose or complex than the original. AI produces ~2x more code on average — simplify before committing.
- Use automated quality gates as a feedback loop: assess health, refactor, validate, repeat.
- Never accept AI refactoring output without reviewing for unnecessary abstractions, bloat, or pattern-stuffing.

**Anti-Patterns:**
- Premature abstraction (wait for 3x rule)
- Over-extracting into too many tiny functions (each extraction must improve readability)
- Design-pattern stuffing (Strategy, Factory, Observer when a function suffices)
- Refactoring as procrastination (endless cleanup instead of delivering the feature)
- Big-bang rewrites disguised as refactoring

### Testing Philosophy

- **Prefer real infrastructure** over mocks for database ops, SQL, transactions, schema validation
- **Use mocks** for unit tests of business logic and external APIs without dev environments
- Write tests for actual requirements, not hypothetical edge cases
- If a test feels overly complex, the code being tested is probably too complex

## Development Workflow

### Planning Rule (MANDATORY)

**IMPORTANT: For ANY non-trivial task, you MUST use the `/two-agent-planning` skill.** Do NOT enter plan mode directly. Do NOT use the generic Plan sub-agent. Do NOT write freeform plans.

"Non-trivial" = multiple files, new features/pages, architectural decisions, phased work, or user asks for a "plan." Only exception: truly trivial changes or user explicitly opts out.

### Execution Rule (MANDATORY)

**IMPORTANT: When an approved plan exists from `/two-agent-planning`, you MUST use `/building-against-plan` to execute it.** Never implement directly — the skill enforces TDD discipline, quality gates, and test immutability. Only exception: user explicitly says "implement directly."

### Test-Driven Development (TDD)

Always use TDD: **Red** (write failing test) -> **Green** (minimal code to pass) -> **Refactor** (clean up, all tests passing). All new functionality must have tests before it's considered complete.

### General Workflow

1. **Before starting**: Ask clarifying questions, confirm simplest approach
2. **Before committing**: Run all quality checks
3. **After all tests pass**: Commit with descriptive message. Push to remote when appropriate.
4. **CLAUDE.md updates**: Only for substantial changes (new features, architectural changes).

### If Things Go Sideways — STOP and Re-Plan

If your approach hits unexpected resistance — tests failing unpredictably, architecture not fitting, cascading changes growing out of control — **STOP immediately.** Do not keep pushing. Step back, reassess, re-plan. It is always cheaper to re-plan than to debug a bad approach into working.

### Project Artifacts

All non-code artifacts go in `.claude/` within the project directory:
- **Plans** -> `.claude/plans/` | **Outputs** -> `.claude/outputs/` | **Verifications** -> `.claude/verifications/`
- **Handoffs** -> `.claude/handoff.md` | **Session notes** -> `.claude/notes/`
- **Todo list** -> `.claude/todo.md`
- Naming: kebab-case, include dates for time-sensitive files (`YYYY-MM-DD-description.md`)
- Create directories as needed. Never write artifacts to project root or `src/`.

## Behavioral Principles

### Ask Clarifying Questions (REQUIRED)

**IMPORTANT: You must ask clarifying questions before writing any plan or code when encountering ambiguity.** Don't make assumptions. Present options with trade-offs backed by best practices. Always present the simplest approach first.

**Exception — Autonomous Bug Fixing**: When given a bug report, **just fix it.** Don't ask for hand-holding. Point at logs, errors, failing tests — then resolve them. Zero context switching for the user. (Still ask if the bug description itself is genuinely ambiguous.)

### UI Walkthrough Before Done (MANDATORY)

After any UI change, before declaring it complete, mentally walk through these 3 scenarios:
1. **Happy path** — user changes fields and saves
2. **Empty path** — user opens the UI, changes nothing, saves/closes
3. **Sidecar path** — user only interacts with the new thing you added (not the existing fields), then saves

For each scenario, trace the full execution: what gets called, what gets sent to the backend, what happens on success/failure. If any scenario produces an error, empty payload, or unhandled state — fix it before calling the task done.

### Verification Before Done

Never mark a task complete without proving it works:
- Run tests, check logs, demonstrate correctness
- Walk through UI scenarios (see above) for any frontend changes
- Ask yourself: **"Would a staff engineer approve this?"**
- If you can't confidently answer yes, keep going

## Sub-Agents and Skills

### Sub-Agent Philosophy

**Use sub-agents liberally.** They keep the main context window clean — your most important resource.

- **Default to delegation** for research, exploration, and parallel analysis
- **One task per sub-agent** for focused execution
- For complex problems, throw more compute at it via sub-agents
- Launch multiple agents in parallel for independent tasks

### Development Workflow

**Primary entry point: `/build`** — routes all work through the right skill:
- Small (1-3 files, single change) -> `/small-feature`
- Medium (4-8 files, clear requirements) -> `/two-agent-planning` simple variant
- Large (8+ files, arch decisions) -> `/two-agent-planning` complex variant

The `/build` skill performs a Boy Scout scan of files to be touched and injects cleanup
findings into the downstream skill. Refactoring is woven into feature work automatically.

**Standalone analysis skills** (not part of `/build` flow):
- `/refactor` — codebase analysis, requires scope parameter, functionality-only

### Skills

Invoke skills via `/skill-name` or the Skill tool. Key skills: `/build` (primary entry point), `/two-agent-planning` (MANDATORY for planning), `/building-against-plan` (MANDATORY for execution). Proactively suggest skills when a user's request matches one.
