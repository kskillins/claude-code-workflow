# Phase 2: Naming — Comprehension & Intent Clarity

## Scope Reminder (from SKILL.md Step 0.5)
Apply exclusion rules: Never suggest UI layout changes, feature removal, aesthetic
changes, API contract changes, or business logic changes. Findings must be limited
to code structure and functionality.

## Purpose
Identify variables, functions, classes, and parameters whose names obscure intent, mislead readers, or fail to communicate what they represent.

## What to Detect

### Vague/Generic Names
- Single-letter variables outside of trivial loops (`i`, `j` are ok in `for i in range`)
- Names like `data`, `result`, `tmp`, `temp`, `val`, `obj`, `item`, `thing`, `stuff`
- Handler names like `handle_it`, `do_stuff`, `process`
- Boolean variables that don't read as predicates (`flag`, `check`, `status` vs `is_active`, `has_permission`)

### Misleading Names
- Variable name suggests one type but holds another (e.g., `user_list` that's actually a dict)
- Function name suggests it returns something but has side effects (or vice versa)
- Names that imply a broader scope than the actual implementation
- Abbreviated names where the abbreviation is ambiguous (`proc` — process? procedure? processor?)

### Inconsistent Naming
- Same concept named differently across files (e.g., `customer_id` vs `cust_id` vs `customerId`)
- Mixed naming conventions within the same module (camelCase + snake_case in Python)
- Plural/singular inconsistency for collections

### Missing Type Annotations (Python only)
- Function parameters without type hints
- Return types not annotated
- Important variables without type annotations
- Note: Don't flag every missing annotation — focus on public functions and unclear types

### Poor Module/File Names
- Files that don't describe their contents
- Modules named after implementation rather than purpose

## Detection Strategy

### Python (api/ directory)
1. Read each Python file in `api/` and `api/routers/`
2. Examine function signatures for vague parameter names
3. Check variable names in function bodies for single-letter or generic names
4. Look for type annotation gaps on public functions
5. Compare naming patterns across router files for consistency

### TypeScript (frontend/src/ directory)
1. Read component files, hooks, and service files
2. Check prop names and state variable names
3. Look for generic callback names (`handleClick` on non-click events, etc.)
4. Check for consistent naming across similar components

## Severity Guidelines
- **Major**: Misleading name that could cause bugs (name implies wrong behavior)
- **Minor**: Vague or generic name that hurts readability but isn't misleading
- **Minor**: Missing type annotation on a public function
- **Critical**: Never used for naming issues alone

## False Positive Guards
- Don't flag idiomatic Python names (`self`, `cls`, `_`, `args`, `kwargs`)
- Don't flag well-known abbreviations (`db`, `url`, `id`, `api`, `auth`, `req`, `res`)
- Don't flag names from external libraries (e.g., Pydantic's `model_dump`)
- Don't flag short lambda parameter names
- Don't flag React's conventional names (`e` for events, `ref` for refs, `props`)
- Respect project conventions from CLAUDE.md (e.g., `get_db()` is an established pattern)
