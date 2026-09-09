from functools import lru_cache

from autonomous_research_agent.agents.graph import build_research_graph
from autonomous_research_agent.services.research_service import ResearchService
from autonomous_research_agent.core.extraction import PDFExtractor, URLExtractor
from autonomous_research_agent.repositories.vector_repository import VectorRepository
from autonomous_research_agent.repositories.document_repository import (
    DocumentRepository,
)
from autonomous_research_agent.core.chunking import TextChunker
from autonomous_research_agent.services.ingestion_service import IngestionService
from autonomous_research_agent.config import settings


@lru_cache
def get_research_graph():
    return build_research_graph()


@lru_cache
def get_research_service() -> ResearchService:
    return ResearchService(graph=get_research_graph())


@lru_cache
def get_vector_repository() -> VectorRepository:
    return VectorRepository()


@lru_cache
def get_document_repository() -> DocumentRepository:
    return DocumentRepository(settings.DOCUMENT_METADATA_PATH)


@lru_cache
def get_ingestion_service() -> IngestionService:
    return IngestionService(
        vector_repo=get_vector_repository(),
        document_repo=get_document_repository(),
        pdf_extractor=PDFExtractor(),
        url_extractor=URLExtractor(),
        text_chunker=TextChunker(),
    )
