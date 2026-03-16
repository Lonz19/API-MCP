from pydantic import BaseModel, Field


class GeminiRequest(BaseModel):
    prompt: str = Field(description="The prompt to send to the Gemini model")
    model: str | None = Field(
        default=None,
        description="Gemini model ID. Defaults to GEMINI_DEFAULT_MODEL from config.",
    )


class GeminiResponse(BaseModel):
    model: str = Field(description="The model ID that was used")
    response_text: str = Field(description="The text response from Gemini")
    metadata: dict = Field(
        default_factory=dict, description="Additional metadata (e.g., token usage)"
    )
