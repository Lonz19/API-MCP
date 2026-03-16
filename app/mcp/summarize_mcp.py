"""Summarize MCP Server.

Exposes a 'summarize_pdf' tool that wraps the Summarize API service.
Clients can provide a URL to a PDF and get back a Markdown summary.
"""

from mcp.server.fastmcp import FastMCP
from app.services.summarize_service import fetch_pdf_from_url, summarize_pdf


def create_summarize_mcp() -> FastMCP:
    mcp = FastMCP(
        "Summarize MCP",
        instructions="Summarize PDF documents. Provide a URL to a PDF and get a Markdown summary.",
    )

    @mcp.tool()
    async def summarize_pdf_url(url: str) -> str:
        """Summarize a PDF document from a URL.

        Args:
            url: URL pointing to a PDF file.

        Returns:
            Markdown-formatted summary of the PDF content.
        """
        content = await fetch_pdf_from_url(url)
        result = await summarize_pdf(content, source=url)
        return result["summary_markdown"]

    @mcp.tool()
    async def summarize_pdf_text(text: str) -> str:
        """Generate a summary from raw text content.

        Args:
            text: The text content to summarize.

        Returns:
            Markdown-formatted summary.
        """
        from app.services.summarize_service import generate_summary

        summary = generate_summary(text, page_count=0)
        return summary

    return mcp
