import pytest
from unittest.mock import patch, AsyncMock

pytestmark = pytest.mark.asyncio


class TestGeminiEndpoint:
    async def test_missing_auth(self, client):
        response = await client.post(
            "/api/v1/gemini",
            json={"prompt": "Hello"},
        )
        assert response.status_code == 401

    async def test_invalid_auth(self, client):
        response = await client.post(
            "/api/v1/gemini",
            json={"prompt": "Hello"},
            headers={"X-API-Key": "wrong-key"},
        )
        assert response.status_code == 403

    async def test_missing_prompt(self, client, auth_headers):
        response = await client.post(
            "/api/v1/gemini",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 422

    @patch("app.api.v1.gemini.generate_content", new_callable=AsyncMock)
    async def test_successful_generation(self, mock_generate, client, auth_headers):
        mock_generate.return_value = {
            "model": "gemini-3.1-flash-lite-preview",
            "response_text": "Hello! How can I help you?",
            "metadata": {"total_tokens": 25},
        }

        response = await client.post(
            "/api/v1/gemini",
            json={"prompt": "Hello"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "gemini-3.1-flash-lite-preview"
        assert data["response_text"] == "Hello! How can I help you?"
        assert data["metadata"]["total_tokens"] == 25

    @patch("app.api.v1.gemini.generate_content", new_callable=AsyncMock)
    async def test_custom_model(self, mock_generate, client, auth_headers):
        mock_generate.return_value = {
            "model": "gemini-2.0-flash",
            "response_text": "Response",
            "metadata": {},
        }

        response = await client.post(
            "/api/v1/gemini",
            json={"prompt": "Hello", "model": "gemini-2.0-flash"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        mock_generate.assert_called_once_with(prompt="Hello", model="gemini-2.0-flash")
