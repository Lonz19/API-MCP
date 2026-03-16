from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    url: str | None = Field(
        default=None,
        description="URL to a PDF file to summarize. Provide either url or upload a file.",
    )


class SummarizeResponse(BaseModel):
    summary_markdown: str = Field(
        description="Markdown-formatted summary of the PDF content"
    )
    source: str = Field(description="Source of the PDF: 'upload' or the URL")
    pages: int = Field(description="Number of pages processed")
