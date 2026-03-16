import io
import logging
from PyPDF2 import PdfReader
import httpx
from app.core.errors import AppError

logger = logging.getLogger(__name__)


async def extract_pdf_text(file_content: bytes) -> tuple[str, int]:
    """Extract text from PDF bytes. Returns (text, page_count)."""
    try:
        reader = PdfReader(io.BytesIO(file_content))
        pages = len(reader.pages)
        text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
        return text, pages
    except Exception as e:
        logger.error("Failed to extract PDF text: %s", e)
        raise AppError(
            status_code=422,
            error="pdf_extraction_failed",
            detail=f"Could not extract text from PDF: {e}",
        )


async def fetch_pdf_from_url(url: str) -> bytes:
    """Download a PDF from a URL."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content
    except httpx.HTTPError as e:
        logger.error("Failed to fetch PDF from URL %s: %s", url, e)
        raise AppError(
            status_code=422,
            error="pdf_fetch_failed",
            detail=f"Could not fetch PDF from URL: {e}",
        )


def generate_summary(text: str, page_count: int) -> str:
    """Generate a markdown summary from extracted text.

    This is a stub implementation. Replace with an actual summarization
    model or API call (e.g., Gemini, Claude) for production use.
    """
    # Truncate for the stub summary
    preview = text[:500].strip()
    if len(text) > 500:
        preview += "..."

    return (
        f"# Document Summary\n\n"
        f"**Pages processed:** {page_count}\n\n"
        f"## Content Preview\n\n"
        f"{preview}\n\n"
        f"---\n"
        f"*This is a stub summary. Integrate a real summarization model for production use.*"
    )


async def summarize_pdf(file_content: bytes, source: str) -> dict:
    """Full pipeline: extract text from PDF and generate summary."""
    text, pages = await extract_pdf_text(file_content)

    if not text.strip():
        raise AppError(
            status_code=422,
            error="empty_pdf",
            detail="The PDF contains no extractable text.",
        )

    summary = generate_summary(text, pages)
    return {
        "summary_markdown": summary,
        "source": source,
        "pages": pages,
    }
