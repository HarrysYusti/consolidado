---
name: python-error-handling
description: Build robust Python applications with proper input validation, meaningful exceptions, and graceful failure handling.
---

# Python Error Handling

## When to Use This Skill

- Validating user input and API parameters
- Designing exception hierarchies
- Handling partial failures in batch operations
- Using Pydantic for complex validation
- Converting external data to domain types
- Implementing fail-fast patterns

## Core Concepts

### 1. Fail Fast

Validate inputs early, before expensive operations. Report errors immediately.

### 2. Meaningful Exceptions

Use appropriate exception types (`ValueError`, not generic `Exception`). Messages should explain _what_ failed and _why_.

### 3. Partial Failures

In batch operations, don't abort everything for one failure. Track successes and failures separately.

### 4. Preserve Context

Chain exceptions (`raise ... from e`) to maintain the debug trail.

## Fundamental Patterns

### Pattern 1: Early Input Validation

Validate at API boundaries.

```python
def process_order(order_id: str, quantity: int):
    if not order_id:
        raise ValueError("'order_id' is required")
    if quantity <= 0:
        raise ValueError(f"'quantity' must be positive, got {quantity}")
    # Proceed...
```

### Pattern 2: Convert to Domain Types Early

Parse strings to Enums or objects immediately.

```python
from enum import Enum

class OutputFormat(Enum):
    JSON = "json"
    CSV = "csv"

def parse_format(val: str) -> OutputFormat:
    try:
        return OutputFormat(val.lower())
    except ValueError:
        raise ValueError(f"Invalid format '{val}'. Valid: {[f.value for f in OutputFormat]}")
```

### Pattern 3: Pydantic for Validation

Use Pydantic for structured data.

```python
from pydantic import BaseModel, Field, field_validator

class UserInput(BaseModel):
    email: str = Field(min_length=5)
    age: int = Field(ge=0, le=150)

    @field_validator("email")
    @classmethod
    def normalize(cls, v: str):
        if "@" not in v: raise ValueError("Invalid email")
        return v.lower()
```

### Pattern 4: Standard Exceptions

Use built-ins where possible: `ValueError`, `TypeError`, `KeyError`, `FileNotFoundError`.

## Advanced Patterns

### Pattern 5: Custom Exceptions with Context

Create domain specific exceptions.

```python
class ApiError(Exception):
    def __init__(self, message: str, status_code: int):
        self.status_code = status_code
        super().__init__(message)

class RateLimitError(ApiError):
    def __init__(self, retry_after: int):
        super().__init__(f"Retry after {retry_after}s", 429)
```

### Pattern 6: Exception Chaining

Preserve original errors.

```python
try:
    # ... operation ...
except FileNotFoundError as e:
    raise ServiceError("Upload failed: file missing") from e
```

### Pattern 7: Batch Processing with Partial Failures

Return a result object containing specific successes and failures.

```python
@dataclass
class BatchResult[T]:
    succeeded: dict[int, T]
    failed: dict[int, Exception]

def process_batch(items: list) -> BatchResult:
    succeeded = {}
    failed = {}
    for idx, item in enumerate(items):
        try:
            succeeded[idx] = process_item(item)
        except Exception as e:
            failed[idx] = e
    return BatchResult(succeeded, failed)
```

## Best Practices Summary

1. **Validate early**.
2. **Use specific exceptions** (`ValueError`, etc).
3. **Include context** in error messages.
4. **Convert types** at boundaries.
5. **Chain exceptions** (`from e`).
6. **Handle partial failures** in batches.
7. **Use Pydantic** for complex validation.
8. **Document failure modes** in docstrings.
