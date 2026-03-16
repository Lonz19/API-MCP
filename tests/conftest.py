import pytest
from httpx import ASGITransport, AsyncClient
from app.core.config import Settings, get_settings
from app.main import create_app

TEST_API_KEY = "test-api-key-12345"


def get_test_settings() -> Settings:
    return Settings(
        app_name="API-MCP-Test",
        app_env="testing",
        debug=True,
        api_key=TEST_API_KEY,
        gemini_api_key="fake-gemini-key",
        gemini_default_model="gemini-3.1-flash-lite-preview",
    )


@pytest.fixture
def app():
    application = create_app()
    application.dependency_overrides[get_settings] = get_test_settings
    return application


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def auth_headers():
    return {"X-API-Key": TEST_API_KEY}
