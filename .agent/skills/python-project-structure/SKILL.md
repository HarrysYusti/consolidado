---
name: python-project-structure
description: Design well-organized Python projects with clear module boundaries, explicit public interfaces, and maintainable directory structures.
---

# Python Project Structure & Module Architecture

## When to Use This Skill

- Starting a new Python project from scratch
- Reorganizing an existing codebase for clarity
- Defining module public APIs with `__all__`
- Deciding between flat and nested directory structures
- Determining test file placement strategies
- Creating reusable library packages

## Core Concepts

### 1. Module Cohesion

Group related code that changes together. A module should have a single, clear purpose.

### 2. Explicit Interfaces

Define what's public with `__all__`. Everything not listed is an internal implementation detail.

### 3. Flat Hierarchies

Prefer shallow directory structures. Add depth only for genuine sub-domains.

### 4. Consistent Conventions

Apply naming and organization patterns uniformly across the project.

## Quick Start

### Minimal Source Layout

```text
myproject/
├── src/
│   └── myproject/
│       ├── __init__.py
│       ├── services/
│       ├── models/
│       └── api/
├── tests/
├── pyproject.toml
└── README.md
```

## Fundamental Patterns

### Pattern 1: One Concept Per File

Each file should focus on a single concept or closely related set of functions. Consider splitting when a file grows beyond 300-500 lines or handles multiple responsibilities.

```python
# Good: Focused files
# user_service.py      - User business logic
# user_repository.py   - User data access
# user_models.py       - User data structures

# Avoid: Kitchen sink files
# user.py              - Contains service, repository, models, utilities...
```

### Pattern 2: Explicit Public APIs with `__all__`

Define the public interface for every module. Unlisted members are internal implementation details.

```python
# mypackage/services/__init__.py
from .user_service import UserService
from .order_service import OrderService
from .exceptions import ServiceError, ValidationError

__all__ = [
    "UserService",
    "OrderService",
    "ServiceError",
    "ValidationError",
]
# Internal helpers remain private by omission
# from .internal_helpers import _validate_input  # Not exported
```

### Pattern 3: Flat Directory Structure

Prefer minimal nesting. Deep hierarchies make imports verbose and navigation difficult.

```text
# Preferred: Flat structure
project/
├── api/
│   ├── routes.py
│   └── middleware.py
├── services/
│   ├── user_service.py
│   └── order_service.py
├── models/
│   ├── user.py
│   └── order.py
└── utils/
    └── validation.py
```

### Pattern 4: Test File Organization

**Option A: Colocated Tests** (Good for visibility)

```text
src/
├── user_service.py
├── test_user_service.py
```

**Option B: Parallel Test Directory** (Standard for larger projects)

```text
src/services/user_service.py
tests/services/test_user_service.py
```

## Advanced Patterns

### Pattern 5: Package Initialization

Use `__init__.py` to provide a clean public interface.

```python
# mypackage/__init__.py
"""MyPackage - A library for doing useful things."""
from .core import MainClass
from .config import Settings

__all__ = ["MainClass", "Settings"]
__version__ = "1.0.0"
```

Consumers import directly: `from mypackage import MainClass`.

### Pattern 6: Layered Architecture

Organize by architectural layer for clear separation.

- **api/**: HTTP handlers
- **services/**: Business logic
- **repositories/**: Data access
- **models/**: Domain entities
- **schemas/**: API schemas (Pydantic)
- **config/**: Configuration

### Pattern 7: Domain-Driven Structure

For complex apps, organize by business domain.

```text
ecommerce/
├── users/
│   ├── models.py
│   ├── services.py
│   └── api.py
├── orders/
│   ├── models.py
│   └── ...
└── shared/
```

## File and Module Naming

- **Snake Case**: `user_repository.py` (not `UserRepo.py`)
- **No Abbreviations**: `user_repository.py` (not `usr_repo.py`)
- **Match Classes**: `UserService` in `user_service.py`
- **Absolute Imports**: `from myproject.models import User` (avoid relative imports like `from ..models import User` where possible, though relative imports within a package are sometimes acceptable).

## Best Practices Summary

1. Keep files focused (one concept per file).
2. Define `__all__` explicitly.
3. Prefer flat structures.
4. Use absolute imports.
5. Be consistent.
6. Match names to content.
7. Separate concerns (layers).
8. Document your structure in README.
