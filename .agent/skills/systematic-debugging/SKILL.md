---
name: systematic-debugging
description: Discover and install skills for AI agents.
---

# Systematic Debugging

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

Random fixes waste time. Symptom fixes are failures.

## The Four Phases

### Phase 1: Root Cause Investigation

**Target**: Find the exact line/config causing the issue.

1.  **Read Errors**: Don't skip stack traces.
2.  **Reproduce**: Can you trigger it reliably?
3.  **Check Changes**: Git diff, recent configs.
4.  **Gather Evidence**: Log inputs/outputs at component boundaries.

### Phase 2: Pattern Analysis

**Target**: Understand why it _should_ work.

1.  **Find Working Examples**: Similar code that works.
2.  **Compare**: Read reference implementations _completely_.
3.  **Diff**: List every difference, however small.

### Phase 3: Hypothesis and Testing

**Target**: Confirm the cause.

1.  **Hypothesis**: "I think X is cause because Y".
2.  **Test Minimally**: Change ONE variable.
3.  **Verify**: Did it work? If not, revert and form new hypothesis.

### Phase 4: Implementation

**Target**: Fix it properly.

1.  **Write Test**: Create a test that fails without the fix.
2.  **Implement Fix**: Apply the solution from Phase 3.
3.  **Verify**: Ensure test passes.

## Red Flags - STOP

- "Quick fix for now"
- "Just try changing X"
- "Add multiple changes"
- "I don't fully understand but..."
  **Action**: STOP. Return to Phase 1.
