---
name: n8n-mcp-tools-expert
description: Master guide for using n8n-mcp MCP server tools to build workflows, discover nodes, and validate configuration.
---

# n8n MCP Tools Expert

## Tool Categories

1. **Node Discovery**: Finding the right node and parameters.
2. **Configuration Validation**: Checking node setup before running.
3. **Workflow Management**: Creating, editing, and activating workflows.

## Most Used Tools

- `search_nodes`: Find nodes by keyword.
- `get_node`: Get details (params, docs) for a node.
- `validate_node`: Check node config.
- `n8n_create_workflow`: Start a new workflow.
- `n8n_update_partial_workflow`: Edit existing workflow.

## Common Workflows

### 1. Finding the Right Node

```javascript
// 1. Search
search_nodes({ query: "slack" });
// 2. Get Details
get_node({ nodeType: "nodes-base.slack" });
// 3. Get Docs
get_node({ nodeType: "nodes-base.slack", mode: "docs" });
```

### 2. Validating Configuration

```javascript
// 1. Validate
validate_node({
  nodeType: "nodes-base.slack",
  config: { resource: "channel", operation: "create" },
  profile: "runtime",
});
// 2. If valid: false, fix errors and repeat.
```

### 3. Building Workflows (Iterative)

```javascript
// 1. Create
n8n_create_workflow({name: "My Workflow", ...})
// 2. Edit
n8n_update_partial_workflow({id: "workflow-id", operations: [...]})
// 3. Validate
n8n_validate_workflow({id: "workflow-id"})
// 4. Activate
n8n_update_partial_workflow({id: "...", operations: [{type: "activateWorkflow"}]})
```

## Critical Concepts

### Node Type Formats

1. **Search/Validate Format** (Short): `nodes-base.slack`
   - Used by: `search_nodes`, `get_node`, `validate_node`.
2. **Workflow Format** (Full): `n8n-nodes-base.slack`
   - Used by: `n8n_create_workflow`, `n8n_update_partial_workflow`.

### Common Mistakes

- Using the wrong node type format.
- Not using `intent` parameter in updates.
- Ignoring validation errors.

## Best Practices

- **Search first**: Don't guess node names.
- **Validate often**: Check config before adding to workflow.
- **Iterate**: Build workflows step-by-step, not all at once.
- **Use templates**: `search_templates` and `n8n_deploy_template` can save time.
