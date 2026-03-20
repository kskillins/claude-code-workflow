# Phase 3: Structure — Complexity Reduction

## Scope Reminder (from SKILL.md Step 0.5)
Apply exclusion rules: Never suggest UI layout changes, feature removal, aesthetic
changes, API contract changes, or business logic changes. Findings must be limited
to code structure and functionality.

## Purpose
Identify overly complex functions, deep nesting, and structural issues that make code hard to understand, test, and maintain.

## What to Detect

### Long Functions
- Python functions > 50 lines (excluding docstrings/comments)
- TypeScript functions/components > 60 lines of logic (excluding JSX template)
- React components with > 80 total lines

### Deep Nesting
- More than 3 levels of indentation (if/for/try nesting)
- Callback pyramids in TypeScript
- Nested ternaries beyond 1 level

### High Cyclomatic Complexity
- Functions with cyclomatic complexity > 10
- Use data from `{DATE}_complexity.json` when available
- Multiple return paths that are hard to trace

### Complex Boolean Expressions
- Compound conditions with 3+ clauses (`if a and b or c and not d`)
- Negated complex conditions (`if not (a or b)`)
- Boolean logic that requires a truth table to understand

### God Functions
- Functions that do multiple unrelated things (violate Single Responsibility)
- Functions that mix I/O with business logic
- Route handlers that contain business logic instead of delegating

### Deep Call Chains
- Functions that call 5+ other functions sequentially (orchestration bloat)
- Long method chains that are hard to debug

## Detection Strategy

1. Read `{DATE}_complexity.json` for automated metrics
2. For files flagged by the script, read them and analyze structure
3. For files not covered by the script, manually assess:
   - Count function lines
   - Count nesting depth
   - Identify mixed responsibilities

## Recommended Refactorings
- **Extract Method**: Pull a coherent block into its own function
- **Replace Nested Conditional with Guard Clauses**: Early returns reduce nesting
- **Decompose Conditional**: Extract complex boolean into named variables/functions
- **Split Phase**: Separate data gathering from data processing

## Severity Guidelines
- **Critical**: Cyclomatic complexity > 20 (near-untestable)
- **Major**: Functions > 50 lines, nesting > 3 deep, CC > 10
- **Minor**: Functions 30-50 lines, nesting at 3, CC 7-10

## False Positive Guards
- Don't flag long functions that are simple sequential operations (e.g., building a PDF with reportlab)
- Don't flag switch/match statements with many cases as "high complexity" if each case is trivial
- Don't flag test functions for length (test setup can be verbose)
- Don't flag route handler length if it's mostly Pydantic model definitions at the top
- Consider the project's router pattern — some handlers are necessarily sequential (query → validate → transform → respond)
