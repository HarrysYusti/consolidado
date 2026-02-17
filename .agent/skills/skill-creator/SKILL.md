---
name: skill-creator
description: Discover and install skills for AI agents.
---

# Skill Creator

## Overview

Guide for creating effectives skills for AI agents.

## Core Principles

1.  **Concise is Key**: Context window is precious. Only add non-obvious context.
2.  **Degrees of Freedom**:
    - **High**: Text instructions (multiple valid approaches).
    - **Medium**: Pseudocode (preferred patterns).
    - **Low**: Scripts (fragile operations).

## Anatomy of a Skill

Structure:

```
skill-name/
  ├── SKILL.md (Required)
  │   ├── Frontmatter (YAML)
  │   └── Body (Markdown instructions)
  └── assets/ (Optional templates)
  └── scripts/ (Optional executable code)
  └── references/ (Optional docs)
```

## Creation Process

1.  **Understand**: Get concrete examples of usage.
2.  **Plan**: Identify reusable resources (scripts, assets).
3.  **Initialize**: `scripts/init_skill.py <name>` (if available) or manual creation.
4.  **Edit**: Write `SKILL.md` (Imperative mood) and resources.
5.  **Package**: `scripts/package_skill.py <path>`.
6.  **Iterate**: Improvements based on usage.

## SKILL.md Guidelines

- **Frontmatter**: `name` and `description` ONLY.
- **Description**: Must include **triggers** (when to use).
- **Body**: Instructions loaded _after_ triggering.
