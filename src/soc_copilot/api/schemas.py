"""Pydantic request/response schemas for the API."""
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="User question")


class Source(BaseModel):
    content: str = Field(..., description="Chunk text snippet")
    chunk_id: int = Field(..., description="Position in retrieval result")


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    refused: bool = Field(..., description="True if model refused (out-of-scope)")


class HealthResponse(BaseModel):
    status: str = "ok"
    chunks_indexed: int
