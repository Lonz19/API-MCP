from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import get_settings
from app.core.errors import AppError, app_error_handler
from app.core.logging import CorrelationIdMiddleware, setup_logging
from app.api.v1.router import v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging("DEBUG" if get_settings().debug else "INFO")
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        description="Template API server hosting HTTP APIs and MCP servers",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Middleware
    application.add_middleware(CorrelationIdMiddleware)

    # Error handlers
    application.add_exception_handler(AppError, app_error_handler)

    # API routes
    application.include_router(v1_router)

    # Health check (unauthenticated)
    @application.get("/health", tags=["Health"])
    async def health():
        return {"status": "ok", "app": settings.app_name}

    # Mount MCP servers
    from app.mcp.summarize_mcp import create_summarize_mcp
    from app.mcp.deep_search_mcp import create_deep_search_mcp

    summarize_mcp = create_summarize_mcp()
    deep_search_mcp = create_deep_search_mcp()

    application.mount("/mcp/summarize", summarize_mcp.streamable_http_app())
    application.mount("/mcp/deep-search", deep_search_mcp.streamable_http_app())

    return application


app = create_app()
