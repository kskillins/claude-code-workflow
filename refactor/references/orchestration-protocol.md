# Orchestration Protocol

## Phase Execution Order

Phases MUST run sequentially within each round because they compound:

1. **Hygiene** removes noise → cleaner signal for all subsequent phases
2. **Naming** clarifies intent → Structure phase understands function purposes
3. **Structure** breaks up complexity → Duplication phase can see clones inside large functions
4. **Duplication** identifies repetition → Consistency phase knows which patterns exist
5. **Consistency** standardizes patterns → Coupling phase sees true dependency shapes
6. **Coupling** maps boundaries → Hotspots phase understands architectural context
7. **Hotspots** prioritizes ROI → report ranks findings by business impact

## Round Sequencing

### Round 1: Wide Net
- Run all 7 phases
- No prior output — everything is `Status: New`
- Goal: catalog all detectable issues

### Round 2: Deep Scrutiny
- Run all 7 phases again
- Each phase agent receives its Round 1 output file
- Cross-reference with other phases' Round 1 findings
- Goal: validate Round 1 findings, catch what was missed, update severity assessments

### Round 3+: Targeted (conditional)
- Only run if thresholds are met (see `round-evaluation.md`)
- Run only the triggered phases
- Maximum: Round 3 only (Round 4 is never automatic)

## Agent Launch Template

For each phase, launch a `general-purpose` Task agent with this prompt structure:

```
You are a code analysis agent running Phase {N} ({Name}) of a refactoring analysis.

**Read these references first:**
- Phase instructions: {SKILLS_DIR}/refactor/references/phase-{N}-{name}.md
- Output format: {SKILLS_DIR}/refactor/references/output-format.md

**Parameters:**
- Round: {R}
- Project root: {PROJECT_ROOT}
- Prior round output: {path or "none"}
- Complexity data: {path to complexity JSON, for phases 3/7}
- Clone data: {path to clones JSON, for phase 4}
- Hotspot data: {path to hotspots JSON, for phase 7}

**Your task:**
1. Read the phase reference file for detection rules
2. Read the output format reference for formatting rules
3. Analyze the codebase at {PROJECT_ROOT} according to your phase's rules
4. Write findings to: {PROJECT_ROOT}/.claude/refactor/{DATE}_round_{R}_phase_{N}_{name}.md
5. Return ONLY the summary block (see output format reference)

**Scope:**
- Backend: api/ directory (Python)
- Frontend: frontend/src/ directory (TypeScript/React)
- Exclude: node_modules, venv, __pycache__, .git, build artifacts

**Rules:**
- Read-only analysis. Do NOT modify any source files.
- Be specific: include file paths with line numbers.
- Be actionable: name the exact refactoring operation to apply.
- Be conservative: only flag genuine issues, not style preferences.
```

## Parallelization Note

While phases within a round must be sequential, the helper scripts (Step 2) can run in parallel with each other. The test baseline (Step 1) must complete before anything else starts.

## Error Handling

- If a phase agent fails or returns no summary block, log the error and continue with the next phase. Note the missing phase in the final report.
- If a helper script fails, the dependent phases should still run but note that automated data was unavailable and rely on manual analysis.
- If the test baseline fails, STOP entirely — do not proceed with analysis.
