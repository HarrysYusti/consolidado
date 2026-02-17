---
name: n8n-code-javascript
description: Expert guidance for writing JavaScript code in n8n Code nodes.
---

# n8n JavaScript Code Node

## Essential Rules

1.  **Mode**: Use "Run Once for All Items" (Recommended).
2.  **Access**: `$input.all()`, `$input.first()`, or `$input.item`.
3.  **Return**: Must return `[{json: {...}}]`.
4.  **Webhooks**: Data is under `$json.body`.

## Quick Start Template

```javascript
const items = $input.all();
return items.map((item) => ({
  json: {
    ...item.json,
    processed: true,
    timestamp: new Date().toISOString(),
  },
}));
```

## Data Access Patterns

### 1. `$input.all()` (Batch)

Most common. Process all items from previous node.

```javascript
const allItems = $input.all();
const valid = allItems.filter((i) => i.json.status === "active");
return valid.map((i) => ({ json: i.json }));
```

### 2. `$input.first()` (Single)

For API responses or singleton data.

```javascript
const data = $input.first().json;
return [{ json: { result: process(data) } }];
```

### 3. `$node` (References)

Access data from other nodes.

```javascript
const webhookData = $node["Webhook"].json;
return [{ json: { data: webhookData } }];
```

## Common Mistakes

1.  **Missing Return**: Always return an array.
2.  **Wrong Access**: `$json.field` behaves differently in Code node. Use `$input`.
3.  **Obj vs Array**: Return `[{json: ...}]`, not `{json: ...}`.
4.  **Null Checks**: Use optional chaining `item.json?.user?.email`.

## Helpers

- **`$helpers.httpRequest`**: Make API calls from code.
- **`DateTime` (Luxon)**: Date manipulation.
- **`$jmespath`**: JSON query language.
