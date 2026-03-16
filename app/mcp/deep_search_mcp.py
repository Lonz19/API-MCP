"""Deep Search MCP Server.

Combines the Summarize API and Gemini API to perform deeper analysis.
Accepts a document (URL or text) and a query, summarizes the document,
then uses Gemini to analyze and answer questions about it.
"""

from mcp.server.fastmcp import FastMCP
from app.services.summarize_service import (
    fetch_pdf_from_url,
    generate_summary,
    summarize_pdf,
)
from app.services.gemini_service import generate_content


def create_deep_search_mcp() -> FastMCP:
    mcp = FastMCP(
        "Deep Search MCP",
        instructions=(
            "Deep analysis of documents. Provide a PDF URL or text along with a query. "
            "The document is summarized, then Gemini provides analysis based on your query."
        ),
    )

    @mcp.tool()
    async def deep_search_url(url: str, query: str) -> dict:
        """Perform deep search on a PDF document from a URL.

        Summarizes the PDF, then uses Gemini to analyze the summary
        and answer the provided query.

        Args:
            url: URL pointing to a PDF file.
            query: The question or analysis request about the document.

        Returns:
            Dictionary with summary_markdown, gemini_analysis, and metadata.
        """
        # Step 1: Fetch and summarize the PDF
        content = await fetch_pdf_from_url(url)
        summary_result = await summarize_pdf(content, source=url)
        summary_md = summary_result["summary_markdown"]

        # Step 2: Use Gemini to analyze
        analysis_prompt = (
            f"Based on the following document summary, answer this question: {query}\n\n"
            f"Document Summary:\n{summary_md}"
        )
        gemini_result = await generate_content(prompt=analysis_prompt)

        return {
            "summary_markdown": summary_md,
            "gemini_analysis": gemini_result["response_text"],
            "source": url,
            "pages": summary_result["pages"],
            "gemini_model": gemini_result["model"],
            "metadata": gemini_result["metadata"],
        }

    @mcp.tool()
    async def deep_search_text(text: str, query: str) -> dict:
        """Perform deep search on provided text content.

        Summarizes the text, then uses Gemini to analyze and answer the query.

        Args:
            text: The text content to analyze.
            query: The question or analysis request about the text.

        Returns:
            Dictionary with summary_markdown, gemini_analysis, and metadata.
        """
        # Step 1: Summarize the text
        summary_md = generate_summary(text, page_count=0)

        # Step 2: Use Gemini to analyze
        analysis_prompt = (
            f"Based on the following text summary, answer this question: {query}\n\n"
            f"Text Summary:\n{summary_md}"
        )
        gemini_result = await generate_content(prompt=analysis_prompt)

        return {
            "summary_markdown": summary_md,
            "gemini_analysis": gemini_result["response_text"],
            "source": "text_input",
            "pages": 0,
            "gemini_model": gemini_result["model"],
            "metadata": gemini_result["metadata"],
        }

    return mcp
