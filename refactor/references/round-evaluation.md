# Round Evaluation — Threshold Triggers for Round 3

After Round 2 completes, evaluate these thresholds to determine if Round 3 is needed. Round 3 is targeted — only the triggered phases re-run.

## Threshold Table

| Threshold | Condition | Phases to Re-Run |
|-----------|-----------|------------------|
| File length | Any source file > 500 lines | Phase 3 only |
| Complexity | 3+ files with cyclomatic complexity > 15 | Phase 3 only |
| Clones | 5+ clone groups detected | Phase 4 only |
| Circular deps | Any circular dependency found in Phase 6 | Phase 6 only |
| Issue volume | Round 2 found 20+ total NEW issues | All 7 phases |

## Evaluation Process

1. Read all Round 2 output files
2. Count NEW findings per phase
3. Check complexity JSON for CC > 15 counts
4. Check clone JSON for group count
5. Check Phase 6 output for circular dependency findings

## Multiple Triggers

If multiple thresholds are met, run the union of all triggered phases. For example, if both "File length" and "Clones" trigger, run Phases 3 and 4.

## Round 4 Policy

Round 4 is **never automatic**. If Round 3 still shows high issue counts, the report should note: "Further refactoring analysis recommended — consider running `/refactor` again after applying top findings."

## Reporting

After threshold evaluation, report to the orchestrator:
```
ROUND 3 EVALUATION:
- File length (>500): {met/not met} ({n} files)
- Complexity (>15 CC): {met/not met} ({n} files)
- Clone groups (>5): {met/not met} ({n} groups)
- Circular deps: {met/not met}
- Issue volume (>20 new): {met/not met} ({n} new issues)
DECISION: {Run Round 3 phases [X, Y] | Skip Round 3}
```
