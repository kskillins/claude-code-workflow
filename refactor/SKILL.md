---
name: refactor
description: Multi-phase codebase refactoring analysis system. Runs 7 specialized detection phases across multiple rounds, produces structured findings and an interactive HTML report. Analysis-only — does NOT auto-apply changes.
trigger: When the user types /refactor or asks for a comprehensive refactoring analysis of the codebase.
---

# /refactor — Multi-Phase Codebase Refactoring Analysis

You are orchestrating a systematic, multi-pass refactoring analysis. You detect code smells, document them with full context, and produce an interactive HTML report. You do NOT apply any changes — that is done separately via `/two-agent-planning` + `/building-against-plan`.

## Prerequisites

Read these reference files before starting:
- `references/orchestration-protocol.md` (relative to this skill) — round/phase sequencing
- `references/output-format.md` (relative to this skill) — standardized finding format

## Orchestration Steps

### Step 0: Setup
1. Create `.claude/refactor/` directory in the project root if it doesn't exist
2. Set `DATE_PREFIX` = current date as `yyyy_mm_dd` (e.g., `2026_03_18`)
3. Identify the project root and tech stack

### Step 0.5: Scope and Exclusion Rules

**Scope (REQUIRED):** Ask the user what to analyze if not specified. Acceptable scopes:
- `backend` — analyze `api/` only
- `frontend` — analyze `frontend/src/` only
- `full` — analyze both
- `path:<dir>` — analyze a specific directory (e.g., `path:api/routers/`)
- `file:<path>` — analyze a specific file

If no scope is provided, ask: "What area should I analyze? (backend, frontend, full,
or a specific path)"

**Exclusion rules (MANDATORY — apply to ALL phases):**

Findings MUST be limited to code structure and functionality. The following are
OUT OF SCOPE and must NEVER appear in findings:

1. **UI layout or design** — never suggest moving, removing, resizing, or reorganizing
   UI elements. Component extraction (Extract Component) is in scope; visual layout is not.
2. **Feature removal** — never suggest removing user-facing functionality. Suggest
   restructuring the code, not removing the feature.
3. **Aesthetic/style** — never suggest changes to colors, spacing, typography, or
   visual design.
4. **API contract changes** — never suggest changing request/response shapes that would
   break existing consumers. Internal restructuring only.
5. **Business logic changes** — never suggest changing what the code does, only how it
   is structured internally.

### Step 1: Baseline Test Suite
Run the full test suite to establish a green baseline. Use whatever test commands are documented in the project's CLAUDE.md or README.

**If ANY test fails → STOP.** Tell the user: "Cannot run refactoring analysis against a red baseline. Fix failing tests first."

### Step 2: Run Helper Scripts
Execute the analysis scripts (located in this skill's `scripts/` directory) to generate data for phases 3, 4, and 7:
```bash
cd {PROJECT_ROOT}
python {SKILLS_DIR}/refactor/scripts/count_complexity.py .claude/refactor/{DATE_PREFIX}_complexity.json
python {SKILLS_DIR}/refactor/scripts/detect_clones.py .claude/refactor/{DATE_PREFIX}_clones.json
python {SKILLS_DIR}/refactor/scripts/compute_hotspots.py .claude/refactor/{DATE_PREFIX}_hotspots.json .claude/refactor/{DATE_PREFIX}_complexity.json
```
Replace `{SKILLS_DIR}` with the actual path to your installed skills directory (e.g., `~/.claude/skills`).

### Step 3: Round 1 — Wide Net (All 7 Phases)
For each phase 1 through 7, **sequentially** launch a `general-purpose` Task agent with:
- The phase reference file path (e.g., `{SKILLS_DIR}/refactor/references/phase-1-hygiene.md`)
- The output format reference path (`{SKILLS_DIR}/refactor/references/output-format.md`)
- `round=1`, `prior_output=none`
- Script output JSON paths for phases 3, 4, and 7
- The project root path
- Instruction: "Analyze the codebase according to the phase reference. Write findings to `.claude/refactor/{DATE_PREFIX}_round_1_phase_{N}_{name}.md`. Return only the summary block."

Read and note the summary block from each agent's response.

### Step 4: Round 2 — Deep Scrutiny (All 7 Phases)
Same as Round 1, but:
- Pass `prior_output` = the Round 1 file path for the same phase
- Add instruction: "Scrutinize deeper. Cross-reference with findings from other phases in Round 1. Mark previously found issues as 'Confirmed' or 'Resolved'. Find what was missed."

### Step 5: Threshold Check for Round 3
Read `references/round-evaluation.md` (relative to this skill) and evaluate whether Round 3 is needed. If triggered, run only the relevant phases.

### Step 6: Generate Report
Launch a `general-purpose` Task agent with:
- `references/report-generation.md` (relative to this skill)
- All `.claude/refactor/{DATE_PREFIX}_round_*_phase_*.md` file paths
- The report template path: `assets/report-template.html` (relative to this skill)
- The generate script path: `scripts/generate_report.py` (relative to this skill)
- Instruction: "Generate the final HTML report."

### Step 7: Present Results
1. Show a brief summary: total findings by severity, top 5 most critical findings
2. Provide the report path: `.claude/refactor/{DATE_PREFIX}_refactor_report.html`
3. Suggest next steps: "To apply findings, use `/two-agent-planning` to plan the refactoring, then `/building-against-plan` to execute with TDD discipline. The planner will automatically use the refactoring workflow variant."

## Important Rules

- **Analysis only**: Never modify source code during this skill. Read-only access to `api/` and `frontend/src/`.
- **Sequential phases**: Phases must run in order (1-7) because they compound.
- **Two Hats Rule**: This skill wears the analysis hat only. Applying changes is a separate workflow.
- **Respect CLAUDE.md**: Follow all project conventions documented in CLAUDE.md.
- **Environment**: Follow the project's CLAUDE.md for environment-specific commands and paths.
