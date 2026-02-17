---
name: python-configuration
description: Externalize configuration from code using environment variables and typed settings (Pydantic).
---

# Python Configuration Management

## When to Use This Skill

- Setting up project configuration
- Migrating hardcoded values to env vars
- Implementing typed settings with `pydantic-settings`
- Managing secrets
- Environment-specific config (dev/prod)

## Core Concepts

### 1. Externalized Configuration

Values come from the environment (The 12-Factor App).

### 2. Typed Settings

Validate config at startup into typed objects.

### 3. Fail Fast

Crash immediately if required config is missing.

### 4. Sensible Defaults

Ease local dev with defaults, force explicit values for prod secrets.

## Fundamental Patterns

### Pattern 1: Typed Settings with Pydantic

Central settings class.

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(alias="DATABASE_URL")
    api_key: str = Field(alias="API_KEY")
    debug: bool = Field(default=False, alias="DEBUG")

    model_config = {"env_file": ".env"}

settings = Settings()
```

### Pattern 2: Fail Fast

Require critical vars. Pydantic raises `ValidationError` at startup if missing.

### Pattern 3: Local Defaults

Use defaults for non-sensitive local dev settings.

```python
db_host: str = Field(default="localhost", alias="DB_HOST")
```

### Pattern 4: Namespaced Env Vars

Prefix variables for clarity.
`DB_HOST`, `REDIS_URL`, `AUTH_SECRET`.

## Advanced Patterns

### Pattern 5: Environment Separation

Use an Enum to detect environment.

```python
class Environment(str, Enum):
    LOCAL = "local"
    PROD = "production"

class Settings(BaseSettings):
    env: Environment = Field(default=Environment.LOCAL, alias="ENV")

    @property
    def is_prod(self):
        return self.env == Environment.PROD
```

### Pattern 6: Nested Configuration

Group settings.

```python
class DatabaseSettings(BaseModel):
    host: str
    port: int

class Settings(BaseSettings):
    db: DatabaseSettings

    model_config = {"env_nested_delimiter": "__"}
```

Env var: `DB__HOST=localhost`

### Pattern 7: Docker Secrets

Read from mounted files.

```python
model_config = {"secrets_dir": "/run/secrets"}
```

## Best Practices

1. **Never hardcode config**.
2. **Use typed settings**.
3. **Fail fast**.
4. **Dev defaults**.
5. **Never commit secrets** (use `.env` in `.gitignore`).
6. **Namespace variables**.
7. **Validate early**.
