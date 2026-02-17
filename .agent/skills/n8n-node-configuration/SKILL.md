---
name: n8n-node-configuration
description: Expert guidance for operation-aware node configuration with property dependencies in n8n.
---

# n8n Node Configuration

## Configuration Philosophy

**Progressive Disclosure**: Start minimal, add complexity as needed.
most configurations need only standard detail, not full schema.

## Core Concepts

### 1. Operation-Aware Configuration

Fields required depend on the `operation` selected.

- **Example (Slack)**: `channel` is required for `post`, but `messageId` is required for `update`.

### 2. Property Dependencies

Fields appear/disappear based on other values (`displayOptions`).

- **Example (HTTP Request)**: `body` field only appears when `sendBody` is `true` AND method is `POST`/`PUT`/`PATCH`.

### 3. Progressive Discovery

Use `get_node` with levels of detail:

1.  **Standard** (Default): `get_node({nodeType: "nodes-base.slack"})` - Covers 95% of use cases.
2.  **Search Properties**: `get_node({mode: "search_properties", propertyQuery: "auth"})` - To find specific fields.
3.  **Full**: `get_node({detail: "full"})` - Complete schema, use sparingly.

## Common Node Patterns

### Resource/Operation Nodes

(Slack, Sheets, Airtable)
Structure: `{ "resource": "...", "operation": "..." }`

- Configure resource and operation first, then check requirements.

### HTTP-Based Nodes

(HTTP Request, Webhook)
Structure: `{ "method": "...", "url": "..." }`

- Dependencies: `sendBody=true` triggers `body` requirement.

### Conditional Logic Nodes

(IF, Switch)
Structure: `{ "conditions": { ... } }`

- Dependencies: Binary operators need `value1` and `value2`. Unary need `value1` + `singleValue: true`.

## Best Practices

- **Start Minimal**: Don't add every optional field.
- **Validate**: Always run `validate_node` before deploying.
- **Check Context**: Re-check requirements when changing operations.
