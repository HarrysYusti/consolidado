---
name: writing-plans
description: Discover and install skills for AI agents.
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context. Document everything: files to touch, code to write, tests to run.
**Context**: Run in a dedicated worktree.
**Save path**: `docs/plans/YYYY-MM-DD-<feature-name>.md`

## The Iron Rules

1.  **Bite-Sized Tasks**: Each step is 2-5 minutes (Write test -> Fail -> Implement -> Pass -> Commit).
2.  **Exact Paths**: Always use full file paths.
3.  **Complete Code**: No "add validation" placeholders. Write the code.
4.  **Exact Commands**: `pytest tests/path/test.py::test_name -v`.

## Plan Document Header

Every plan **MUST** start with:

```markdown
# [Feature Name] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.
> **Goal:** [One sentence]
> **Architecture:** [2-3 sentences]

## **Tech Stack:** [Key technologies]
```

## Task Structure Template

````markdown
### Task N: [Component Name]

**Files:**

- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`

**Step 1: Write the failing test**

```python
def test_thing(): ...
```
````

**Step 2: Run test to verify it fails**
Run: `pytest ...`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
def implementation(): ...
```

**Step 4: Verify pass**
Run: `pytest ...`
Expected: PASS

**Step 5: Commit**

```bash
git add ...
git commit -m "feat: ..."
```

```

## Execution Handoff
Offer options:
1.  **Subagent-Driven**: Single session, fresh subagent per task.
2.  **Parallel Session**: New session with `superpowers:executing-plans`.
```
