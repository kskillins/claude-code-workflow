# Phase 1: Hygiene — Zero-Risk Noise Removal

## Scope Reminder (from SKILL.md Step 0.5)
Apply exclusion rules: Never suggest UI layout changes, feature removal, aesthetic
changes, API contract changes, or business logic changes. Findings must be limited
to code structure and functionality.

## Purpose
Identify dead code, unused imports, and other noise that obscures the real codebase. These are safe to remove with zero behavioral impact.

## What to Detect

### Dead Code
- Functions/methods never called from anywhere in the codebase
- Variables assigned but never read
- Unreachable code after `return`, `raise`, `break`, `continue`
- Unused class definitions
- Dead branches in conditionals (e.g., `if False:`, constants that make a branch unreachable)

### Unused Imports
- Python: `import X` or `from X import Y` where Y is never used in the file
- TypeScript: `import { X }` where X is never referenced
- Re-exports that are never consumed downstream

### Commented-Out Code
- Blocks of commented-out code (not documentation comments)
- `# old implementation`, `// TODO: remove`, etc.
- Distinguish from legitimate documentation comments

### TODO/FIXME/HACK Markers
- `TODO`, `FIXME`, `HACK`, `XXX`, `TEMP`, `WORKAROUND` comments
- Classify by age if possible (check git blame)
- These aren't necessarily "fix now" — just catalog them

### Unused Configuration
- Unused environment variable reads
- Dead feature flags
- Unused route registrations

## Detection Strategy

### Python (api/ directory)
1. Use Grep to find all `import` statements
2. For each import, Grep for usage of that name in the same file
3. Use Grep to find all `def` and `class` definitions
4. For each, Grep for usage across the entire `api/` directory
5. Look for `# ` followed by code-like patterns (commented-out code)
6. Grep for TODO/FIXME/HACK/XXX

### TypeScript (frontend/src/ directory)
1. Use Grep to find all `import` statements
2. For each import, check usage in the same file
3. Look for unused exported functions/components
4. Check for commented-out JSX or code blocks
5. Grep for TODO/FIXME markers

## Severity Guidelines
- **Major**: Dead functions/classes (clutters codebase significantly)
- **Minor**: Unused imports, single-line commented code, TODO markers
- **Critical**: Never used for hygiene issues (they don't cause bugs)

## False Positive Guards
- Don't flag imports used only in type annotations (Python `TYPE_CHECKING`)
- Don't flag `__init__.py` re-exports without checking downstream usage
- Don't flag test fixtures or conftest definitions as "unused"
- Don't flag FastAPI dependency injection functions that appear unused but are referenced in `Depends()`
- Don't flag React components that are only used in route definitions
