---
name: python-packaging
description: Comprehensive guide to creating, building, and publishing Python packages using modern standards (pyproject.toml) and best practices.
---

# Python Packaging

## When to Use This Skill

- Creating Python libraries for distribution
- Building command-line tools with entry points
- Publishing packages to PyPI or private repositories
- Setting up Python project structure
- Creating installable packages with dependencies
- Building wheels and source distributions
- Versioning and releasing Python packages
- Creating namespace packages
- Implementing package metadata and classifiers

## Core Concepts

### 1. Package Structure

- **Source layout**: `src/package_name/` (recommended)
- **Flat layout**: `package_name/` (simpler but less flexible)
- **Package metadata**: `pyproject.toml` (standard), `setup.py`, or `setup.cfg`
- **Distribution formats**: wheel (`.whl`) and source distribution (`.tar.gz`)

### 2. Modern Packaging Standards

- **PEP 517/518**: Build system requirements
- **PEP 621**: Metadata in `pyproject.toml`
- **PEP 660**: Editable installs

### 3. Build Backends

- **setuptools**: Traditional, widely used
- **hatchling**: Modern, opinionated
- **flit**: Lightweight, for pure Python
- **poetry**: Dependency management + packaging

### 4. Distribution

- **PyPI**: Python Package Index (public)
- **TestPyPI**: Testing before production
- **Private repositories**: JFrog, AWS CodeArtifact, etc.

## Quick Start

### Minimal Package Structure

```text
my-package/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── my_package/
│       ├── __init__.py
│       └── module.py
└── tests/
    └── test_module.py
```

### Minimal pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-package"
version = "0.1.0"
description = "A short description"
authors = [{name = "Your Name", email = "you@example.com"}]
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black>=22.0",
]
```

## Package Structure Patterns

### Pattern 1: Source Layout (Recommended)

```text
my-package/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── core.py
│       ├── utils.py
│       └── py.typed  # For type hints
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── test_utils.py
└── docs/
    └── index.md
```

**Configuration for source layout:**

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

### Pattern 2: Flat Layout

```text
my-package/
├── pyproject.toml
├── My_package/
│   ├── __init__.py
│   └── module.py
```

_Easier for scripts, but prone to import errors during testing._

## Complete pyproject.toml Examples

### Pattern 4: Full-Featured usage

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-awesome-package"
version = "1.0.0"
description = "An awesome Python package"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "you@example.com"},
]
keywords = ["example", "package", "awesome"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]
dependencies = [
    "requests>=2.28.0,<3.0.0",
    "click>=8.0.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
docs = [
    "sphinx>=5.0.0",
]

[project.urls]
Homepage = "https://github.com/username/my-awesome-package"
Repository = "https://github.com/username/my-awesome-package"
"Bug Tracker" = "https://github.com/username/my-awesome-package/issues"

[project.scripts]
my-cli = "my_package.cli:main"

[tool.setuptools.packages.find]
where = ["src"]
```

### Pattern 5: Dynamic Versioning

```toml
[build-system]
requires = ["setuptools>=61.0", "setuptools-scm>=8.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-package"
dynamic = ["version"]

[tool.setuptools_scm]
write_to = "src/my_package/_version.py"
```

In `__init__.py`:

```python
from importlib.metadata import version
__version__ = version("my-package")
```

## Command-Line Interface (CLI) Patterns

### Pattern 6: CLI with Click

```python
# src/my_package/cli.py
import click

@click.group()
@click.version_option()
def cli():
    """My awesome CLI tool."""
    pass

@cli.command()
@click.argument("name")
@click.option("--greeting", default="Hello", help="Greeting to use")
def greet(name: str, greeting: str):
    """Greet someone."""
    click.echo(f"{greeting}, {name}!")

def main():
    cli()

if __name__ == "__main__":
    main()
```

Register in `pyproject.toml`:

```toml
[project.scripts]
my-tool = "my_package.cli:main"
```

## Building and Publishing

### Pattern 8: Build Package Locally

```bash
pip install build twine
python -m build
twine check dist/*
```

### Pattern 9: Publishing to PyPI

```bash
# TestPyPI
twine upload --repository testpypi dist/*

# Production PyPI
twine upload dist/*
```

## Advanced Patterns

### Pattern 11: Including Data Files

```toml
[tool.setuptools.package-data]
my_package = [
    "data/*.json",
    "templates/*.html",
    "py.typed",
]
```

Access in code:

```python
from importlib.resources import files
data = files("my_package").joinpath("data/config.json").read_text()
```

## Testing Installation

### Pattern 16: Editable Install

```bash
# Install in development mode
pip install -e .
pip install -e ".[dev]"
```

## Documentation

### Pattern 18: README.md Template

````markdown
# My Package

[![PyPI version](https://badge.fury.io/py/my-package.svg)](https://pypi.org/project/my-package/)

Brief description of your package.

## Installation

```bash
pip install my-package
```
````

```

## Best Practices
1. **Use `src` layout** to avoid import issues.
2. **Use `pyproject.toml`** for all configuration (PEP 621).
3. **Pin dependencies** with ranges (e.g., `>=1.0,<2.0`).
4. **Use Semantic Versioning**.
5. **Include a `LICENSE` file**.
6. **Test with `tox` or multiple python versions**.
7. **Automate publishing** with GitHub Actions.
```
