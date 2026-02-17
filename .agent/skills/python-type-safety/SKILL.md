---
name: python-type-safety
description: Leverage Python's type system to catch errors at static analysis time. Use annotations, generics, and protocols for robust code.
---

# Python Type Safety

## When to Use This Skill

- Adding type hints to code
- Configuring strict `mypy` or `pyright`
- Creating generic, reusable classes
- Defining protocols (interfaces)
- Using type narrowing and guards

## Core Concepts

### 1. Type Annotations

Declare expected types for robust documentation and validation.

### 2. Generics

Write reusable code that preserves type information (`list[T]`).

### 3. Protocols

Define structural interfaces (duck typing) enforced by type checkers.

### 4. Type Narrowing

Use `is None`, `isinstance` checks to guide the type checker.

## Fundamental Patterns

### Pattern 1: Annotate All Public Signatures

Functions, methods, and class attributes should have types.

```python
def get_user(user_id: str) -> User:
    ...
```

### Pattern 2: Modern Union Syntax

Use `|` for unions (Python 3.10+).

```python
def find(id: str) -> User | None:
    ...
```

### Pattern 3: Type Narrowing with Guards

```python
def process(user: User | None):
    if user is None:
        return
    # Checker knows user is User here
    print(user.name)
```

### Pattern 4: Generic Classes

Create type-safe containers.

```python
from typing import TypeVar, Generic
T = TypeVar("T")

class Result(Generic[T]):
    def __init__(self, value: T):
        self.value = value
```

## Advanced Patterns

### Pattern 5: Generic Repository

Type-safe data access.

```python
class Repository(Generic[T, ID]):
    def get(self, id: ID) -> T | None: ...
```

### Pattern 6: TypeVar with Bounds

Restrict generics.

```python
ModelT = TypeVar("ModelT", bound=BaseModel)
```

### Pattern 7: Protocols

Structural typing.

```python
from typing import Protocol

class Serializable(Protocol):
    def to_dict(self) -> dict: ...

def save(obj: Serializable):
    data = obj.to_dict()
```

### Pattern 8: Type Aliases

Readable names for complex types.

```python
# Python 3.10+
type UserId = str
type Handler = Callable[[Request], Response]
```

### Pattern 9: Strict Mode Configuration

Enable strict checking in `pyproject.toml` for `mypy`:

```toml
[tool.mypy]
strict = true
disallow_untyped_defs = true
no_implicit_optional = true
```

## Best Practices

1. **Annotate public APIs**.
2. **Use `T | None`** over `Optional[T]`.
3. **Run strict checks** in CI.
4. **Use Generics** for reusability.
5. **Use Protocols** for interfaces.
6. **Minimize `Any`**.
7. **Use Type Aliases** for clarity.
