---
name: n8n-code-python
description: Expert guidance for writing Python code in n8n Code nodes (Beta).
---

# n8n Python Code Node (Beta)

## ⚠️ Important: JavaScript First

Use JavaScript for 95% of use cases. Only use Python when:

- You need specific Python standard library functions.
- You're significantly more comfortable with Python syntax.
- You're doing data transformations better suited to Python.

**Limitations**: No external libraries (no requests, pandas, numpy). Standard library only.

## Quick Start

```python
# Basic template for Python Code nodes
# items = _input.all() gets all items from previous node
items = _input.all()
processed = []

for item in items:
    # Always return a list of dictionaries with "json" key
    processed.append({
        "json": {
            **item["json"],
            "processed": True,
            "timestamp": _now.isoformat()
        }
    })

return processed
```

## Essential Rules

1. Access data: `_input.all()`, `_input.first()`, or `_input.item`.
2. **CRITICAL**: Must return `[{"json": {...}}]` format.
3. **CRITICAL**: Webhook data is under `_json["body"]` (not `_json` directly).
4. No external libraries.

## Data Access Patterns

### Pattern 1: `_input.all()` - Most Common

Use for batch processing, filtering, aggregation.

```python
all_items = _input.all()
valid = [item for item in all_items if item["json"].get("status") == "active"]
return [{"json": item["json"]} for item in valid]
```

### Pattern 2: `_input.first()`

Use for single object processing.

```python
first_item = _input.first()
data = first_item["json"]
return [{"json": {"result": process(data)}}]
```

### Pattern 3: `_input.item`

Use only in "Run Once for Each Item" mode.

```python
item = _input.item
return [{"json": {**item["json"], "checked": True}}]
```

## Common Mistakes

1. **Wrong Webhook Access**: Use `_json["body"]["field"]`, not `_json["field"]`.
2. **Importing Libraries**: `import pandas` will fail. Use standard lib only (`json`, `datetime`, `re`, `math`, `statistics`).
3. **Bad Return Format**: Must be list of dicts with "json" key. `return [{"data": ...}]` is WRONG.
4. **Empty Return**: Always return something, even empty list `[]`.

## Best Practices

1. Use `.get()` for dictionary access to avoid KeyErrors.
2. Handle `None` explicitly.
3. Use List Comprehensions for filtering.
4. Debug with `print()` (visible in browser console/n8n logs).
