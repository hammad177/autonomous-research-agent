from fastapi import APIRouter, Depends, HTTPException

from autonomous_research_agent.schemas.research import (
    ResearchStartRequest,
    PlanDecisionRequest,
    ResearchStatusResponse,
)
from autonomous_research_agent.services.research_service import ResearchService
from autonomous_research_agent.common.dependencies import get_research_service
from autonomous_research_agent.common.utils import (
    new_thread_id,
    extract_pending_interrupt,
)

router = APIRouter(prefix="/api/research", tags=["Research"])


def _build_status_response(thread_id: str, result: dict) -> ResearchStatusResponse:
    pending = extract_pending_interrupt(result)
    status = "awaiting_plan_approval" if pending else "completed"
    return ResearchStatusResponse(
        thread_id=thread_id,
        goal=result.get("goal", ""),
        status=status,
        pending_plan=pending,
        draft=result.get("draft"),
        trace=result.get("trace", []),
    )


@router.post("/start", response_model=ResearchStatusResponse)
async def start_research(
    body: ResearchStartRequest,
    service: ResearchService = Depends(get_research_service),
):
    thread_id = new_thread_id()
    result = await service.start(thread_id, body.goal)
    return _build_status_response(thread_id, result)


@router.get("/{thread_id}", response_model=ResearchStatusResponse)
async def get_research_status(
    thread_id: str,
    service: ResearchService = Depends(get_research_service),
):
    status_info = await service.get_status(thread_id)
    status = (
        "awaiting_plan_approval"
        if status_info["pending_plan"]
        else ("in_progress" if status_info["is_paused"] else "completed")
    )
    return ResearchStatusResponse(
        thread_id=thread_id,
        goal=status_info["goal"],
        status=status,
        pending_plan=status_info["pending_plan"],
        draft=status_info["draft"],
        trace=status_info["trace"],
    )


@router.post("/{thread_id}/plan", response_model=ResearchStatusResponse)
async def decide_on_plan(
    thread_id: str,
    body: PlanDecisionRequest,
    service: ResearchService = Depends(get_research_service),
):
    try:
        result = await service.resume_with_plan_decision(
            thread_id, body.model_dump(exclude_none=True)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to resume run: {e}")

    return _build_status_response(thread_id, result)
