from fastapi import APIRouter, Depends

from autonomous_research_agent.schemas.research import (
    ResearchStartRequest,
    ResearchRunResponse,
)
from autonomous_research_agent.common.dependencies import get_research_graph
from autonomous_research_agent.common.utils import new_thread_id

router = APIRouter(prefix="/api/research", tags=["Research"])


@router.post("/start", response_model=ResearchRunResponse)
async def start_research(
    body: ResearchStartRequest,
    graph=Depends(get_research_graph),
):
    thread_id = new_thread_id()
    config = {"configurable": {"thread_id": thread_id}}

    result = await graph.ainvoke({"goal": body.goal}, config=config)

    return ResearchRunResponse(
        thread_id=thread_id,
        goal=result.get("goal", body.goal),
        trace=result.get("trace", []),
        draft=result.get("draft"),
    )
