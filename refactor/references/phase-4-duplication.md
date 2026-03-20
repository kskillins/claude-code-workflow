# Phase 4: Duplication — DRY Violations

## Scope Reminder (from SKILL.md Step 0.5)
Apply exclusion rules: Never suggest UI layout changes, feature removal, aesthetic
changes, API contract changes, or business logic changes. Findings must be limited
to code structure and functionality.

## Purpose
Identify duplicated code patterns that violate the DRY principle. Respects the project's 3x rule: don't extract until you see the same pattern 3+ times.

## What to Detect

### Exact Clones
- Identical code blocks appearing in multiple locations
- Copy-pasted functions with no modifications
- Use data from `{DATE}_clones.json` when available

### Near-Duplicates
- Code blocks that are 80%+ similar with minor variations (different variable names, slightly different logic)
- Functions that do the same thing but with different parameter names
- Error handling patterns repeated with slight variations

### 3x Rule Violations
- Patterns that appear 3 or more times and should be extracted
- Common query patterns repeated across routers
- Similar validation logic in multiple handlers
- Repeated data transformation patterns

### Structural Duplication
- Multiple router files following the same boilerplate pattern that could be generalized
- Similar React components that differ only in data source
- Test files with heavily repeated setup/teardown

### Cross-Layer Duplication
- Same validation logic in both frontend and backend (expected for some cases, but worth cataloging)
- Constants defined in multiple places instead of shared

## Detection Strategy

1. Read `{DATE}_clones.json` for hash-based clone detection results
2. For each clone group, read the actual code to assess whether it's a true duplicate or incidental similarity
3. Manually scan router files for repeated query/validation patterns
4. Compare React components for structural similarity
5. Look for repeated error handling blocks

## Recommended Refactorings
- **Extract Method**: Pull duplicated block into a shared function
- **Extract Module**: Create a utility module for cross-file duplicates
- **Template Method**: When the structure is the same but details differ
- **Parameterize**: When duplicates differ only in a value, make it a parameter

## Severity Guidelines
- **Major**: 3+ exact or near-duplicate blocks (clear 3x rule violation)
- **Minor**: 2 duplicates (not yet at 3x threshold, but worth noting)
- **Minor**: Structural duplication in boilerplate (may be intentional)
- **Critical**: Never — duplication doesn't cause bugs directly

## False Positive Guards
- Don't flag test code duplication as strongly (test readability > DRY)
- Don't flag router CRUD boilerplate if each handler has unique business logic
- Don't flag Pydantic model definitions that look similar but represent different entities
- Don't flag import blocks that happen to import the same things
- Respect the 3x rule — 2 occurrences is a note, not a finding
- Don't flag intentional denormalization (e.g., frontend and backend both validating email format)
