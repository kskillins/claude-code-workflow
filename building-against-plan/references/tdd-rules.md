# TDD Enforcement Rules

## Contents
- Test immutability protocol
- Red-Green-Refactor enforcement
- Test writing standards
- Failure resolution flowchart
- Real connection testing guidelines
- Edge case test requirements

## Test immutability protocol

Once a test is written and confirmed to fail for the right reason (Red phase), it becomes immutable. The test defines the contract. The production code must conform to the contract.

**Permitted test modifications:**
- Fixing a syntax error in the test itself (typo, missing import) -- only before the test has been confirmed as a valid Red test
- Adding new test cases alongside existing ones
- Improving test setup (fixtures, helpers) that do not change assertions

**Prohibited test modifications:**
- Changing assertion values to match buggy output
- Weakening assertions (e.g., changing `assertEqual` to `assertIn`, loosening regex)
- Adding conditional logic to tests that allows multiple outcomes
- Commenting out or skipping failing tests
- Deleting tests that fail
- Wrapping assertions in try/except blocks

**If a test seems wrong after implementation:**
1. Re-read the plan's requirements for this behavior
2. If the test genuinely misinterprets the requirements, ask the user to confirm
3. Only with explicit user approval, rewrite the test to match corrected requirements
4. The rewritten test must still fail against the current implementation (Red), then implementation is updated (Green)

## Red-Green-Refactor enforcement

### Red phase rules

