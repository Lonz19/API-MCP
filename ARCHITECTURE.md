# Architecture Guide

## Overview

This project is a **FastAPI-based template** that hosts both HTTP APIs and MCP (Model Context Protocol) servers in a single application. It is designed for maintainability, testability, and easy extension using Claude Code.

## Layered Architecture

```
┌─────────────────────────────────────────┐
│         Routes / MCP Handlers           │  ← Thin: validate input, call service, return response
├─────────────────────────────────────────┤
│            Service Layer                │  ← Business logic, external API calls
├─────────────────────────────────────────┤
│           Models (Pydantic)             │  ← Request/response schemas, validation
├─────────────────────────────────────────┤
│          Core (config, auth, logging)   │  ← Cross-cutting concerns
└─────────────────────────────────────────┘
```

### Separation of Concerns

- **Routes** (`app/api/v1/`): Receive HTTP requests, validate via Pydantic models, call services, return responses. No business logic here.
- **MCP Handlers** (`app/mcp/`): Define MCP tools. Each tool calls service functions directly (not HTTP round-trips).
- **Services** (`app/services/`): All business logic. Called by both routes and MCP handlers. This is the key sharing layer.
- **Models** (`app/models/`): Pydantic models for request/response validation.
- **Core** (`app/core/`): Configuration, authentication, logging, error handling.

## API Patterns

### Versioning

All HTTP API endpoints are versioned under `/api/v1/`. When breaking changes are needed, create a new version (`/api/v2/`) while keeping the old one available.

### Authentication

Every API endpoint (except `/health`) requires an `X-API-Key` header. The key is validated against the `API_KEY` environment variable via the `require_api_key` dependency.

```python
from app.core.auth import require_api_key

@router.post("/my-endpoint")
async def my_endpoint(_api_key: str = Depends(require_api_key)):
    ...
```

### Async-First

All endpoints use `async def`. External I/O (HTTP calls, file reads) uses async libraries (`httpx`, async file operations).

### Error Handling

Use `AppError` for expected errors. These are caught by the global error handler and returned as structured JSON:

```json
{
  "error": "error_code",
  "detail": "Human-readable description",
  "status_code": 422
}
```

### Request/Response Models

Every endpoint defines Pydantic models for input and output:

```python
class MyRequest(BaseModel):
    field: str = Field(description="Description for OpenAPI docs")

class MyResponse(BaseModel):
    result: str
```

### Logging & Observability

- Every request gets a correlation ID (from `X-Request-ID` header or auto-generated).
- All log entries include the correlation ID for tracing.
- Use `logging.getLogger(__name__)` in every module.

## MCP Server Patterns

### Structure

Each MCP server is a function that returns a `FastMCP` instance:

```python
from mcp.server.fastmcp import FastMCP

def create_my_mcp() -> FastMCP:
    mcp = FastMCP("My MCP", instructions="What this MCP does")

    @mcp.tool()
    async def my_tool(arg: str) -> str:
        """Tool docstring becomes the tool description."""
        result = await some_service_function(arg)
        return result

    return mcp
```

### Mounting

MCP servers are mounted on the FastAPI app in `app/main.py`:

```python
mcp = create_my_mcp()
app.mount("/mcp/my-server", mcp.streamable_http_app())
```

### Tool Registration

- Use `@mcp.tool()` decorator
- Docstrings become tool descriptions
- Type hints become parameter schemas
- Tools call service functions from `app/services/`, never HTTP endpoints

### Transport

MCP servers use **Streamable HTTP** transport (the modern MCP standard). Clients connect via HTTP POST to the mount path.

## Testing Strategy

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Business logic tests (services)
├── integration/             # HTTP endpoint tests (FastAPI TestClient)
└── mcp/                     # MCP tool execution tests
```

### Unit Tests

Test service functions in isolation. Mock external dependencies (HTTP clients, Gemini API).

### Integration Tests

Test HTTP endpoints using `httpx.AsyncClient`. Verify:
- Authentication enforcement
- Input validation
- Response schemas
- Error responses

### MCP Tests

Test MCP tools by calling `mcp.call_tool()` directly. Mock service layer dependencies.

### Naming Convention

- `test_{service_name}_service.py` for unit tests
- `test_{api_name}_api.py` for integration tests
- `test_{mcp_name}_mcp.py` for MCP tests

## Security Best Practices

1. **Never commit secrets** — use `.env` files (gitignored) and environment variables
2. **API key validation** on all endpoints by default
3. **Input validation** via Pydantic models (automatic)
4. **Dependency injection** for auth — easy to extend to OAuth2/JWT later
5. **No hardcoded credentials** — all config from environment

## Adding a New API

1. Create models in `app/models/new_api.py`
2. Create service in `app/services/new_api_service.py`
3. Create route in `app/api/v1/new_api.py`
4. Add router to `app/api/v1/router.py`
5. Add unit tests in `tests/unit/test_new_api_service.py`
6. Add integration tests in `tests/integration/test_new_api_api.py`
7. Update `README.md` with docs and code snippets

## Adding a New MCP Server

1. Create `app/mcp/new_mcp.py` using the pattern above
2. Mount in `app/main.py`
3. Add MCP tests in `tests/mcp/test_new_mcp.py`
4. Update `README.md`
