from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, StreamingResponse

from autonomous_research_agent.schemas.research import (
    ResearchStartRequest,
    PlanDecisionRequest,
    DraftDecisionRequest,
    ResearchStatusResponse,
)
from autonomous_research_agent.services.research_service import ResearchService
from autonomous_research_agent.common.dependencies import get_research_service
from autonomous_research_agent.common.utils import (
    new_thread_id,
    extract_pending_interrupt,
    process_stream_chunk,
)
from autonomous_research_agent.common.sse import format_sse

router = APIRouter(prefix="/api/research", tags=["Research"])


def _build_status_response(thread_id: str, result: dict) -> ResearchStatusResponse:
    pending = extract_pending_interrupt(result)
    pending_plan = None
    pending_draft = None
    status = "completed"

    if pending:
        if pending.get("type") == "plan_approval":
            status = "awaiting_plan_approval"
            pending_plan = pending.get("sub_questions")
        elif pending.get("type") == "draft_approval":
            status = "awaiting_draft_approval"
            pending_draft = pending.get("draft")

    return ResearchStatusResponse(
        thread_id=thread_id,
        goal=result.get("goal", ""),
        status=status,
        pending_plan=pending_plan,
        pending_draft=pending_draft,
        findings=result.get("findings", []),
        critic_verdict=result.get("critic_verdict"),
        revision_count=result.get("revision_count", 0),
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


@router.post("/start/stream")
async def start_research_stream(
    body: ResearchStartRequest,
    service: ResearchService = Depends(get_research_service),
):
    thread_id = new_thread_id()

    async def event_generator():
        yield format_sse("thread", {"thread_id": thread_id})
        async for chunk in service.stream_start(thread_id, body.goal):
            for event in process_stream_chunk(chunk):
                yield format_sse(event["type"], event)
        yield format_sse("done", {"thread_id": thread_id})

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/{thread_id}", response_model=ResearchStatusResponse)
async def get_research_status(
    thread_id: str,
    service: ResearchService = Depends(get_research_service),
):
    status_info = await service.get_status(thread_id)
    pending = status_info.get("pending_interrupt")

    pending_plan = None
    pending_draft = None
    if pending and pending.get("type") == "plan_approval":
        status = "awaiting_plan_approval"
        pending_plan = pending.get("sub_questions")
    elif pending and pending.get("type") == "draft_approval":
        status = "awaiting_draft_approval"
        pending_draft = pending.get("draft")
    else:
        status = "in_progress" if status_info["is_paused"] else "completed"

    return ResearchStatusResponse(
        thread_id=thread_id,
        goal=status_info["goal"],
        status=status,
        pending_plan=pending_plan,
        pending_draft=pending_draft,
        findings=status_info.get("findings", []),
        critic_verdict=status_info.get("critic_verdict"),
        revision_count=status_info.get("revision_count", 0),
        draft=status_info["draft"],
        trace=status_info["trace"],
    )


@router.get("/{thread_id}/report", response_class=PlainTextResponse)
async def get_report_markdown(
    thread_id: str,
    service: ResearchService = Depends(get_research_service),
):
    status_info = await service.get_status(thread_id)
    draft = status_info.get("draft")
    if not draft:
        raise HTTPException(
            status_code=404, detail="Report not yet available for this run."
        )
    return draft


@router.post("/{thread_id}/plan", response_model=ResearchStatusResponse)
async def decide_on_plan(
    thread_id: str,
    body: PlanDecisionRequest,
    service: ResearchService = Depends(get_research_service),
):
    try:
        result = await service.resume_with_decision(
            thread_id, body.model_dump(exclude_none=True)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to resume run: {e}")
    return _build_status_response(thread_id, result)


@router.post("/{thread_id}/plan/stream")
async def decide_on_plan_stream(
    thread_id: str,
    body: PlanDecisionRequest,
    service: ResearchService = Depends(get_research_service),
):
    async def event_generator():
        async for chunk in service.stream_resume(
            thread_id, body.model_dump(exclude_none=True)
        ):
            for event in process_stream_chunk(chunk):
                yield format_sse(event["type"], event)
        yield format_sse("done", {"thread_id": thread_id})

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/{thread_id}/draft", response_model=ResearchStatusResponse)
async def decide_on_draft(
    thread_id: str,
    body: DraftDecisionRequest,
    service: ResearchService = Depends(get_research_service),
):
    try:
        result = await service.resume_with_decision(
            thread_id, body.model_dump(exclude_none=True)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to resume run: {e}")
    return _build_status_response(thread_id, result)


@router.post("/{thread_id}/draft/stream")
async def decide_on_draft_stream(
    thread_id: str,
    body: DraftDecisionRequest,
    service: ResearchService = Depends(get_research_service),
):
    async def event_generator():
        async for chunk in service.stream_resume(
            thread_id, body.model_dump(exclude_none=True)
        ):
            for event in process_stream_chunk(chunk):
                yield format_sse(event["type"], event)
        yield format_sse("done", {"thread_id": thread_id})

    return StreamingResponse(event_generator(), media_type="text/event-stream")
