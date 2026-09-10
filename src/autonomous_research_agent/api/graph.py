from fastapi import APIRouter, Depends, Query

from autonomous_research_agent.repositories.graph_repository import GraphRepository
from autonomous_research_agent.common.dependencies import get_graph_repository

router = APIRouter(prefix="/api/graph", tags=["Graph"])


@router.get("/entities")
async def list_entities(graph_repo: GraphRepository = Depends(get_graph_repository)):
    return {"entities": graph_repo.list_entities()}


@router.get("/related")
async def related(
    entity: str = Query(...),
    graph_repo: GraphRepository = Depends(get_graph_repository),
):
    return {"facts": graph_repo.find_related(entity)}
