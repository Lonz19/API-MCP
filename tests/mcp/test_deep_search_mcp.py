import pytest
from unittest.mock import patch, AsyncMock
from app.mcp.deep_search_mcp import create_deep_search_mcp

pytestmark = pytest.mark.asyncio


class TestDeepSearchMcp:
    @patch("app.mcp.deep_search_mcp.generate_content", new_callable=AsyncMock)
    @patch("app.mcp.deep_search_mcp.summarize_pdf", new_callable=AsyncMock)
    @patch("app.mcp.deep_search_mcp.fetch_pdf_from_url", new_callable=AsyncMock)
    async def test_deep_search_url_tool(self, mock_fetch, mock_summarize, mock_gemini):
        mock_fetch.return_value = b"fake-pdf"
        mock_summarize.return_value = {
            "summary_markdown": "# Summary\nTest doc",
            "source": "https://example.com/doc.pdf",
            "pages": 3,
        }
        mock_gemini.return_value = {
            "model": "gemini-3.1-flash-lite-preview",
            "response_text": "The document discusses testing patterns.",
            "metadata": {"total_tokens": 50},
        }

        mcp = create_deep_search_mcp()

        tools = await mcp.list_tools()
        tool_names = [t.name for t in tools]
        assert "deep_search_url" in tool_names

        result = await mcp.call_tool(
            "deep_search_url",
            {"url": "https://example.com/doc.pdf", "query": "What is this about?"},
        )
        assert len(result) > 0

    @patch("app.mcp.deep_search_mcp.generate_content", new_callable=AsyncMock)
    async def test_deep_search_text_tool(self, mock_gemini):
        mock_gemini.return_value = {
            "model": "gemini-3.1-flash-lite-preview",
            "response_text": "Analysis of the text content.",
            "metadata": {"total_tokens": 30},
        }

        mcp = create_deep_search_mcp()

        result = await mcp.call_tool(
            "deep_search_text",
            {
                "text": "Some content about AI and testing",
                "query": "What topics are covered?",
            },
        )
        assert len(result) > 0
