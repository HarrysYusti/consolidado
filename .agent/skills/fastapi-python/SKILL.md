---
name: fastapi-python
description: Expert guidelines for FastAPI and Python backend development, focusing on concise, functional, and performant code.
---

# FastAPI Python

## Key Principles

- **Concise & Technical**: Accurate Python examples.
- **Functional over Class-based**: Prefer plain functions for routes and dependencies.
- **Modularization**: Eliminate duplication, export explicitly.
- **Naming**: `snake_case` for files/functions, boolean prefixes (`is_active`).
- **RORO Pattern**: Receive Object, Return Object.

## Standards

- Use `def` for pure functions, `async def` for I/O.
- **Type Hints**: Mandatory. Prefer Pydantic models.
- **Structure**:
  - `routers/`
  - `schemas/`
  - `models/`
  - `services/`
- **Conditionals**: One-line syntax where appropriate, omit braces.

## Error Handling

- **Guard Clauses**: Handle edge cases early. return/raise early.
- **HTTPException**: Use for expected API errors.
- **Avoid `else`**: Use if-return pattern.

## Guidelines

1. **Validation**: Use Pydantic models.
2. **Return Types**: Annotate all routes.
3. **Lifespan**: Use context managers for startup/shutdown.
4. **Middleware**: For logging/monitoring.

## Performance

- **Sync/Async**: Use `async` for DB/API calls.
- **Caching**: implement Redis/in-memory.
- **Lazy Loading**: For large datasets.

## Example Route

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(UserCreate):
    id: int

@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db: Database = Depends(get_db)) -> UserResponse:
    if await db.user_exists(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = await db.create_user(user)
    return new_user
```
