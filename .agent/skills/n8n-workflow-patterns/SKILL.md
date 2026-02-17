---
name: n8n-workflow-patterns
description: Proven architectural patterns for building robust n8n workflows.
---

# n8n Workflow Patterns

## The 5 Core Patterns

### 1. Webhook Processing (Most Common)

**Receive → Process → Output**

- **Use case**: Integrations, slash commands, form submissions.
- **Pattern**: Webhook → Validate → Transform → Respond.

### 2. HTTP API Integration

**Fetch → Transform → Store**

- **Use case**: Data pipelines, sync with 3rd party services.
- **Pattern**: Trigger → HTTP Request → Transform → Action → Error Handler.

### 3. Database Operations

**Read/Write/Sync**

- **Use case**: ETL, database sync.
- **Pattern**: Schedule → Query → Transform → Write → Verify.

### 4. AI Agent Workflow

**Trigger → Agent → Output**

- **Use case**: Conversational AI, tool-using agents.
- **Pattern**: Trigger → AI Agent (Model + Tools + Memory).

### 5. Scheduled Tasks

**Schedule → Execute → Log**

- **Use case**: Recurring reports, cleanup.

## Data Flow Patterns

1.  **Linear**: Simple single path.
2.  **Branching**: `IF` node for conditional paths.
3.  **Parallel**: Split flow, then `Merge`.
4.  **Loop**: `Split In Batches` for large datasets.
5.  **Error Handler**: Separate flow attached to "Error Trigger".

## Common Gotchas

1.  **Webhook Data**: Access via `$json.body`, not top-level.
2.  **Multiple Items**: Nodes run for _each_ item. Use `Execute Once` if needed.
3.  **Auth**: Use Credentials store, not hardcoded params.
4.  **Order**: Use "Connection-based" execution order (v1).
