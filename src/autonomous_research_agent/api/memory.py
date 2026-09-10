from fastapi import APIRouter, Depends, Query

from autonomous_research_agent.services.memory_service import MemoryService
from autonomous_research_agent.schemas.memory import MemoryListResponse
from autonomous_research_agent.common.dependencies import get_memory_service

router = APIRouter(prefix="/api/memory", tags=["Memory"])


@router.get("", response_model=MemoryListResponse)
async def list_memories(memory_service: MemoryService = Depends(get_memory_service)):
    return MemoryListResponse(memories=memory_service.get_all())


@router.get("/search", response_model=MemoryListResponse)
async def search_memories(
    q: str = Query(..., min_length=1),
    memory_service: MemoryService = Depends(get_memory_service),
):
    return MemoryListResponse(memories=memory_service.search(q))
