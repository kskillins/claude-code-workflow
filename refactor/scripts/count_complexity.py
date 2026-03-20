"""Count cyclomatic complexity and line counts for Python and TypeScript files.

Usage:
    python count_complexity.py <output_json_path>

Scans api/ for Python files and frontend/src/ for TypeScript files.
Outputs JSON: [{file, lines, max_complexity, functions: [{name, lines, complexity}]}]
"""

import ast
import json
import os
import sys


def _count_complexity_node(node):
    """Count cyclomatic complexity contributors in an AST node."""
    count = 0
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.IfExp)):
            count += 1
        elif isinstance(child, (ast.For, ast.While, ast.AsyncFor)):
            count += 1
        elif isinstance(child, ast.ExceptHandler):
            count += 1
        elif isinstance(child, ast.BoolOp):
            # Each 'and'/'or' adds a branch
            count += len(child.values) - 1
        elif isinstance(child, ast.Assert):
            count += 1
    return count


def analyze_python_file(filepath):
    """Analyze a Python file for complexity metrics."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
    except (OSError, IOError):
        return None

    lines = source.count("\n") + 1

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return {"file": filepath, "lines": lines, "max_complexity": 0, "functions": []}

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_lines = (node.end_lineno or node.lineno) - node.lineno + 1
            complexity = 1 + _count_complexity_node(node)
            functions.append({
                "name": node.name,
                "line": node.lineno,
                "lines": func_lines,
                "complexity": complexity,
            })

    max_cc = max((f["complexity"] for f in functions), default=0)
    return {
        "file": filepath,
        "lines": lines,
        "max_complexity": max_cc,
        "functions": functions,
    }


def analyze_ts_file(filepath):
    """Analyze a TypeScript file with heuristic complexity metrics."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            source_lines = f.readlines()
    except (OSError, IOError):
        return None

    lines = len(source_lines)
    max_depth = 0
    current_depth = 0

    for line in source_lines:
        stripped = line.strip()
        current_depth += stripped.count("{") - stripped.count("}")
        if current_depth > max_depth:
            max_depth = current_depth

    # Heuristic complexity: count branching keywords
    source = "".join(source_lines)
    complexity = 1
    for keyword in ["if ", "if(", "else if", "case ", "for ", "for(", "while ",
                     "while(", "catch ", "catch(", "&&", "||", "? ", "?."]:
        complexity += source.count(keyword)

    return {
        "file": filepath,
        "lines": lines,
        "max_complexity": min(complexity, 100),  # cap heuristic
        "functions": [{"name": "(module)", "lines": lines, "complexity": complexity}],
    }


def collect_files(root, extensions, exclude_dirs):
    """Walk directory tree collecting files with given extensions."""
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for fname in filenames:
            if any(fname.endswith(ext) for ext in extensions):
                results.append(os.path.join(dirpath, fname).replace("\\", "/"))
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: count_complexity.py <output_json_path>", file=sys.stderr)
        sys.exit(1)

    output_path = sys.argv[1]
    exclude = {"node_modules", "venv", "__pycache__", ".git", "dist", "build", ".next"}

    results = []

    # Python files
    if os.path.isdir("api"):
        for filepath in collect_files("api", [".py"], exclude):
            entry = analyze_python_file(filepath)
            if entry:
                results.append(entry)

    # TypeScript files
    if os.path.isdir("frontend/src"):
        for filepath in collect_files("frontend/src", [".ts", ".tsx"], exclude):
            entry = analyze_ts_file(filepath)
            if entry:
                results.append(entry)

    # Sort by max_complexity descending
    results.sort(key=lambda x: x["max_complexity"], reverse=True)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Analyzed {len(results)} files -> {output_path}")


if __name__ == "__main__":
    main()
