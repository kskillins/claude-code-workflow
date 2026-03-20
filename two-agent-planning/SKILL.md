---
name: two-agent-planning
description: >
  MANDATORY for any non-trivial planning. If a task involves more than a single simple change
  (e.g., multiple files, new pages/features, architectural decisions, phased work, or the user
  asks for a "plan"), you MUST invoke this skill instead of entering plan mode directly.
  Do NOT use the generic Plan agent or freeform plan mode for multi-step work — use this skill.
  Builds comprehensive project plans using an automated two-agent workflow where a planner agent
  creates detailed plans and a separate reviewer agent provides critical analysis, iterating
  until the plan is robust. Asks clarifying questions early and often.
---

# Two-Agent Planning

Produce and review comprehensive plans through an automated planner-reviewer loop. A planner agent drafts the plan, a reviewer agent critiques it, and the cycle repeats until the plan addresses all identified issues.

## Mandatory rules

1. **Only the user can approve a plan.** Reviewer APPROVED is a quality gate, not authorization. These are separate gates -- never conflate them.
2. **Minimum 2 planner-reviewer cycles** (3 for complex tasks with >5 files or architectural decisions). Even a first-cycle APPROVED triggers a mandatory re-review with deeper scrutiny.
3. **You are the orchestrator, not the fixer.** REVISE means launch a new planner agent then a new reviewer agent. Never incorporate feedback yourself. Never say "rather than another cycle." Never skip the reviewer.
4. **Phase 5 is mandatory.** Read the final plan fresh from disk and present it in full. Never summarize or paraphrase.

## Core principles

1. **The plan is the real work** -- invest energy in planning, not patching forward
2. **Fresh perspective finds different problems** -- a separate reviewer catches what the planner missed
3. **Ambiguity is the enemy** -- ask clarifying questions before planning, not during implementation
4. **Iterate until robust** -- keep cycling until no critical issues remain
5. **Verify, don't assume** -- every claim in the plan must be defensible
6. **Plan for TDD execution** -- every phase must define testable behaviors so tests can be written before implementation

## Context window protocol

Sub-agents communicate through disk, not through the main agent's context.

**Sub-agent type:** All sub-agents use `general-purpose` (they need Write access to save output).

**File locations:**
- Plans: `.claude/plans/{project-name}-plan-vN.md`
- Reviews: `.claude/reviews/{project-name}-review-vN.md`

**Project name:** During Phase 1, derive a 1-2 word kebab-case project name from the task (e.g., `auth-flow`, `csv-export`, `route-proxy`). Use this name consistently in all file paths for plans and reviews. This prevents overwriting plans from different tasks.

**Launch prompts must be under 10 lines.** Provide file paths, cycle number, and an instruction to read the role guide. Never paste plan or review content into prompts.

**Summary block requirement:** Every sub-agent must end its response with:
```
---
CYCLE: N
SAVED TO: [path]
VERDICT: APPROVED|REVISE|RETHINK (reviewer only)
CRITICAL: count | MAJOR: count | MINOR: count (reviewer only)
KEY ISSUES: [one-line each, max 3] (reviewer only)
---
```
Use ONLY this block to decide the next action. Ignore any other text in the response.

**Deferred reading:** Do NOT read plan or review files during iteration (Phase 4). Only read the final plan in Phase 5 for user presentation.

## Workflow

### Phase 1: Clarification

Before any planning, gather requirements and reduce ambiguity.

