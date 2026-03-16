import logging
from google import genai
from app.core.config import get_settings
from app.core.errors import AppError

logger = logging.getLogger(__name__)


def _get_client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise AppError(
            status_code=503,
            error="gemini_not_configured",
            detail="GEMINI_API_KEY is not set. Configure it in the environment.",
        )
    return genai.Client(api_key=settings.gemini_api_key)


async def generate_content(prompt: str, model: str | None = None) -> dict:
    """Call the Gemini API and return structured response."""
    settings = get_settings()
    model_id = model or settings.gemini_default_model

    try:
        client = _get_client()
        response = await client.aio.models.generate_content(
            model=model_id,
            contents=prompt,
        )

        metadata = {}
        if response.usage_metadata:
            metadata = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "candidates_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
            }

        return {
            "model": model_id,
            "response_text": response.text or "",
            "metadata": metadata,
        }
    except AppError:
        raise
    except Exception as e:
        logger.error("Gemini API call failed: %s", e)
        raise AppError(
            status_code=502,
            error="gemini_api_error",
            detail=f"Gemini API call failed: {e}",
        )
