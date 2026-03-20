# Phase 5: Consistency — Cohesion & Pattern Uniformity

## Scope Reminder (from SKILL.md Step 0.5)
Apply exclusion rules: Never suggest UI layout changes, feature removal, aesthetic
changes, API contract changes, or business logic changes. Findings must be limited
to code structure and functionality.

## Purpose
Identify magic numbers, inconsistent error handling, and pattern drift across modules that should follow the same conventions.

## What to Detect

### Magic Numbers/Strings
- Hardcoded numeric values without named constants (e.g., `if len(items) > 50`)
- Hardcoded string literals used as keys or identifiers
- HTTP status codes used as raw numbers instead of constants
- Timeout values, retry counts, buffer sizes without named constants
- Exception: small obvious numbers (0, 1, -1) and HTTP status codes in route handlers are acceptable

### Inconsistent Error Handling
- Some functions raise exceptions while similar functions return error codes
- Inconsistent HTTP status codes for similar error conditions across routers
- Some handlers catch specific exceptions while others use bare `except`
- Missing error handling in some places where similar code handles errors

### Pattern Drift
- Router files that deviate from the established CRUD pattern without reason
- Components that handle state differently from similar components
- Inconsistent use of Pydantic models (some endpoints use them, similar ones don't)
- Different pagination approaches across similar list endpoints

### Inconsistent API Conventions
- Mixed response formats (some return `data`, some return raw objects)
- Inconsistent query parameter naming
- Some endpoints validate input, similar ones don't
- Status code inconsistency for similar operations

### Configuration Drift
- Environment variables accessed in different ways across the codebase
- Different approaches to database access patterns
- Inconsistent logging patterns

## Detection Strategy

1. Read all router files and compare their structure side-by-side
2. Catalog error handling patterns across all handlers
3. Search for hardcoded numbers/strings that should be constants
4. Compare React hook patterns across similar components
5. Check API response format consistency

## Recommended Refactorings
- **Extract Constant**: Replace magic numbers with named constants
- **Standardize Pattern**: Align drifted code with the established convention
- **Extract Base Handler**: When pattern drift is severe, create a shared pattern

## Severity Guidelines
- **Major**: Inconsistent error handling that could mask bugs
- **Major**: Pattern drift that makes the codebase harder to navigate
- **Minor**: Magic numbers in non-critical code
- **Minor**: Mild stylistic inconsistency
- **Critical**: Only if inconsistency creates a security or data integrity risk

## False Positive Guards
- Don't flag HTTP status codes in FastAPI route handlers (422, 404, 409 are idiomatic)
- Don't flag `0`, `1`, `-1` as magic numbers
- Don't flag string literals that are API endpoint paths
- Don't flag pagination defaults (offset=0, limit=50) as magic numbers
- Don't flag intentional deviation documented in CLAUDE.md
- Respect the project's established patterns (e.g., `get_db()` per handler is intentional)
