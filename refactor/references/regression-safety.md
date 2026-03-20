# Regression Safety Protocol

## During Analysis (Phases 1-7)

The refactoring analysis is **strictly read-only**. No source files are modified during rounds.

1. **Baseline requirement**: Full test suite must be green before analysis starts
2. **No code changes**: Phase agents only read files and write findings to `.claude/refactor/`
3. **No dependency changes**: No package installs, no config modifications

## When Applying Findings (Post-Analysis)

After the analysis is complete and the user chooses to apply findings via `/two-agent-planning` + `/building-against-plan`:

### Per-Finding Application Protocol

1. **Single micro-step**: Apply one named refactoring transformation at a time
2. **Run full test suite immediately** after each transformation (use whatever test commands are documented in the project's CLAUDE.md or README)
3. **Green** → commit as `refactor: [phase] - [finding ID] - [brief description]`
4. **Red** → revert immediately: `git checkout -- .`
   - Mark finding as "Reverted — non-trivial, needs deeper analysis"
   - Do NOT attempt to fix the failing test
   - Move to next finding

### Commit Message Format

```
refactor: P3 - P3-R1-001 - extract inventory deduction from confirm_work_order

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
```

### Final Verification

After all applied refactorings:
1. Run full test suite (backend + frontend + type check)
2. Run frontend build
3. Verify no regressions
4. Create summary of applied vs. skipped vs. reverted findings

## Two Hats Rule Compliance

- **Analysis rounds**: Wearing the "analysis hat" — detection only, no changes
- **Application phase**: Wearing the "refactoring hat" — structural changes only, no new behavior
- These are separate workflows, separated by user decision
- Never mix feature work with refactoring in the same commit
