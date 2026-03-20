# Output Format Reference

## File Naming

Each phase produces one markdown file per round:
```
.claude/refactor/{DATE_PREFIX}_round_{N}_phase_{N}_{name}.md
```

Examples:
- `.claude/refactor/2026_03_18_round_1_phase_3_structure.md`
- `.claude/refactor/2026_03_18_round_2_phase_1_hygiene.md`

## File Structure

```markdown
# Phase {N}: {Phase Name} — Round {R}

## Findings

### [{PHASE_CODE}-R{ROUND}-{SEQ}]
- **File:** path/to/file.py:142
- **Severity:** Critical | Major | Minor
- **Status:** New | Confirmed | Resolved | Reverted
- **Description:** Clear, specific description of the issue
- **Recommendation:** Named refactoring operation (e.g., "Extract Method", "Rename Variable")
- **Code snippet:**
<details>
<summary>Show code</summary>

\```python
# 5-10 lines of relevant code
\```
</details>

---

## Summary

| Metric | Count |
|--------|-------|
| New | {n} |
| Confirmed | {n} |
| Resolved | {n} |
| Critical | {n} |
| Major | {n} |
| Minor | {n} |
```

## Finding ID Format

- `P{phase}-R{round}-{sequence}` — e.g., `P3-R1-001`
- Phase codes: P1=Hygiene, P2=Naming, P3=Structure, P4=Duplication, P5=Consistency, P6=Coupling, P7=Hotspots
- Sequence numbers are 3-digit zero-padded, starting at 001 per phase per round

## Severity Levels

- **Critical**: Actively causes bugs, data loss, or security issues. Must fix before shipping.
- **Major**: Significantly harms maintainability, readability, or testability. Should fix soon.
- **Minor**: Style issue, mild smell, or opportunity for improvement. Fix when convenient.

## Status Values

- **New**: First time this issue is detected (Round 1, or newly found in later rounds)
- **Confirmed**: Was found in a prior round and still present (Round 2+)
- **Resolved**: Was found in a prior round but is no longer present (rare during analysis-only)
- **Reverted**: Was applied but caused test failure and was reverted (only during application phase)

## Summary Block (for agent responses)

Each phase agent MUST end its response with this exact format so the orchestrator can parse it:

```
---
ROUND: {N}  PHASE: {N}
SAVED TO: .claude/refactor/{filename}
NEW: {n} | CONFIRMED: {n} | RESOLVED: {n}
CRITICAL: {n} | MAJOR: {n} | MINOR: {n}
---
```

## Cross-Reference Format

When a finding in one phase relates to a finding in another phase, reference it inline:
```
Related: [P1-R1-003] (dead code in same function)
```

## Round 2+ Instructions

In Round 2 and beyond, the agent receives the prior round's output file. For each prior finding:
1. Re-examine the code — is the issue still present? → Status: Confirmed
2. Was it more severe/less severe than initially assessed? → Update severity with a note
3. Were there related issues missed in Round 1? → Add as New findings

Additionally, cross-reference with other phases' Round 1 findings to spot patterns.
