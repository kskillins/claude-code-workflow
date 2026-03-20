# Claude Code Build Workflow

A unified development workflow for [Claude Code](https://claude.ai/code) that weaves preparatory refactoring into every feature build. One command (`/build`) assesses scope, scans for structural issues, and routes work through the correct skill with TDD discipline.

## What's included

| Skill | Purpose |
|-------|---------|
| `/build` | Entry point. Scope assessment + Boy Scout scan + routing |
| `/small-feature` | TDD workflow for 1-3 file changes |
| `/two-agent-planning` | Planner + reviewer agents for medium/large features |
| `/building-against-plan` | TDD execution engine for approved plans |
| `/refactor` | Standalone multi-phase codebase analysis |

## How it works

```
/build "add phone field to customer form"
  |
  +-- Step 1: Understand task
  +-- Step 2: Scope assessment (small/medium/large)
  +-- Step 3: Preparatory refactoring scan
  |     +-- Boy Scout hygiene (unused imports, bad names)
  |     +-- Structural readiness (long functions, deep nesting)
  |     +-- Consolidation search (3x rule violations)
  |     +-- Architectural signals (data clumps, feature envy)
  |
  +-- Step 4: Route to downstream skill with findings
        |
        +-- Small  -> /small-feature (with cleanup list)
        +-- Medium -> /two-agent-planning (simple variant, with Phase 0)
        +-- Large  -> /two-agent-planning (complex variant, with Phase 0)
```

Refactoring happens at three points:
1. **Before coding** - preparatory scan finds structural issues to fix first
2. **During coding** - Boy Scout check after each build phase
3. **After coding** - mandatory scan of touched files before commit

## Installation

### Option A: Global installation (all projects)

Copy the skill directories into your Claude Code skills folder:

```bash
# macOS/Linux
cp -r build small-feature two-agent-planning building-against-plan refactor ~/.claude/skills/

# Windows (Git Bash)
cp -r build small-feature two-agent-planning building-against-plan refactor "$USERPROFILE/.claude/skills/"
```

Then merge the contents of `CLAUDE.md` from this repo into your `~/.claude/CLAUDE.md`.

### Option B: Project-level installation (single project)

Copy into your project's `.claude/skills/` directory:

```bash
mkdir -p .claude/skills
cp -r build small-feature two-agent-planning building-against-plan refactor .claude/skills/
```

Then merge the contents of `CLAUDE.md` from this repo into your project's `CLAUDE.md`.

### Post-install

After copying, verify the skills are detected by running Claude Code and typing `/build`. You should see it in the skill list.

## Customization

### Project-specific verification gates

The `building-against-plan` skill has a "Project-specific verification gates" section with generic categories. Replace these with checks derived from your own project's historical bugs. For example:

- If your project uses PostgREST, add FK ambiguity checks
- If your app is mobile-first, add viewport verification gates
- If you use Pydantic, add model/form alignment checks

### Refactor exclusion rules

The `/refactor` skill enforces exclusion rules (no UI layout suggestions, no feature removal, etc.). These are intentional -- refactoring should only change code structure, never behavior or design.

### Scope thresholds

The `/build` scope matrix uses file count as the primary signal. Adjust the thresholds in `build/SKILL.md` if your project has a different density (e.g., if touching 5 files is routine in your codebase, raise the small/medium boundary).

## Philosophy

This workflow is built on three ideas from Martin Fowler's *Refactoring* and Kent Beck's TDD:

1. **"Make the change easy, then make the easy change"** - Preparatory refactoring before every feature ensures you're never building on a shaky foundation.

2. **The Boy Scout Rule** - Leave code cleaner than you found it, but bounded to the files you touched. No scope creep into unrelated cleanup.

3. **Two Hats Rule** - Never mix refactoring with feature work in the same commit. Each commit is either structural (refactoring) or behavioral (feature/fix).
