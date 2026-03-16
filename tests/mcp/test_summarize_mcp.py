import pytest
from unittest.mock import patch, AsyncMock
from app.mcp.summarize_mcp import create_summarize_mcp

pytestmark = pytest.mark.asyncio


class TestSummarizeMcp:
    @patch("app.mcp.summarize_mcp.summarize_pdf", new_callable=AsyncMock)
    @patch("app.mcp.summarize_mcp.fetch_pdf_from_url", new_callable=AsyncMock)
    async def test_summarize_pdf_url_tool(self, mock_fetch, mock_summarize):
        mock_fetch.return_value = b"fake-pdf"
        mock_summarize.return_value = {
            "summary_markdown": "# Summary\nTest",
            "source": "https://example.com/test.pdf",
            "pages": 2,
        }

        mcp = create_summarize_mcp()

        # Get the tool function directly
        tools = await mcp.list_tools()
        tool_names = [t.name for t in tools]
        assert "summarize_pdf_url" in tool_names

        # Call the tool
        result = await mcp.call_tool(
            "summarize_pdf_url", {"url": "https://example.com/test.pdf"}
        )
        # MCP SDK returns list of content items
        assert len(result) > 0

    async def test_summarize_pdf_text_tool(self):
        mcp = create_summarize_mcp()

        result = await mcp.call_tool(
            "summarize_pdf_text", {"text": "Some test content to summarize"}
        )
        assert len(result) > 0
