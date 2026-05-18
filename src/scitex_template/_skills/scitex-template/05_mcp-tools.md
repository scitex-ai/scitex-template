---
description: |
  [TOPIC] Mcp Tools
  [DETAILS] scitex-template exposes its CLI surface as MCP tools so agents can enumerate and clone templates without shell access.
tags: [scitex-template-mcp-tools, scitex-template, scitex-package]
---

# MCP tools

The legacy unified scitex MCP server exposes these tools (prefix-stripped
so Claude + other clients can discover them):

| tool | action | equivalent CLI |
|---|---|---|
| `template_clone_template` | Populate a target from a template id | `scitex-template clone <id> <target>` |
| `template_get_code_template` | Return the source of a named code snippet | — (Python-API only) |
| `template_list_code_templates` | List the 14 code snippet IDs | — |
| `template_list_git_strategies` | List the four `git_strategy` values with descriptions | — |

## Invocation

Once registered (e.g. via the unified scitex MCP server running under
Claude Code), tools appear as `mcp__scitex__template_*`:

```python
# Agent perspective — call is made by Claude via MCP
mcp__scitex__template_clone_template(template_id="research", project_dir="./my-proj")
```

Under the hood each tool imports `scitex_template` and calls the Python
API described in [02_python-api.md](02_python-api.md).

## Adding new MCP tools

Tools live in `src/scitex_template/_mcp/handlers.py`. To add a tool:

1. Add a handler function to `HANDLERS` in `handlers.py`.
2. Register it in the unified MCP server's tool list.
3. Document it here.

## Running a standalone MCP server

```bash
scitex-template-mcp     # starts the legacy scitex-template-only MCP server
```

Prefer the unified scitex MCP server (`scitex serve`) over the standalone
when possible — it exposes every scitex-* package's tools in one process.
