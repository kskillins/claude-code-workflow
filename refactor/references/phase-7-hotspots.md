# Phase 7: Hotspots — ROI-Driven Prioritization

## Scope Reminder (from SKILL.md Step 0.5)
Apply exclusion rules: Never suggest UI layout changes, feature removal, aesthetic
changes, API contract changes, or business logic changes. Findings must be limited
to code structure and functionality.

## Purpose
Identify the intersection of frequently-changed files and high-complexity code. These hotspots represent the highest-ROI refactoring targets — the top 5% of code that receives 90% of changes.

## What to Detect

### Change-Frequency Hotspots
- Files changed most often in git history
- Use data from `{DATE}_hotspots.json` when available
- Weight recent changes more heavily than old ones

### Complexity x Frequency Intersection
- Files that are BOTH frequently changed AND highly complex
- Score: `change_count * max_complexity` — highest scores are the top hotspots
- These are the files where refactoring pays off most

### Temporal Coupling
- Files that always change together (if you change A, you must change B)
- This indicates hidden coupling even if there's no direct import relationship
- Detected by analyzing git commits for co-changing files

### Churn Patterns
- Files with high churn (many small changes) vs. stable files with occasional large changes
- High churn suggests the code is hard to get right — needs structural improvement
- Frequent revert/re-apply patterns

### Risk Concentration
- Critical business logic in high-churn files (risky)
- Authorization/security code that changes frequently (very risky)
- Data mutation code with high complexity scores

## Detection Strategy

1. Read `{DATE}_hotspots.json` for pre-computed git analysis
2. Read `{DATE}_complexity.json` for complexity metrics
3. Cross-reference: find files appearing in both lists with high scores
4. Analyze temporal coupling by looking at commit co-occurrence
5. Cross-reference with findings from Phases 1-6 — hotspot files with many findings are top priority

## Output Additions

In addition to the standard finding format, this phase produces a **Priority Matrix** at the top of the output file:

```markdown
## Priority Matrix

| Rank | File | Changes | Max CC | Score | Phase Findings |
|------|------|---------|--------|-------|----------------|
| 1 | api/routers/work_orders.py | 23 | 15 | 345 | P3-R1-001, P4-R1-003 |
| 2 | frontend/src/hooks/useDashboardData.ts | 18 | 8 | 144 | P2-R1-005 |
| ... | | | | | |
```

## Recommended Actions
- **Top 3 hotspots**: Prioritize these for immediate refactoring
- **Temporal coupling pairs**: Consider merging or extracting shared logic
- **High-churn files**: Add characterization tests before refactoring

## Severity Guidelines
- **Critical**: Security/auth code in hotspot with CC > 15
- **Major**: Top 5 hotspots with complexity issues
- **Minor**: Moderate hotspots, temporal coupling clusters

## False Positive Guards
- Don't flag files that changed frequently due to one-time migrations
- Don't flag config files or auto-generated files
- Don't flag test files as hotspots (they change with the code they test)
- Don't flag CLAUDE.md or documentation as hotspots
- Consider that some files are *supposed* to change often (routers adding new endpoints)
