---
name: python-code-style
description: Consistent code style and clear documentation make codebases maintainable and collaborative. This skill covers modern Python tooling, naming conventions, and documentation standards.
---

# Python Code Style & Documentation

## When to Use This Skill

- Setting up linting and formatting for a new project
- Writing or reviewing docstrings
- Establishing team coding standards
- Configuring ruff, mypy, or pyright
- Reviewing code for style consistency
- Creating project documentation

## Core Concepts

### 1. Automated Formatting

Let tools handle formatting debates. Configure once, enforce automatically.

### 2. Consistent Naming

Follow PEP 8 conventions with meaningful, descriptive names.

### 3. Documentation as Code

Docstrings should be maintained alongside the code they describe.

### 4. Type Annotations

Modern Python code should include type hints for all public APIs.

## Quick Start

```bash
# Install modern tooling
pip install ruff mypy
```

Configure in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 120
target-version = "py312"

[tool.mypy]
strict = true
```

## Fundamental Patterns

### Pattern 1: Modern Python Tooling

Use **ruff** as an all-in-one linter and formatter. It replaces flake8, isort, and black.

**pyproject.toml configuration:**

```toml
[tool.ruff]
line-length = 120
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "UP", # pyupgrade
    "SIM", # flake8-simplify
]
ignore = ["E501"] # Line length handled by formatter

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

Run with:

```bash
ruff check --fix .
ruff format .
```

### Pattern 2: Type Checking Configuration

Configure strict type checking for production code.

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

### Pattern 3: Naming Conventions

Follow PEP 8 with emphasis on clarity.

- **Classes**: `PascalCase` (e.g., `UserRepository`)
- **Functions/Variables**: `snake_case` (e.g., `get_user_by_email`)
- **Constants**: `SCREAMING_SNAKE_CASE` (e.g., `MAX_RETRY_ATTEMPTS`)
- **Avoid Abbreviations**: Use `user_repository` instead of `usr_repo`.

### Pattern 4: Import Organization

Group imports: Standard Lib -> Third Party -> Local. Use absolute imports.

```python
# Standard library
import os
from typing import Any

# Third-party packages
import httpx
from pydantic import BaseModel

# Local imports
from myproject.models import User
```

## Advanced Patterns

### Pattern 5: Google-Style Docstrings

Write docstrings for all public APIs.

**Function Example:**

```python
def process_batch(items: list[Item], max_workers: int = 4) -> BatchResult:
    """Process items concurrently using a worker pool.

    Args:
        items: The items to process. Must not be empty.
        max_workers: Maximum concurrent workers. Defaults to 4.

    Returns:
        BatchResult containing succeeded items and exceptions.

    Raises:
        ValueError: If items is empty.
    """
    ...
```

**Class Example:**

```python
class UserService:
    """Service for managing user operations.

    Attributes:
        repository: The data access layer.
    """
```

### Pattern 6: Line Length

Set line length to **120 characters** for modern displays.

### Pattern 7: Project Documentation

**README Structure:**

1. **Title & Badges**
2. **Brief Description**
3. **Installation**
4. **Quick Start**
5. **Configuration**
6. **Development**

## Best Practices Summary

1. **Use ruff** - Single tool for linting and formatting.
2. **Enable strict mypy** - Catch type errors early.
3. **120 character lines** - Modern readability.
4. **Descriptive names** - Clarity over brevity.
5. **Absolute imports** - Avoid relative imports.
6. **Google-style docstrings** - Consistent documentation.
7. **Document public APIs**.
8. **Automate in CI**.
