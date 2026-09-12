from fastapi import APIRouter, Depends

from autonomous_research_agent.repositories.run_registry_repository import (
    RunRegistryRepository,
)
from autonomous_research_agent.services.research_service import ResearchService
from autonomous_research_agent.schemas.run import RunSummary, RunListResponse
from autonomous_research_agent.common.dependencies import (
    get_run_registry_repository,
    get_research_service,
)

router = APIRouter(prefix="/api/runs", tags=["Runs"])


@router.get("", response_model=RunListResponse)
async def list_runs(
    registry: RunRegistryRepository = Depends(get_run_registry_repository),
    service: ResearchService = Depends(get_research_service),
):
    records = registry.list_all()
    summaries = []

    for record in records:
        status_info = await service.get_status(record.thread_id)
        pending = status_info.get("pending_interrupt")

        if pending and pending.get("type") == "plan_approval":
            status = "awaiting_plan_approval"
        elif pending and pending.get("type") == "draft_approval":
            status = "awaiting_draft_approval"
        elif status_info["is_paused"]:
            status = "in_progress"
        else:
            status = "completed"

        summaries.append(
            RunSummary(
                thread_id=record.thread_id,
                goal=record.goal,
                created_at=record.created_at,
                status=status,
            )
        )

    return RunListResponse(runs=summaries)