1. Restate the user's goal to confirm understanding
2. Identify ambiguities, unstated assumptions, and missing context
3. Ask targeted clarifying questions (batch logically, don't overwhelm)
4. Confirm scope, priorities, and constraints
5. Select workflow variant -- see [references/workflow-variants.md](references/workflow-variants.md)

**Clarification checklist:**
- What is the desired outcome?
- What are the hard constraints (tools, environment, dependencies)?
- What are the known unknowns?
- Are there existing patterns or conventions to follow?
- What does "done" look like?

Proceed only when requirements are clear enough to plan against.

### Phase 2: Plan creation (Planner agent)

Launch a `general-purpose` Task agent with a prompt like:

```
You are a planner agent. Read your methodology: [skill-path]/references/planner-role.md
GOAL: [from Phase 1]  CONSTRAINTS: [from Phase 1]  CONTEXT: [key file paths]
PROJECT NAME: [project-name]  CYCLE: N  PRIOR PLAN: [path or N/A]  PRIOR REVIEW: [path or N/A]
Write plan to .claude/plans/{project-name}-plan-vN.md. End response with summary block only.
```

The planner reads its role guide, reads prior files from disk, writes the plan, and returns the summary block. Do NOT read the plan file after the agent returns.

### Phase 3: Plan review (Reviewer agent)

Launch a separate `general-purpose` Task agent:

```
You are a reviewer agent. Read your methodology: [skill-path]/references/reviewer-role.md
PROJECT NAME: [project-name]  CYCLE: N  PLAN TO REVIEW: .claude/plans/{project-name}-plan-vN.md
Write review to .claude/reviews/{project-name}-review-vN.md. End response with summary block only.
```

The reviewer reads its role guide, reads the plan from disk, writes the review, and returns the summary block with verdict. Do NOT read the review file after the agent returns.

### Phase 4: Iteration

Based on the summary block verdict:

**APPROVED on cycle 1 (mandatory re-review):**
Launch a new reviewer: "Apply deeper scrutiny. Challenge assumptions the first reviewer accepted too easily." If second review also approves, proceed to Phase 5. If REVISE, continue below.

**APPROVED on cycle 2+:** Proceed to Phase 5.

**REVISE:**
STOP. Do NOT present the plan. Do NOT incorporate feedback yourself.
1. Launch new planner agent with paths to prior plan and review files
2. Launch new reviewer agent on the revised plan
3. Repeat until APPROVED or 5 cycles exhausted
4. At 5 cycles: present current state with outstanding issues, ask user for direction

**RETHINK:**
Present fundamental concerns to the user. Ask clarifying questions. Return to Phase 2.

**Cycle log** (maintain this, show in Phase 5):
```
Cycle 1: {project-name}-plan-v1.md -> {project-name}-review-v1.md | REVISE | 0C 2M 1m
Cycle 2: {project-name}-plan-v2.md -> {project-name}-review-v2.md | APPROVED | 0C 0M 1m
```

### Phase 5: User presentation and approval

**Entry gate -- all must be true:**
- [ ] Most recent reviewer verdict: APPROVED
- [ ] At least 2 full cycles completed
- [ ] All plan/review files saved to disk

If any unchecked, return to Phase 4.

**Read the final plan fresh from disk** (`.claude/plans/{project-name}-plan-vN.md`) using the Read tool.

Present to the user with:
1. Executive summary (plain language)
2. The full plan (unabridged, as read from disk)
3. Key decisions and trade-offs
4. Risks acknowledged and mitigations
5. Cycle log showing all iterations
6. Issues resolved across cycles
7. Open questions requiring user input
8. Saved artifact paths

Ask: "Do you approve this plan for implementation, or would you like changes?"
- Approved: ready for execution via the `building-against-plan` skill
- Changes requested: return to Phase 2, run full review cycle again
- Questions: answer them, then ask for approval again

## When to re-plan

If execution of an approved plan starts failing:
- Stop immediately -- do not patch forward
- Assess what went wrong and what new information emerged
- Return to Phase 2 with accumulated knowledge

## Anti-patterns

- Rushing clarification to start planning faster
- Patching a failing plan instead of re-planning
- Summarizing the plan to the user instead of presenting in full
- Reading plan/review content into your context during iteration
- Passing plan/review content in sub-agent prompts instead of file paths
- Treating reviewer APPROVED as user approval

## Utility scripts

**Validate plan structure:**
```bash
python scripts/validate_plan.py <plan-file.md>
```

## After approval (MANDATORY handoff)

When the user approves the plan, you MUST hand off to `building-against-plan` for execution. Do NOT offer to implement directly. Do NOT say "I'll implement this directly since the plan has code snippets." The `building-against-plan` skill enforces TDD discipline, quality gates, and test immutability that direct implementation skips.

**Required behavior after user approval:**
1. State: "Plan approved. Invoking `/building-against-plan` to execute with TDD discipline."
2. Invoke the `building-against-plan` skill via the Skill tool
3. Never proceed to write implementation code without going through the skill

**Why this matters:** Even when the plan contains exact code snippets, the `building-against-plan` skill ensures:
- Tests are written BEFORE implementation (Red-Green-Refactor)
- Tests are never edited to pass — only production code is fixed
- Quality gates (lint, type check, format, tests) run after every phase
- Specialist agents handle each step (qa-test-engineer for tests, feature-implementer for code, debugger for failures)
- Edge cases get dedicated test coverage

## Plan format contract (for building-against-plan compatibility)

Plans produced by the planner agent MUST include these sections in each phase to enable mechanical extraction by `building-against-plan`:

### Required per-phase sections

- **`### Testable Behaviors`** — bulleted list where each item becomes one or more tests. Each item specifies: function/endpoint name, inputs, expected outputs, error conditions. If this section is missing, `building-against-plan` cannot write tests-first.
- **`### Success Criteria`** — concrete, verifiable conditions expressed as assertions where possible (e.g., "POST /api/users returns 201 with {id, name, email}" not "the endpoint works").
- **`### Dependencies`** — what must exist before this phase starts. References specific prior phase deliverables.

### Format example

```markdown
### Phase 2: User Authentication

#### Testable Behaviors
- `authenticate(email, password)`: valid credentials returns JWT token with user_id claim; invalid password raises AuthError; nonexistent email raises AuthError; expired account raises AccountDisabledError
- `POST /api/auth/login`: accepts {email, password}, returns 200 with {token, expires_at}; returns 401 for invalid credentials; returns 422 for missing fields

#### Success Criteria
- All auth tests pass (unit + integration)
- JWT tokens are verifiable with the project's signing key
- Login endpoint returns correct status codes for all error cases

#### Dependencies
- Phase 1 complete: User model exists with password_hash field
- Database migrations applied
```

This contract ensures the planner's output is directly consumable by the build skill without guessing or re-interpretation.

## References

- **Planner role guide**: [references/planner-role.md](references/planner-role.md) (read by planner agents)
- **Reviewer role guide**: [references/reviewer-role.md](references/reviewer-role.md) (read by reviewer agents)
- **Workflow variants**: [references/workflow-variants.md](references/workflow-variants.md) (simple/complex/exploratory/refactoring)
- **Refactoring workflow**: [references/refactoring-workflow.md](references/refactoring-workflow.md) (read by planner agents when applying /refactor findings)
