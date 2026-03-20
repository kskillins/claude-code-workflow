# Report Generation Reference

## Overview

The report generator assembles all phase findings into a single self-contained HTML file. It uses the template at `assets/report-template.html` and injects parsed findings as JSON.

## Process

1. Read all `.claude/refactor/{DATE}_round_*_phase_*.md` files
2. Parse each file into structured finding objects
3. Run `scripts/generate_report.py` to assemble the HTML

## Parsing Rules

Each finding in a phase MD file follows this structure:
```markdown
### [P3-R1-001]
- **File:** api/routers/work_orders.py:142
- **Severity:** Major
- **Status:** New
- **Description:** ...
- **Recommendation:** ...
- **Code snippet:**
<details>
<summary>Show code</summary>
```code```
</details>
```

Parse into JSON:
```json
{
  "id": "P3-R1-001",
  "phase": 3,
  "phase_name": "Structure",
  "round": 1,
  "file": "api/routers/work_orders.py",
  "line": 142,
  "severity": "Major",
  "status": "New",
  "description": "...",
  "recommendation": "...",
  "code_snippet": "..."
}
```

## Report Assembly

The `generate_report.py` script:
1. Reads all phase MD files matching the date prefix
2. Parses findings using regex
3. Reads `assets/report-template.html`
4. Replaces `%%DATA%%` with the JSON array of findings
5. Replaces `%%DATE%%` with the analysis date
6. Replaces `%%TOTAL%%`, `%%CRITICAL%%`, `%%MAJOR%%`, `%%MINOR%%` with counts
7. Writes the final HTML to `.claude/refactor/{DATE}_refactor_report.html`

## Execution

```bash
cd {PROJECT_ROOT}
python {SKILLS_DIR}/refactor/scripts/generate_report.py .claude/refactor {DATE_PREFIX}
```
Replace `{SKILLS_DIR}` with the actual path to your installed skills directory (e.g., `~/.claude/skills`).

Arguments:
- `argv[1]`: path to the refactor output directory (e.g., `.claude/refactor`)
- `argv[2]`: date prefix (e.g., `2026_03_18`)

## Verification

After generation, verify:
- The HTML file exists at the expected path
- The file size is > 1KB (not empty)
- Opening in a browser shows the dashboard with correct counts
