from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    provider: str = Field(..., description="LLM provider: openai, anthropic, gemini, mistral")
    model: Optional[str] = Field(default=None, description="Override default model for the provider")
    collections: list[str] = Field(default=["bundled"], description="Collections to search")


class Citation(BaseModel):
    id: int
    title: str
    snippet: str       # truncated preview for the card
    full_text: str     # full chunk text for the modal
    source: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
