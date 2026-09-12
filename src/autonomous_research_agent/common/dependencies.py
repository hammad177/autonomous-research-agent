from functools import lru_cache

from autonomous_research_agent.services.research_service import ResearchService
from autonomous_research_agent.core.extraction import PDFExtractor, URLExtractor
from autonomous_research_agent.repositories.vector_repository import VectorRepository
from autonomous_research_agent.repositories.run_registry_repository import (
    RunRegistryRepository,
)
from autonomous_research_agent.repositories.document_repository import (
    DocumentRepository,
)
from autonomous_research_agent.core.chunking import TextChunker
from autonomous_research_agent.repositories.graph_repository import GraphRepository
from autonomous_research_agent.services.ingestion_service import IngestionService
from autonomous_research_agent.services.graph_service import GraphService
from autonomous_research_agent.services.memory_service import MemoryService
from autonomous_research_agent.config import settings


@lru_cache
def get_vector_repository() -> VectorRepository:
    return VectorRepository()


@lru_cache
def get_graph_repository() -> GraphRepository:
    return GraphRepository()


@lru_cache
def get_graph_service() -> GraphService:
    return GraphService(graph_repo=get_graph_repository())


@lru_cache
def get_memory_service() -> MemoryService:
    return MemoryService()


@lru_cache
def get_document_repository() -> DocumentRepository:
    return DocumentRepository(settings.DOCUMENT_METADATA_PATH)


@lru_cache
def get_run_registry_repository() -> RunRegistryRepository:
    return RunRegistryRepository(settings.RUN_REGISTRY_PATH)


@lru_cache
def get_ingestion_service() -> IngestionService:
    return IngestionService(
        vector_repo=get_vector_repository(),
        document_repo=get_document_repository(),
        pdf_extractor=PDFExtractor(),
        url_extractor=URLExtractor(),
        text_chunker=TextChunker(),
        graph_service=get_graph_service(),
    )


_research_graph = None
_research_service: ResearchService | None = None


def set_research_graph(graph) -> None:
    global _research_graph, _research_service
    _research_graph = graph
    _research_service = ResearchService(graph=graph)


def get_research_graph():
    if _research_graph is None:
        raise RuntimeError(
            "Research graph not initialized — check app startup/lifespan."
        )
    return _research_graph


def get_research_service() -> ResearchService:
    if _research_service is None:
        raise RuntimeError(
            "Research service not initialized — check app startup/lifespan."
        )
    return _research_service
