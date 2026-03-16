import logging
from fastapi import APIRouter, Depends, File, Form, UploadFile
from app.core.auth import require_api_key
from app.core.errors import AppError
from app.models.summarize import SummarizeResponse
from app.services.summarize_service import fetch_pdf_from_url, summarize_pdf

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Summarize"])


@router.post(
    "/summarize",
    response_model=SummarizeResponse,
    summary="Summarize a PDF document",
    description="Upload a PDF file or provide a URL to a PDF. Returns a Markdown-formatted summary.",
)
async def summarize(
    _api_key: str = Depends(require_api_key),
    file: UploadFile | None = File(default=None, description="PDF file to summarize"),
    url: str | None = Form(default=None, description="URL to a PDF file"),
) -> SummarizeResponse:
    if file is None and url is None:
        raise AppError(
            status_code=400,
            error="missing_input",
            detail="Provide either a PDF file upload or a URL.",
        )

    if file is not None:
        content = await file.read()
        source = f"upload:{file.filename}"
    else:
        content = await fetch_pdf_from_url(url)
        source = url

    result = await summarize_pdf(content, source)
    return SummarizeResponse(**result)
