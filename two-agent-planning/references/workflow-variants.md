# Workflow Variants

## Simple task (< 5 files, clear requirements)
- Shorten Phase 1 to 2-3 targeted questions
- Planner produces concise plan (phases not needed if work is linear)
- Minimum 2 review cycles still required
- Phase 5 user presentation still required

## Complex task (> 5 files, architectural decisions, multiple stakeholders)
- Thorough Phase 1 with multiple rounds of clarification
- Planner includes architecture diagrams (ASCII) and decision records
- Minimum 3 review cycles required
- Consider breaking into sub-plans if scope exceeds a single planning session

## Exploratory task (unclear scope, research needed)
- Phase 1 focuses on defining what is known vs unknown
- First plan may be a "discovery plan" -- steps to gather information
- After discovery, create the real implementation plan
- Minimum 2 review cycles still required for the final implementation plan

## Refactoring task (driven by /refactor findings)
- Phase 1 is shortened — scope is already defined by findings
- Planner reads `.claude/refactor/*_round_*_phase_*.md` files as primary input
- See [refactoring-workflow.md](refactoring-workflow.md) for full methodology
- Two Hats Rule enforced: each phase is purely structural (refactoring) or purely behavioral (characterization tests), never both
- Characterization test phases precede refactoring phases for uncovered code
- Minimum 2 review cycles still required
- Reviewer must verify that no phase mixes refactoring with new behavior

## Feature task with Boy Scout findings (from /build)

When `/build` provides Boy Scout findings alongside a feature request:

- Phase 1 Clarification is shortened — scope is already assessed by /build
- Planner receives Boy Scout findings as additional context
- Planner MUST evaluate each finding and document disposition:
  - **Non-trivial** (structural changes, extractions): create a Phase 0 preparatory
    refactoring phase following the refactoring workflow pattern (characterization tests
    if coverage is insufficient, then structural changes)
  - **Trivial** (unused imports, single renames): fold into the TDD refactor step
    (Step 3 in building-against-plan) of the nearest relevant feature phase
  - **Out of scope**: defer explicitly with rationale
- Reviewer must verify Boy Scout findings were addressed or explicitly deferred
- Minimum 2 review cycles still required

## Choosing a variant

The main agent selects the variant during Phase 1 based on:
- File count estimate (< 5 = simple, > 5 = complex)
- Whether requirements are clear (unclear = exploratory)
- Whether architectural decisions are involved (yes = complex)
- Whether `/refactor` findings exist in `.claude/refactor/` (yes = refactoring)
- Whether `/build` provided Boy Scout findings (yes = feature with Boy Scout variant)

Communicate the chosen variant in the planner agent's launch prompt.
