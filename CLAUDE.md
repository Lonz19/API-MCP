# CLAUDE.md - Instructions for Claude Code

## Project Overview
This is a FastAPI template for hosting HTTP APIs and MCP servers. It deploys to Replit via GitHub.

## Key Commands
- Run app: `uvicorn app.main:app --reload`
- Run tests: `pytest tests/ -v --cov=app --cov-report=term-missing`
- Lint: `ruff check app/ tests/`
- Format: `ruff format app/ tests/`

## Architecture Rules
- **APIs** go in `app/api/v1/` — one file per API resource
- **MCP servers** go in `app/mcp/` — one file per MCP server
- **Business logic** goes in `app/services/` — routes and MCPs call services, not the other way around
- **Pydantic models** go in `app/models/` — one file per domain
- **Config** is in `app/core/config.py` — all settings come from environment variables

## When Adding a New API
1. Create Pydantic models in `app/models/`
2. Create service in `app/services/`
3. Create route in `app/api/v1/` with `async def` endpoints
4. Register the router in `app/api/v1/router.py`
5. Add unit test in `tests/unit/`
6. Add integration test in `tests/integration/`
7. Update README.md with endpoint docs, Python + JS examples

## When Adding a New MCP Server
1. Create MCP server file in `app/mcp/`
2. Use the `mcp` SDK's `FastMCP` class
3. Register tools that call services from `app/services/`
4. Mount the MCP app in `app/main.py`
5. Add MCP test in `tests/mcp/`
6. Update README.md

## Testing Conventions
- Test files mirror source: `app/services/foo.py` -> `tests/unit/test_foo_service.py`
- API tests use `httpx.AsyncClient` with the FastAPI app
- MCP tests mock service dependencies
- All tests must pass before merge; coverage minimum is 80%

## Auth
- All API endpoints require `X-API-Key` header
- Key is validated against `API_KEY` environment variable
- Health check (`GET /health`) is unauthenticated
