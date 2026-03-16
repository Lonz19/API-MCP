import pytest
from unittest.mock import patch, AsyncMock

pytestmark = pytest.mark.asyncio


class TestSummarizeEndpoint:
    async def test_missing_auth(self, client):
        response = await client.post("/api/v1/summarize")
        assert response.status_code == 401

    async def test_invalid_auth(self, client):
        response = await client.post(
            "/api/v1/summarize",
            headers={"X-API-Key": "wrong-key"},
        )
        assert response.status_code == 403

    async def test_no_input(self, client, auth_headers):
        response = await client.post("/api/v1/summarize", headers=auth_headers)
        assert response.status_code == 400

    @patch("app.api.v1.summarize.summarize_pdf", new_callable=AsyncMock)
    async def test_file_upload(self, mock_summarize, client, auth_headers):
        mock_summarize.return_value = {
            "summary_markdown": "# Summary\nTest content",
            "source": "upload:test.pdf",
            "pages": 3,
        }

        files = {"file": ("test.pdf", b"fake-pdf-content", "application/pdf")}
        response = await client.post(
            "/api/v1/summarize",
            headers=auth_headers,
            files=files,
        )

        assert response.status_code == 200
        data = response.json()
        assert "summary_markdown" in data
        assert data["pages"] == 3

    @patch("app.api.v1.summarize.fetch_pdf_from_url", new_callable=AsyncMock)
    @patch("app.api.v1.summarize.summarize_pdf", new_callable=AsyncMock)
    async def test_url_input(self, mock_summarize, mock_fetch, client, auth_headers):
        mock_fetch.return_value = b"fake-pdf-content"
        mock_summarize.return_value = {
            "summary_markdown": "# Summary\nURL content",
            "source": "https://example.com/test.pdf",
            "pages": 5,
        }

        response = await client.post(
            "/api/v1/summarize",
            headers=auth_headers,
            data={"url": "https://example.com/test.pdf"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "https://example.com/test.pdf"


class TestHealthEndpoint:
    async def test_health_no_auth_required(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
