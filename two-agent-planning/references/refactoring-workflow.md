# Refactoring Workflow — Planning from /refactor Output

## When this applies

Use this workflow variant when the user runs `/refactor` first, then invokes `/two-agent-planning` to plan the application of findings. The refactor skill produces structured findings in `.claude/refactor/` — this guide tells the planner how to consume them.

## Input artifacts

The `/refactor` skill produces:
- **Phase findings**: `.claude/refactor/{DATE}_round_{N}_phase_{N}_{name}.md` — one file per phase per round
- **HTML report**: `.claude/refactor/{DATE}_refactor_report.html` — aggregated interactive report
- **Script data**: `{DATE}_complexity.json`, `{DATE}_clones.json`, `{DATE}_hotspots.json`

The planner should read the **phase findings files** (not the HTML report) as primary input. The HTML report is for human review; the markdown files have the structured data.

## Finding format (what the planner will see)

Each finding has:
- **ID**: `P{phase}-R{round}-{seq}` (e.g., `P3-R1-001`)
- **File**: path and line number
- **Severity**: Critical, Major, Minor
- **Status**: New, Confirmed (validated across rounds), Resolved
- **Description**: What the issue is
- **Recommendation**: Named refactoring operation (e.g., "Extract Method", "Rename Variable")

Severity meanings:
- **Critical**: Actively causes bugs, data loss, or security issues
- **Major**: Significantly harms maintainability, readability, or testability
- **Minor**: Style issue, mild smell, or opportunity for improvement

## Planning rules for refactoring

### Two Hats Rule (MANDATORY)

Each phase in the plan must be either a **structural change** (refactoring) or a **behavioral change** (feature/fix), never both. Refactoring phases change internal structure without changing external behavior. This means:
- No new features in refactoring phases
- No new tests for new behavior — only characterization tests that capture existing behavior
- Tests must stay green after every micro-step

### Grouping findings into phases

Group findings by **locality and dependency**, not by phase number:

1. **Same-file findings** that touch overlapping code go in the same phase
2. **Dependent findings** where one must be applied before another go in sequential phases
3. **Independent findings** in different files can be parallelized or ordered by severity

Prioritize by: `severity > confirmed status > hotspot score > locality`.

Critical and Confirmed findings come first. Minor findings at the end (or deferred entirely if scope is large).

### Phase structure for refactoring

Each phase should specify:

1. **Which findings it addresses** — list finding IDs (e.g., P3-R1-001, P2-R2-003)
2. **The named refactoring operations** — in execution order (e.g., "Extract Method `validate_input` from `create_user`", "Rename `x` to `validation_result`")
3. **Testable Behaviors** — for refactoring, these are **characterization tests**: tests that capture the current behavior before the refactoring is applied. The function/endpoint should produce the same outputs after refactoring.
4. **Success Criteria** — "All existing tests pass. No behavioral change. [specific structural assertion, e.g., 'function X no longer exists, replaced by Y and Z']."
5. **Rollback trigger** — "If any test goes red, undo to last green state immediately."

### Micro-step sequencing

Within each phase, tasks must be atomic refactoring operations:
- Extract Method / Extract Function
- Rename (variable, function, class, file)
- Inline (variable, function)
- Move (function to module, method to class)
- Replace conditional with polymorphism
- Introduce parameter object

Each task = one operation + run tests. Never batch multiple operations before testing.

### Handling findings that need tests first

If a finding targets code with no test coverage:
1. Add a **characterization test phase** before the refactoring phase
2. The characterization tests capture current behavior as-is (even if that behavior is buggy)
3. Only then apply the refactoring, keeping characterization tests green

### Deferral

Not all findings need to be addressed. The planner should recommend deferring:
- Minor findings in stable, rarely-changed code
- Findings that would require large-scale changes disproportionate to their severity
- Findings where the recommended fix is subjective or debatable

Explicitly list deferred findings and why in a **Deferred Findings** section.

## Example phase structure

```markdown
### Phase 1: Characterization tests for appointment router

#### Findings Addressed
- Prep for P3-R2-001 (Extract Method), P6-R1-002 (Reduce coupling)

#### Testable Behaviors
- `GET /api/appointments` with date range returns filtered appointments (characterization)
- `PATCH /api/appointments/{id}` with status field triggers state machine validation (characterization)
- `create_appointment()` helper: current inputs -> current outputs (characterization)

#### Success Criteria
- New characterization tests pass against current code
- No production code changes in this phase

#### Dependencies
- None (first phase)

---

### Phase 2: Extract date filtering logic

#### Findings Addressed
- P3-R2-001: Extract `_filter_by_date_range` from appointment list handler
- P2-R1-005: Rename `d` to `filter_date` in extracted function

#### Testable Behaviors
- `_filter_by_date_range(start, end)`: same outputs as inline code (covered by Phase 1 characterization tests)
- Existing endpoint tests remain green

#### Success Criteria
- All existing tests pass (zero failures)
- `_filter_by_date_range` exists as a standalone function
- Appointment list handler calls `_filter_by_date_range` instead of inline logic

#### Dependencies
- Phase 1 complete: characterization tests in place

#### Rollback Trigger
- Any test red -> `git checkout` to last green commit
```

## Integration with building-against-plan

When `building-against-plan` executes a refactoring plan:
- The qa-test-engineer writes characterization tests (not new-behavior tests)
- The feature-implementer applies named refactoring operations one at a time
- The test-runner verifies green after every operation
- The debugger reverts (not fixes) if tests go red — refactoring that breaks tests is wrong by definition
