import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.gemini_service import generate_content
from app.core.errors import AppError


class TestGenerateContent:
    @pytest.mark.asyncio
    @patch("app.services.gemini_service._get_client")
    async def test_successful_generation(self, mock_get_client):
        # Mock the Gemini response
        mock_response = MagicMock()
        mock_response.text = "This is a test response"
        mock_response.usage_metadata = MagicMock()
        mock_response.usage_metadata.prompt_token_count = 10
        mock_response.usage_metadata.candidates_token_count = 20
        mock_response.usage_metadata.total_token_count = 30

        mock_client = MagicMock()
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await generate_content(
            prompt="Hello", model="gemini-3.1-flash-lite-preview"
        )

        assert result["model"] == "gemini-3.1-flash-lite-preview"
        assert result["response_text"] == "This is a test response"
        assert result["metadata"]["total_tokens"] == 30

    @pytest.mark.asyncio
    @patch("app.services.gemini_service._get_client")
    async def test_uses_default_model(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.text = "Response"
        mock_response.usage_metadata = None

        mock_client = MagicMock()
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await generate_content(prompt="Hello")

        assert result["model"] == "gemini-3.1-flash-lite-preview"
        assert result["metadata"] == {}

    @pytest.mark.asyncio
    @patch("app.services.gemini_service._get_client")
    async def test_api_error_raises_app_error(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.aio.models.generate_content = AsyncMock(
            side_effect=RuntimeError("API unavailable")
        )
        mock_get_client.return_value = mock_client

        with pytest.raises(AppError) as exc_info:
            await generate_content(prompt="Hello")
        assert exc_info.value.status_code == 502

    @pytest.mark.asyncio
    async def test_missing_api_key_raises(self):
        with patch("app.services.gemini_service.get_settings") as mock_settings:
            mock_settings.return_value.gemini_api_key = ""
            with pytest.raises(AppError) as exc_info:
                await generate_content(prompt="Hello")
            assert exc_info.value.status_code == 503
