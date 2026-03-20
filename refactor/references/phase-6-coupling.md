# Phase 6: Coupling — Module Boundaries & Dependencies

## Scope Reminder (from SKILL.md Step 0.5)
Apply exclusion rules: Never suggest UI layout changes, feature removal, aesthetic
changes, API contract changes, or business logic changes. Findings must be limited
to code structure and functionality.

## Purpose
Identify tight coupling, circular dependencies, god modules, and leaking abstractions that make the codebase rigid and hard to change.

## What to Detect

### Circular Dependencies
- Module A imports from Module B, and Module B imports from Module A
- Transitive cycles: A -> B -> C -> A
- In Python: circular imports that work due to late binding but are still architectural smells

### God Modules
- Files that are imported by > 50% of other files
- Files with > 20 exported functions/classes
- Files that mix unrelated responsibilities (e.g., auth + validation + formatting)

### Cross-Feature Imports
- Frontend features importing from other feature directories (e.g., `features/dashboard/` importing from `features/work-order-flow/`)
- Backend routers importing from other routers (instead of shared services)
- Direct database access from unexpected modules

### Leaking Abstractions
- Implementation details exposed in public interfaces
- Database column names appearing in frontend code
- Supabase-specific patterns leaking into business logic

### Inappropriate Intimacy
- One module reaching into another's internals (accessing private-by-convention attributes)
- Components that know too much about their parent's state
- Tightly coupled function signatures that pass through many parameters

### Missing Boundaries
- Business logic embedded in route handlers instead of service functions
- Data transformation happening at the wrong layer
- Validation split across multiple layers without clear ownership

## Detection Strategy

1. Map all import statements across the codebase
2. Build a dependency graph (which files import which)
3. Check for cycles in the graph
4. Identify files with high fan-in (many importers) and high fan-out (many imports)
5. Check frontend `features/` directories for cross-feature imports
6. Look for database/Supabase patterns in unexpected locations

## Recommended Refactorings
- **Extract Service**: Move business logic from handlers to service modules
- **Introduce Interface**: Define clear boundaries between modules
- **Move Method**: Relocate functions to the module where they belong
- **Dependency Inversion**: Depend on abstractions, not concretions

## Severity Guidelines
- **Critical**: Circular dependencies that could cause import errors
- **Major**: God modules, cross-feature coupling, missing service layer
- **Minor**: Mild inappropriate intimacy, slightly leaky abstractions
- **Minor**: Missing boundaries that don't currently cause problems

## False Positive Guards
- Don't flag `api/index.py` importing all routers (that's its job)
- Don't flag shared utilities being imported widely (that's their purpose)
- Don't flag `AuthContext` being used everywhere (cross-cutting concern)
- Don't flag `apiFetch` being imported everywhere (it's the API client)
- Don't flag `conftest.py` imports in tests (test infrastructure)
- The project intentionally uses supabase-py directly (no ORM) — this is not a leaky abstraction
