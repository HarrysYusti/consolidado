---
name: find-skills
description: Discover and install skills for AI agents.
---

# Find Skills

## Overview

Use the `npx skills` CLI to discover and install new capabilities for the agent.

## When to Use

- User asks "How do I do X?" (where X is common).
- User wants to add capabilities.
- User mentions a specific domain (e.g., "I need help with AWS").

## The Skills CLI

`npx skills` is the package manager for agent skills.

### Key Commands

1.  **Find**: `npx skills find [query]`
    - Example: `npx skills find react performance`
2.  **Add**: `npx skills add <package>`
    - Example: `npx skills add vercel-labs/agent-skills@vercel-react-best-practices`
3.  **Check**: `npx skills check` (updates)
4.  **Update**: `npx skills update`

## Workflow

1.  **Understand Need**: Identify domain (e.g., React, Testing).
2.  **Search**: Run `npx skills find <keywords>`.
3.  **Present**: Show user the best match with install command.
4.  **Install**: If user agrees, run `npx skills add <package> -g -y`.
