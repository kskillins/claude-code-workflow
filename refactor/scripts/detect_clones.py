"""Detect near-duplicate code blocks using sliding window hashing.

Usage:
    python detect_clones.py <output_json_path>

Scans api/ and frontend/src/ for duplicate code blocks (6+ lines).
Outputs JSON: [{hash, locations: [{file, start_line, end_line}], line_count}]
"""

import hashlib
import json
import os
import re
import sys


WINDOW_SIZE = 6  # minimum lines for a clone
EXCLUDE_DIRS = {"node_modules", "venv", "__pycache__", ".git", "dist", "build", ".next"}
EXTENSIONS = {".py", ".ts", ".tsx"}


def normalize_line(line):
    """Normalize a line for comparison: strip whitespace, remove comments."""
    stripped = line.strip()
    # Skip empty lines, pure comment lines, import lines
    if not stripped:
        return None
    if stripped.startswith("#") or stripped.startswith("//"):
        return None
    if stripped.startswith("import ") or stripped.startswith("from "):
        return None
    # Remove inline comments
    stripped = re.sub(r'#.*$', '', stripped)
    stripped = re.sub(r'//.*$', '', stripped)
    # Normalize whitespace
    stripped = re.sub(r'\s+', ' ', stripped).strip()
    return stripped if stripped else None


def collect_files(roots):
    """Collect source files from multiple root directories."""
    files = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for fname in filenames:
                ext = os.path.splitext(fname)[1]
                if ext in EXTENSIONS:
                    files.append(os.path.join(dirpath, fname).replace("\\", "/"))
    return files


def hash_windows(filepath):
    """Generate hashes for sliding windows of normalized lines."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            raw_lines = f.readlines()
    except (OSError, IOError):
        return []

    # Build list of (original_line_number, normalized_content)
    normalized = []
    for i, line in enumerate(raw_lines, 1):
        norm = normalize_line(line)
        if norm is not None:
            normalized.append((i, norm))

    windows = []
    for i in range(len(normalized) - WINDOW_SIZE + 1):
        window = normalized[i:i + WINDOW_SIZE]
        content = "\n".join(line for _, line in window)
        h = hashlib.md5(content.encode("utf-8")).hexdigest()
        start_line = window[0][0]
        end_line = window[-1][0]
        windows.append((h, start_line, end_line))

    return windows


def main():
    if len(sys.argv) < 2:
        print("Usage: detect_clones.py <output_json_path>", file=sys.stderr)
        sys.exit(1)

    output_path = sys.argv[1]
    files = collect_files(["api", "frontend/src"])

    # Collect all window hashes
    hash_locations = {}  # hash -> [(file, start, end)]
    for filepath in files:
        for h, start, end in hash_windows(filepath):
            if h not in hash_locations:
                hash_locations[h] = []
            hash_locations[h].append({
                "file": filepath,
                "start_line": start,
                "end_line": end,
            })

    # Filter: only keep hashes with 2+ locations across different files
    # (or same file but non-overlapping)
    clones = []
    for h, locations in hash_locations.items():
        if len(locations) < 2:
            continue

        # Deduplicate: remove overlapping ranges in the same file
        unique = []
        seen = set()
        for loc in locations:
            key = (loc["file"], loc["start_line"])
            if key not in seen:
                seen.add(key)
                unique.append(loc)

        # Must have locations in 2+ different files, or 2+ non-overlapping in same file
        files_involved = set(loc["file"] for loc in unique)
        if len(files_involved) >= 2 or len(unique) >= 2:
            clones.append({
                "hash": h,
                "locations": unique,
                "line_count": WINDOW_SIZE,
            })

    # Sort by number of locations (most duplicated first)
    clones.sort(key=lambda c: len(c["locations"]), reverse=True)

    # Limit to top 100 to avoid noise
    clones = clones[:100]

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(clones, f, indent=2)

    print(f"Found {len(clones)} clone groups -> {output_path}")


if __name__ == "__main__":
    main()
