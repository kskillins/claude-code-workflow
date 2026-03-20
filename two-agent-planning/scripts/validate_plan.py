#!/usr/bin/env python3
"""Validate that a plan file contains all required sections and structure.

Usage:
    python validate_plan.py <plan-file.md>
    python validate_plan.py <plan-file.md> --strict

Checks for:
- Required top-level sections (Overview, Phases, etc.)
- Phase structure (goals, tasks, success criteria, dependencies, risks)
- Technical decisions with rationale
- Risk assessment presence
- Verification strategy
- Open questions section

Exit codes:
    0 - All checks passed
    1 - Structural issues found
    2 - File not found or read error
"""

import sys
import re
from pathlib import Path


REQUIRED_SECTIONS = [
    "overview",
    "phase",
    "technical decision",
    "risk assessment",
    "verification strategy",
]

REQUIRED_PHASE_ELEMENTS = [
    "goal",
    "task",
    "success criteria",
    "dependenc",
    "risk",
]

RECOMMENDED_SECTIONS = [
    "open question",
]


def read_plan(filepath: str) -> str:
    """Read plan file and return contents."""
    path = Path(filepath)
    if not path.exists():
        print(f"ERROR: File not found: {filepath}")
        sys.exit(2)
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"ERROR: Could not read file: {e}")
        sys.exit(2)


def find_sections(content: str) -> list:
    """Extract all markdown headers from the content."""
    headers = re.findall(r"^(#{1,4})\s+(.+)$", content, re.MULTILINE)
    return [(len(h[0]), h[1].strip()) for h in headers]


def find_phases(content: str) -> list:
    """Extract phase sections from the plan."""
    phase_pattern = re.compile(
        r"^###?\s+Phase\s+\d+[:\s].*$", re.MULTILINE | re.IGNORECASE
    )
    return phase_pattern.findall(content)


def extract_phase_content(content: str) -> list:
    """Extract the content of each phase section."""
    phase_splits = re.split(
        r"(?=^###?\s+Phase\s+\d+)", content, flags=re.MULTILINE | re.IGNORECASE
    )
    return [s for s in phase_splits if re.match(r"^###?\s+Phase\s+\d+", s, re.IGNORECASE)]


def check_required_sections(content: str, strict: bool) -> list:
    """Check that all required top-level sections are present."""
    issues = []
    content_lower = content.lower()

    for section in REQUIRED_SECTIONS:
        if section not in content_lower:
            issues.append(f"CRITICAL: Missing required section: '{section}'")

    for section in RECOMMENDED_SECTIONS:
        if section not in content_lower:
            level = "MAJOR" if strict else "MINOR"
            issues.append(f"{level}: Missing recommended section: '{section}'")

    return issues


def check_phase_structure(content: str) -> list:
    """Check that each phase has required elements."""
    issues = []
    phases = extract_phase_content(content)

    if not phases:
        issues.append("CRITICAL: No phases found in the plan")
        return issues

    for i, phase_content in enumerate(phases, 1):
        phase_lower = phase_content.lower()
        phase_header = phase_content.split("\n")[0].strip()

        for element in REQUIRED_PHASE_ELEMENTS:
            if element not in phase_lower:
                issues.append(
                    f"MAJOR: Phase ({phase_header}) missing '{element}' section"
                )

    return issues


def check_verification(content: str) -> list:
    """Check for verification and success criteria patterns."""
    issues = []
    content_lower = content.lower()

    verification_terms = ["success criteria", "verification", "verify", "confirm", "test"]
    has_verification = any(term in content_lower for term in verification_terms)

    if not has_verification:
        issues.append(
            "CRITICAL: No verification or success criteria found anywhere in the plan"
        )

    return issues


def check_rationale(content: str) -> list:
    """Check that technical decisions include rationale."""
    issues = []
    content_lower = content.lower()

    if "technical decision" in content_lower or "technical approach" in content_lower:
        rationale_terms = ["because", "rationale", "reason", "why", "trade-off", "tradeoff", "alternative"]
        has_rationale = any(term in content_lower for term in rationale_terms)
        if not has_rationale:
            issues.append(
                "MAJOR: Technical decisions section exists but contains no rationale or alternatives"
            )

    return issues


def validate_plan(filepath: str, strict: bool = False) -> list:
    """Run all validation checks and return issues."""
    content = read_plan(filepath)
    issues = []

    issues.extend(check_required_sections(content, strict))
    issues.extend(check_phase_structure(content))
    issues.extend(check_verification(content))
    issues.extend(check_rationale(content))

    return issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_plan.py <plan-file.md> [--strict]")
        sys.exit(2)

    filepath = sys.argv[1]
    strict = "--strict" in sys.argv

    print(f"Validating plan: {filepath}")
    print(f"Mode: {'strict' if strict else 'standard'}")
    print("-" * 50)

    issues = validate_plan(filepath, strict)

    if not issues:
        print("All checks passed. Plan structure is valid.")
        sys.exit(0)

    critical = [i for i in issues if i.startswith("CRITICAL")]
    major = [i for i in issues if i.startswith("MAJOR")]
    minor = [i for i in issues if i.startswith("MINOR")]

    if critical:
        print(f"\nCRITICAL issues ({len(critical)}):")
        for issue in critical:
            print(f"  - {issue}")

    if major:
        print(f"\nMAJOR issues ({len(major)}):")
        for issue in major:
            print(f"  - {issue}")

    if minor:
        print(f"\nMINOR issues ({len(minor)}):")
        for issue in minor:
            print(f"  - {issue}")

    print(f"\nTotal: {len(critical)} critical, {len(major)} major, {len(minor)} minor")

    if critical or major:
        print("\nResult: FAIL - Plan has structural issues that should be addressed.")
        sys.exit(1)
    else:
        print("\nResult: PASS - Only minor suggestions found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