1. Write the test before any production code for the feature exists
2. Run the test and confirm it fails
3. The failure reason must be meaningful:
   - `ModuleNotFoundError` or `ImportError` -- acceptable (module doesn't exist yet)
   - `AttributeError` -- acceptable (method doesn't exist yet)
   - `AssertionError` with wrong value -- acceptable (logic not implemented)
   - `SyntaxError` in the test -- NOT acceptable (fix the test, this is not a valid Red)
   - Test passes -- NOT acceptable (either the feature already exists or the test is wrong)
4. If the test passes immediately, either:
   - The feature already exists (skip to edge case tests)
   - The test is not testing the right thing (rewrite the test)

### Green phase rules

1. Write the absolute minimum code to make the failing test pass
2. Do not write code for untested behavior
3. Do not optimize, do not refactor, do not clean up -- just make it green
4. Run the FULL test suite, not just the new test
5. If existing tests break:
   - Do NOT edit existing tests
   - The new code has a regression -- fix the production code to satisfy both old and new tests
6. Repeat until all tests pass

### Refactor phase rules

**The Two Hats Rule:** During refactor, you wear the refactoring hat ONLY. No new behavior, no new tests for new features, no bug fixes. Only structural improvements. Each commit during refactor must be purely structural — never mix structural and behavioral changes in one commit.

1. Only refactor while all tests are green
2. **Micro-steps**: Each change must be a single, named transformation from Fowler's catalog (Extract Method, Rename Variable, Inline Function, Move to Module, Introduce Parameter Object, Replace Conditional with Polymorphism). If you can't name it, you're probably rewriting, not refactoring
3. Run the full test suite after EACH micro-step (not after a batch of changes)
4. If any test fails:
   - Immediately undo the last refactoring change (you should be exactly one step from green)
   - Try a different refactoring approach
   - If multiple approaches fail, leave the code as-is (working beats elegant)
5. Refactoring targets (in priority order):
   - Duplicate code that has appeared 3+ times (the 3x rule — never abstract earlier)
   - Unclear variable or function names (comprehension refactoring — encode understanding into the code)
   - Functions longer than ~30 lines (Extract Method)
   - Deeply nested conditionals, 3+ levels (early returns or Replace Conditional with Polymorphism)
   - Functions with 5+ parameters (Introduce Parameter Object)
6. Do NOT refactor:
   - Code that works and is readable (no gold-plating)
   - Code that "could be better" but isn't causing problems
   - Code in other parts of the codebase not related to the current phase
   - Stable, rarely-changed code (prioritize hotspots — high change frequency + low quality)
7. **One-hour rule** (Kent Beck): If refactoring has consumed more than one hour without making the actual behavior change, stop and reassess. You've likely lost track of the minimum structural changes needed
8. **AI output discipline**: After AI-generated refactoring, verify the result is not more verbose or complex than the original. AI produces ~2x more code on average — simplify before committing. If the refactored version is longer, question whether it actually improved anything
9. You may refactor test code during this step (improve fixtures, reduce setup duplication), but never simultaneously with production code. Refactor either tests OR production code between commits — each acts as a check on the other
10. **Commit after each successful refactoring step**. Keep refactoring commits separate from behavior-change commits

### Safety net requirements for refactoring

Before refactoring ANY code (during the Refactor phase or standalone refactoring work):

1. **Test coverage must exist** over the code being refactored. If it doesn't, write characterization tests first — tests that capture current behavior (including bugs) as a baseline
2. **Version control with frequent commits**: Every micro-step should be committable and reversible
3. **Fast test execution**: If the test suite takes too long, identify a fast subset covering the refactored code
4. **Clear behavior boundary**: Know exactly what observable behavior must not change

**Characterization tests** (for code without sufficient coverage):
- Assert current behavior, even if that behavior seems wrong
- These document actual behavior, not desired behavior
- Once passing, you can safely refactor
- After refactoring, decide separately whether any "wrong" behavior should change (that's a behavior change — different hat, different commit)

## Test writing standards

### Naming convention

```
test_<unit>_<scenario>_<expected_result>
```

Examples:
- `test_calculate_total_with_empty_cart_returns_zero`
- `test_login_with_expired_token_raises_auth_error`
- `test_parse_csv_with_missing_headers_uses_defaults`

### Structure

Every test follows Arrange-Act-Assert:

```
# Arrange: Set up the test conditions
# Act: Execute the code under test
# Assert: Verify the expected outcome
```

Keep each section short. If Arrange requires more than 10 lines, extract a fixture or helper.

### One behavior per test

Each test verifies one specific behavior. Multiple assertions are acceptable only when they verify different aspects of the same behavior.

Good:
```
test_create_user_returns_user_object  # verifies return type and fields
```

Bad:
```
test_create_user  # verifies creation, validation, persistence, and notification
```

### Test independence

Every test must pass when run in isolation. No shared mutable state between tests. Use setup/teardown (fixtures) to create fresh state for each test.

## Failure resolution flowchart

When a test fails during the Green or Refactor phase:

```
Test fails
  |
  v
Is the failure in a NEW test (current phase)?
  |-- Yes --> Is it a syntax/import error in the test?
  |             |-- Yes --> Fix the test syntax, re-run (this is not a test logic change)
  |             |-- No --> Refactor PRODUCTION code to make it pass
  |
  |-- No --> Is the failure in an EXISTING test (prior phase)?
              |-- Yes --> The new code introduced a regression
              |           |
              |           v
              |           Refactor PRODUCTION code to satisfy BOTH old and new tests
              |           Do NOT touch the existing test
              |
              |-- No --> (should not happen -- investigate)
```

When production code changes cannot satisfy both old and new tests:
1. Check if the old test's requirements conflict with the new phase's requirements
2. If conflict exists, STOP and report to the user
3. The plan may have a design error that needs resolution before continuing

## Real connection testing guidelines

### When to use real connections

- Database is available (local, dev, or test instance) --> use it
- API endpoint is reachable and has a test/sandbox mode --> use it
- File system operations --> always use real files (in a temp directory)
- LLM/AI API calls --> use real calls with small inputs to verify integration

### When to mock

- External service is unavailable or has no test mode
- Operation is destructive and irreversible (production database writes, sending real emails)
- Operation is non-deterministic in a way that makes assertions impossible (random API, timing-dependent)
- Operation costs significant money per call with no test tier

### Real connection test setup

1. Use environment variables or config files for connection strings
2. Create test-specific schemas, databases, or namespaces
3. Clean up test data in teardown (fixtures)
4. Handle connection failures gracefully in test setup (skip with reason, not silent failure)

## Edge case test requirements

For every function or method, write tests for these categories:

**Boundary values:**
- Zero, one, maximum expected value
- Empty collections (empty list, empty string, empty dict)
- Null/None/undefined inputs (where the type system allows)

**Error conditions:**
- Invalid input types
- Out-of-range values
- Missing required fields
- Malformed data (bad JSON, invalid dates, broken URLs)

**State transitions:**
- First call vs subsequent calls
- Empty state vs populated state
- Concurrent access (if the function is shared across threads/requests)

**Integration boundaries:**
- Network timeout or connection refused
- Database constraint violations
- File permission errors
- API rate limits or auth failures

Not every function needs every category. Apply judgment: a pure math function needs boundary tests but not network timeout tests. A database query function needs connection failure tests but not concurrency tests (unless it's explicitly concurrent).
