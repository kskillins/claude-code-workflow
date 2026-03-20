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

## Prerequisites

- [Claude Code](https://claude.ai/code) installed and working
- [Git](https://git-scm.com/downloads) installed

## Installation

### Step 1: Clone this repo

Pick a place to download it. This is a temporary clone — you'll copy the skills out of it.

**PowerShell (Windows):**
```powershell
cd $env:USERPROFILE\Downloads
git clone https://github.com/kskillins/claude-code-workflow.git
cd claude-code-workflow
```

**bash (macOS/Linux):**
```bash
cd ~/Downloads
git clone https://github.com/kskillins/claude-code-workflow.git
cd claude-code-workflow
```

### Step 2: Copy the skills

Choose **one** of the two options below.

#### Option A: Global installation (all your projects get the skills)

**PowerShell (Windows):**
```powershell
# Create the skills folder if it doesn't exist
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null

# Copy each skill
$skills = "build", "small-feature", "two-agent-planning", "building-against-plan", "refactor"
foreach ($s in $skills) {
    Copy-Item -Recurse -Force $s "$env:USERPROFILE\.claude\skills\$s"
}
```

**bash (macOS/Linux):**
```bash
mkdir -p ~/.claude/skills
cp -r build small-feature two-agent-planning building-against-plan refactor ~/.claude/skills/
```

#### Option B: Project-level installation (skills only available in one project)

Run this from inside your project directory (not the clone):

**PowerShell (Windows):**
```powershell
# From your project root:
New-Item -ItemType Directory -Force -Path .claude\skills | Out-Null

$clonePath = "$env:USERPROFILE\Downloads\claude-code-workflow"
$skills = "build", "small-feature", "two-agent-planning", "building-against-plan", "refactor"
foreach ($s in $skills) {
    Copy-Item -Recurse -Force "$clonePath\$s" ".claude\skills\$s"
}
```

**bash (macOS/Linux):**
```bash
# From your project root:
mkdir -p .claude/skills
cp -r ~/Downloads/claude-code-workflow/{build,small-feature,two-agent-planning,building-against-plan,refactor} .claude/skills/
```

### Step 3: Add the CLAUDE.md configuration

Open the `CLAUDE.md` file from this repo and copy the sections you want into your own `CLAUDE.md`:

- For **global** install: paste into `~/.claude/CLAUDE.md` (create it if it doesn't exist)
- For **project** install: paste into the `CLAUDE.md` at your project root

At minimum, copy the **Development Workflow** and **Sub-Agents and Skills** sections. The rest (Core Principles, Refactoring Discipline, etc.) are recommended but optional.

### Step 4: Verify

Open Claude Code in your project and type `/build`. If it appears in the skill list, you're good.

### Cleanup

You can delete the clone after installation:

**PowerShell:**
```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\Downloads\claude-code-workflow"
```

**bash:**
```bash
rm -rf ~/Downloads/claude-code-workflow
```

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
