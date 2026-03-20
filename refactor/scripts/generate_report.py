"""Generate interactive HTML report from phase markdown findings.

Usage:
    python generate_report.py <refactor_dir> <date_prefix>

Example:
    python generate_report.py .claude/refactor 2026_03_18

Reads all {date_prefix}_round_*_phase_*.md files, parses findings,
and assembles the HTML report using the template.
"""

import json
import os
import re
import sys


PHASE_NAMES = {
    1: "Hygiene",
    2: "Naming",
    3: "Structure",
    4: "Duplication",
    5: "Consistency",
    6: "Coupling",
    7: "Hotspots",
}

TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets",
    "report-template.html",
)


def parse_findings(filepath):
    """Parse a phase markdown file into a list of finding dicts."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, IOError):
        return []

    findings = []
    # Split on finding headers: ### [P3-R1-001]
    pattern = r'###\s*\[([A-Z]\d+-R\d+-\d+)\]'
    parts = re.split(pattern, content)

    # parts[0] is preamble, then alternating: id, body, id, body...
    for i in range(1, len(parts) - 1, 2):
        finding_id = parts[i]
        body = parts[i + 1]

        # Parse phase and round from ID
        id_match = re.match(r'P(\d+)-R(\d+)-(\d+)', finding_id)
        if not id_match:
            continue

        phase = int(id_match.group(1))
        round_num = int(id_match.group(2))

        # Extract fields
        file_match = re.search(r'\*\*File:\*\*\s*(.+?)(?:\n|$)', body)
        severity_match = re.search(r'\*\*Severity:\*\*\s*(.+?)(?:\n|$)', body)
        status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', body)
        desc_match = re.search(r'\*\*Description:\*\*\s*(.+?)(?:\n|$)', body)
        rec_match = re.search(r'\*\*Recommendation:\*\*\s*(.+?)(?:\n|$)', body)

        # Extract code snippet if present
        snippet_match = re.search(r'```[\w]*\n(.*?)```', body, re.DOTALL)

        # Parse file:line
        file_path = ""
        line = 0
        if file_match:
            file_str = file_match.group(1).strip()
            if ":" in file_str:
                parts_fl = file_str.rsplit(":", 1)
                file_path = parts_fl[0]
                try:
                    line = int(parts_fl[1])
                except ValueError:
                    file_path = file_str
            else:
                file_path = file_str

        finding = {
            "id": finding_id,
            "phase": phase,
            "phase_name": PHASE_NAMES.get(phase, f"Phase {phase}"),
            "round": round_num,
            "file": file_path,
            "line": line,
            "severity": severity_match.group(1).strip() if severity_match else "Minor",
            "status": status_match.group(1).strip() if status_match else "New",
            "description": desc_match.group(1).strip() if desc_match else "",
            "recommendation": rec_match.group(1).strip() if rec_match else "",
            "code_snippet": snippet_match.group(1).strip() if snippet_match else "",
        }
        findings.append(finding)

    return findings


def main():
    if len(sys.argv) < 3:
        print("Usage: generate_report.py <refactor_dir> <date_prefix>", file=sys.stderr)
        sys.exit(1)

    refactor_dir = sys.argv[1]
    date_prefix = sys.argv[2]

    # Collect all phase MD files
    all_findings = []
    if os.path.isdir(refactor_dir):
        for fname in sorted(os.listdir(refactor_dir)):
            if fname.startswith(date_prefix) and "_round_" in fname and fname.endswith(".md"):
                filepath = os.path.join(refactor_dir, fname)
                findings = parse_findings(filepath)
                all_findings.extend(findings)

    # Compute counts
    total = len(all_findings)
    critical = sum(1 for f in all_findings if f["severity"] == "Critical")
    major = sum(1 for f in all_findings if f["severity"] == "Major")
    minor = sum(1 for f in all_findings if f["severity"] == "Minor")

    # Read template
    if not os.path.isfile(TEMPLATE_PATH):
        print(f"Template not found: {TEMPLATE_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    # Inject data
    display_date = date_prefix.replace("_", "-")
    html = template.replace("%%DATA%%", json.dumps(all_findings, indent=2))
    html = html.replace("%%DATE%%", display_date)
    html = html.replace("%%TOTAL%%", str(total))
    html = html.replace("%%CRITICAL%%", str(critical))
    html = html.replace("%%MAJOR%%", str(major))
    html = html.replace("%%MINOR%%", str(minor))

    # Write output
    output_path = os.path.join(refactor_dir, f"{date_prefix}_refactor_report.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated report: {output_path} ({total} findings)")


if __name__ == "__main__":
    main()
