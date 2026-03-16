import logging
from fastapi import APIRouter, Depends
from app.core.auth import require_api_key
from app.models.gemini import GeminiRequest, GeminiResponse
from app.services.gemini_service import generate_content

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Gemini"])


@router.post(
    "/gemini",
    response_model=GeminiResponse,
    summary="Generate content with Gemini",
    description="Send a prompt to a Google Gemini model and get a response.",
)
async def gemini(
    request: GeminiRequest,
    _api_key: str = Depends(require_api_key),
) -> GeminiResponse:
    result = await generate_content(prompt=request.prompt, model=request.model)
    return GeminiResponse(**result)
