import io
import pytest
from PyPDF2 import PdfWriter
from app.services.summarize_service import (
    extract_pdf_text,
    generate_summary,
    summarize_pdf,
)
from app.core.errors import AppError


def _make_pdf_bytes(text: str = "Hello world. This is a test PDF.") -> bytes:
    """Create a minimal PDF with text for testing."""
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    # PdfWriter doesn't easily add text, so we test with a real-ish PDF
    # For unit tests, we'll test generate_summary directly and mock extract_pdf_text
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


class TestGenerateSummary:
    def test_short_text(self):
        result = generate_summary("Short text", page_count=1)
        assert "# Document Summary" in result
        assert "Short text" in result
        assert "**Pages processed:** 1" in result

    def test_long_text_truncated(self):
        long_text = "A" * 1000
        result = generate_summary(long_text, page_count=5)
        assert "..." in result
        assert "**Pages processed:** 5" in result

    def test_empty_text(self):
        result = generate_summary("", page_count=0)
        assert "# Document Summary" in result


class TestExtractPdfText:
    @pytest.mark.asyncio
    async def test_valid_pdf(self):
        pdf_bytes = _make_pdf_bytes()
        text, pages = await extract_pdf_text(pdf_bytes)
        assert pages >= 1
        assert isinstance(text, str)

    @pytest.mark.asyncio
    async def test_invalid_pdf(self):
        with pytest.raises(AppError) as exc_info:
            await extract_pdf_text(b"not a pdf")
        assert exc_info.value.status_code == 422


class TestSummarizePdf:
    @pytest.mark.asyncio
    async def test_empty_pdf_raises(self):
        # A blank PDF with no text content
        pdf_bytes = _make_pdf_bytes()
        # Blank pages have no text, so this should raise
        with pytest.raises(AppError) as exc_info:
            await summarize_pdf(pdf_bytes, source="test")
        assert exc_info.value.error == "empty_pdf"
