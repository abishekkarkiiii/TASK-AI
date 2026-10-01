from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ChunkStrategy(str, Enum):
    SENTENCE = "sentence"
    FIXED = "fixed"


class IngestResponse(BaseModel):
    document_id: int
    filename: str
    content_type: str | None
    strategy: ChunkStrategy
    total_chunks: int
    chunk_sizes: list[int]
    embedding_dimension: int


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    content_type: str | None
    strategy: str
    total_chunks: int
    total_characters: int
    created_at: datetime


class SearchResult(BaseModel):
    score: float
    text: str
    filename: str
    chunk_index: int


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    intent: str = "question"
    sources: list[str] = Field(default_factory=list)
    booking_id: int | None = None


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    date: str
    time: str
    created_at: datetime
