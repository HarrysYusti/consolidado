---
name: mcp-builder
description: Discover and install skills for AI agents.
---

# mcp-builder

## Overview

Create MCP (Model Context Protocol) servers that enable LLMs to interact with external services.

## High-Level Workflow

### Phase 1: Deep Research and Planning

1.  **Understand Modern MCP Design**:
    - Balance API coverage with specialized workflow tools.
    - Use clear, descriptive tool names (e.g., `github_create_issue`).
    - Ensure actionable error messages.
2.  **Study Protocol & Frameworks**:
    - **TypeScript (Recommended)**: Best for broad usage, static typing.
    - **Python**: Good alternative.
    - Transport: Streamable HTTP for remote, stdio for local.
3.  **Plan Implementation**:
    - Review target API documentation.
    - Select tools to implement.

### Phase 2: Implementation

1.  **Project Structure**: Follow language-specific guides (see References).
2.  **Core Infrastructure**: Shared utilities for API clients, error handling, logging.
3.  **Implement Tools**:
    - **Input Schema**: Zod (TS) or Pydantic (Python).
    - **Output Schema**: Define structured data returns.
    - **Annotations**: `readOnlyHint`, `is_destructive`, etc.

### Phase 3: Review and Test

1.  **Code Quality**: DRY, consistent error handling, full type coverage.
2.  **Build and Test**:
    - TS: `npm run build`, `npx @modelcontextprotocol/inspector`
    - Python: `python -m py_compile`, `npx @modelcontextprotocol/inspector`

### Phase 4: Create Evaluations

Create 10 complex, realistic, read-only questions to test the server.
Format:

```xml
<evaluation>
  <qa_pair>
    <question>...</question>
    <answer>...</answer>
  </qa_pair>
</evaluation>
```

## Reference

- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
