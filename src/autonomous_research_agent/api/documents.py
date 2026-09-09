import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query

from autonomous_research_agent.services.ingestion_service import IngestionService
from autonomous_research_agent.repositories.document_repository import (
    DocumentRepository,
)
from autonomous_research_agent.repositories.vector_repository import VectorRepository
from autonomous_research_agent.schemas.document import (
    IngestResponse,
    DocumentListResponse,
    RetrievedChunk,
    URLIngestRequest,
)
from autonomous_research_agent.common.dependencies import (
    get_ingestion_service,
    get_document_repository,
    get_vector_repository,
)
from autonomous_research_agent.config import settings

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload", response_model=IngestResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest_path = upload_dir / file.filename

    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        return ingestion_service.ingest_pdf(dest_path, original_filename=file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/url", response_model=IngestResponse)
async def ingest_url(
    body: URLIngestRequest,
    ingestion_service: IngestionService = Depends(get_ingestion_service),
):
    try:
        return ingestion_service.ingest_url(str(body.url))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch URL: {e}")


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    document_repo: DocumentRepository = Depends(get_document_repository),
):
    return DocumentListResponse(documents=document_repo.list_all())


@router.get("/search", response_model=list[RetrievedChunk])
async def search_documents(
    q: str = Query(..., min_length=1),
    top_k: int = Query(default=5, ge=1, le=20),
    vector_repo: VectorRepository = Depends(get_vector_repository),
):
    results = vector_repo.hybrid_search(q, top_k=top_k)
    return [RetrievedChunk(**r) for r in results]
