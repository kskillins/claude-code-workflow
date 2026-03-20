---
name: build
description: >
  Single entry-point for all development work. Assesses task scope (small/medium/large),
  performs a Boy Scout scan of files to be touched, identifies preparatory refactoring
  opportunities, and routes to the correct downstream skill (/small-feature or
  /two-agent-planning). Use when the user describes a feature, bug fix, or code change
  to implement.
---

# /build — Unified Development Workflow

Single entry-point that assesses scope, performs preparatory refactoring analysis, and routes to the correct downstream skill. Refactoring is woven into every feature build automatically.

## Workflow

### Step 1: Understand the task

- Restate the user's goal
- Ask clarifying questions if ambiguous (batch, don't overwhelm)
- Determine: what files change, backend/frontend/both, which roles affected

### Step 2: Scope assessment

| Signal | Small | Medium | Large |
|--------|-------|--------|-------|
| Files touched | 1-3 | 4-8 | 8+ |
| New tables/models | 0 | 0-1 | 2+ |
| Architectural decisions | None | Minor | Major |
| User flows affected | 1 | 1-2 | 3+ |
| New API endpoints | 0-1 | 2-4 | 5+ |
| Phase count | 1 (linear) | 2-3 | 4+ |

If 2+ signals point higher, route up. When borderline, state reasoning and ask user preference.

### Step 3: Preparatory refactoring assessment

"Make the change easy, then make the easy change." — Kent Beck

The depth of this assessment scales with scope. No artificial time limits — quality matters more than speed.

| Scope | Scan depth |
|-------|------------|
| Small | Modified files only |
| Medium | Modified files + immediate callers/callees (one hop) |
| Large | Modified files + related modules + codebase-wide pattern search |

#### 3A: Boy Scout scan (all scopes)

Read the files the task will modify. Look for:
- Unused imports
- Misleading names in code being modified
- Obvious duplication in the functions being modified
- TODO/FIXME comments in the modified code

#### 3B: Structural readiness (all scopes)

For each function/module you're about to modify, check these patterns:

1. **Long function** — Is the function you need to modify >50 lines or handling multiple
   concerns (validation + DB query + response formatting)? If so, Extract Method to
   isolate the section you'll change. Modifying a 60-line function is risky; modifying
   a 15-line extracted function is safe.

2. **Deep nesting** — Does the code path you need to modify have 3+ nesting levels?
   Flatten with guard clauses / early returns first. Deep nesting obscures logic and
   makes new branches error-prone.

3. **Growing parameter list** — Will your feature add parameters to a function that
   already has 3+? Introduce a Parameter Object (Pydantic model or dataclass) first.
   Long parameter lists are hard to understand and easy to reorder incorrectly.

4. **Unclear naming** — Would adding your feature create confusing variants
   (`process_data` + `process_data_v2`)? Rename the original to reflect its specific
   purpose first, then give the new feature its own clear name.

#### 3C: Consolidation search (all scopes, depth varies)

For each new function, endpoint, or component the task will introduce:

1. Search the codebase for existing functions with similar names, signatures, or behavior
2. If **2+ similar implementations already exist** — this is a 3x consolidation
   opportunity. Extract a shared helper first, then build the new feature on top.
3. If **1 similar implementation exists** — note it so the new code stays aware and
   avoids divergence.

#### 3D: Architectural signals (medium and large scopes only)

1. **Data clumps** — Are the same 3+ fields (e.g., address/city/state/zip) passed
   together across multiple functions? If your feature adds another usage, extract a
   value object first.

2. **Divergent change** — Does `git log` show the module you're modifying changes for
   multiple unrelated reasons? If you're adding yet another reason, consider splitting
   the module first (Extract Class / Extract Module).

3. **Feature envy** — Will your new code heavily access another module's data? The logic
   should live where the data lives. Move it before building on top.

4. **Primitive obsession** — Are you about to validate the same domain concept (phone
   numbers, zip codes, status strings) in yet another place? Extract a value object or
   enum first.

If files can't be identified yet (vague task), skip and let the downstream skill handle it.

### Step 4: Route

| Scope | Route to | Boy Scout injection |
|-------|----------|---------------------|
| Small | `/small-feature` | Pass findings as "cleanup after green" list |
| Medium | `/two-agent-planning` (simple variant) | Include findings in planner prompt as preparatory refactoring context |
| Large | `/two-agent-planning` (complex variant) | Include findings in planner prompt as preparatory refactoring context |

When routing to `/two-agent-planning`, include in the planner context:
> "Preparatory refactoring findings from `/build` scan: [list — categorized as Boy Scout hygiene, structural readiness, consolidation, or architectural]. Non-trivial findings should become a Phase 0 preparatory refactoring phase (characterization tests + structural changes per refactoring-workflow.md). Trivial findings (unused imports, single renames) should be folded into the TDD refactor step of the nearest feature phase. Document disposition of each finding in a Boy Scout Disposition section."

When routing to `/small-feature`, include:
> "Preparatory refactoring findings: [list]. Structural readiness items (Extract Method, Parameter Object, renames) and consolidation opportunities should be applied BEFORE Step 3 (Red), as separate commits. Boy Scout hygiene items should be applied in Step 5 after Green."

**Preparatory refactoring triggers escalation**: If any finding would touch 4+ files (e.g., consolidation across multiple modules, splitting a God module), escalate from Small to Medium (route to `/two-agent-planning` instead of `/small-feature`). Cross-cutting structural work benefits from a plan.

## Related skills (not part of /build flow)
- `/refactor` — standalone codebase analysis (produces findings, does not apply changes)
- `/testing-suite-refactor` — standalone test suite audit
