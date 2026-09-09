from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class DocumentMetadata(BaseModel):
    id: str
    filename: str
    source_type: str  # "pdf" or "url"
    source: str
    content_hash: str
    chunk_count: int
    ingested_at: datetime = Field(default_factory=datetime.utcnow)


class IngestResponse(BaseModel):
    id: str
    source: str
    status: str  # "ingested", "skipped_duplicate"
    chunk_count: int


class DocumentListResponse(BaseModel):
    documents: list[DocumentMetadata]


class RetrievedChunk(BaseModel):
    text: str
    source: str
    chunk_index: int
    score: float


class URLIngestRequest(BaseModel):
    url: HttpUrl
