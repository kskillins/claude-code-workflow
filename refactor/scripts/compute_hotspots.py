"""Compute git change-frequency hotspots crossed with complexity data.

Usage:
    python compute_hotspots.py <output_json_path> <complexity_json_path>

Parses git log to count change frequency per file, then crosses with
complexity data to produce a ranked hotspot list.

Outputs JSON: [{file, changes, lines, max_complexity, score}]
"""

import json
import os
import subprocess
import sys


def get_git_file_changes():
    """Parse git log to count how often each file was changed."""
    try:
        result = subprocess.run(
            ["git", "log", "--format=format:", "--name-only", "--diff-filter=AMRC"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(f"git log failed: {result.stderr}", file=sys.stderr)
            return {}
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"git log error: {e}", file=sys.stderr)
        return {}

    counts = {}
    for line in result.stdout.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Normalize path separators
        line = line.replace("\\", "/")
        # Only count source files
        if line.endswith((".py", ".ts", ".tsx")):
            counts[line] = counts.get(line, 0) + 1

    return counts


def load_complexity(path):
    """Load complexity JSON into a dict keyed by file path."""
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {entry["file"]: entry for entry in data}
    except (json.JSONDecodeError, KeyError):
        return {}


def main():
    if len(sys.argv) < 3:
        print("Usage: compute_hotspots.py <output_json> <complexity_json>", file=sys.stderr)
        sys.exit(1)

    output_path = sys.argv[1]
    complexity_path = sys.argv[2]

    changes = get_git_file_changes()
    complexity = load_complexity(complexity_path)

    hotspots = []
    # Union of files from both sources
    all_files = set(changes.keys()) | set(complexity.keys())

    for filepath in all_files:
        change_count = changes.get(filepath, 0)
        comp = complexity.get(filepath, {})
        lines = comp.get("lines", 0)
        max_cc = comp.get("max_complexity", 0)

        # Score: change frequency * complexity (higher = more urgent)
        score = change_count * max(max_cc, 1)

        if change_count > 0 or max_cc > 0:
            hotspots.append({
                "file": filepath,
                "changes": change_count,
                "lines": lines,
                "max_complexity": max_cc,
                "score": score,
            })

    # Sort by score descending
    hotspots.sort(key=lambda h: h["score"], reverse=True)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(hotspots, f, indent=2)

    print(f"Computed {len(hotspots)} hotspots -> {output_path}")


if __name__ == "__main__":
    main()
