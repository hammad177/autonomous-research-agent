import hashlib
import uuid
from pathlib import Path

from autonomous_research_agent.core.extraction import PDFExtractor, URLExtractor
from autonomous_research_agent.core.chunking import TextChunker
from autonomous_research_agent.repositories.vector_repository import VectorRepository
from autonomous_research_agent.repositories.document_repository import (
    DocumentRepository,
)
from autonomous_research_agent.services.graph_service import GraphService
from autonomous_research_agent.schemas.document import DocumentMetadata, IngestResponse


class IngestionService:
    def __init__(
        self,
        vector_repo: VectorRepository,
        document_repo: DocumentRepository,
        pdf_extractor: PDFExtractor,
        url_extractor: URLExtractor,
        text_chunker: TextChunker,
        graph_service: GraphService,
    ):
        self.vector_repo = vector_repo
        self.document_repo = document_repo
        self.pdf_extractor = pdf_extractor
        self.url_extractor = url_extractor
        self.chunker = text_chunker
        self.graph_service = graph_service

    @staticmethod
    def _hash_text(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _ingest(self, text: str, source: str, source_type: str) -> IngestResponse:
        if not text.strip():
            raise ValueError(f"No extractable text found in '{source}'.")

        content_hash = self._hash_text(text)
        existing = self.document_repo.find_by_hash(content_hash)
        if existing:
            return IngestResponse(
                id=existing.id,
                source=source,
                status="skipped_duplicate",
                chunk_count=existing.chunk_count,
            )

        # Same source, different content -> replace the old version
        stale = self.document_repo.find_by_source(source)
        if stale and stale.content_hash != content_hash:
            self.vector_repo.delete_by_document_id(stale.id)
            self.document_repo.delete(stale.id)
            self.graph_service.graph_repo.delete_by_source(source)

        chunks = self.chunker.chunk(text)
        document_id = str(uuid.uuid4())
        self.vector_repo.add_chunks(chunks, source=source, document_id=document_id)

        # Extract on the full text, not per chunk, so relationships spanning
        # multiple sentences/paragraphs aren't lost to chunk boundaries.
        self.graph_service.extract_and_store(text, source=source)

        metadata = DocumentMetadata(
            id=document_id,
            filename=source,
            source_type=source_type,
            source=source,
            content_hash=content_hash,
            chunk_count=len(chunks),
        )
        self.document_repo.save(metadata)

        return IngestResponse(
            id=document_id, source=source, status="ingested", chunk_count=len(chunks)
        )

    def ingest_pdf(self, file_path: Path, original_filename: str) -> IngestResponse:
        text = self.pdf_extractor.extract(file_path)
        return self._ingest(text, source=original_filename, source_type="pdf")

    def ingest_url(self, url: str) -> IngestResponse:
        text = self.url_extractor.extract(url)
        return self._ingest(text, source=url, source_type="url")
