from mcp.server.fastmcp import FastMCP

from autonomous_research_agent.common.dependencies import (
    get_research_service,
    get_run_registry_repository,
)
from autonomous_research_agent.common.utils import (
    new_thread_id,
    extract_pending_interrupt,
)

mcp = FastMCP("autonomous-research-agent")


def _summarize_result(thread_id: str, result: dict) -> dict:
    pending = extract_pending_interrupt(result)
    status = "completed"
    pending_plan = None
    pending_draft = None

    if pending:
        if pending.get("type") == "plan_approval":
            status = "awaiting_plan_approval"
            pending_plan = pending.get("sub_questions")
        elif pending.get("type") == "draft_approval":
            status = "awaiting_draft_approval"
            pending_draft = pending.get("draft")

    return {
        "thread_id": thread_id,
        "goal": result.get("goal", ""),
        "status": status,
        "pending_plan": pending_plan,
        "pending_draft": pending_draft,
        "critic_verdict": result.get("critic_verdict"),
        "revision_count": result.get("revision_count", 0),
        "trace": result.get("trace", []),
    }


@mcp.tool()
async def start_research(goal: str) -> dict:
    """Starts a new research run for the given goal. The run pauses for
    plan approval before any research happens — call approve_plan with
    the returned thread_id to continue."""
    service = get_research_service()
    registry = get_run_registry_repository()

    thread_id = new_thread_id()
    registry.record(thread_id, goal)
    result = await service.start(thread_id, goal)
    return _summarize_result(thread_id, result)


@mcp.tool()
async def approve_plan(
    thread_id: str, action: str = "approve", feedback: str | None = None
) -> dict:
    """Resolves a paused plan-approval checkpoint. action must be one of
    'approve', 'reject', or 'edit'. Pass feedback when rejecting, to
    guide the planner's next attempt."""
    service = get_research_service()
    decision = {"action": action}
    if feedback:
        decision["feedback"] = feedback

    result = await service.resume_with_decision(thread_id, decision)
    return _summarize_result(thread_id, result)


@mcp.tool()
async def approve_draft(
    thread_id: str, action: str = "approve", feedback: str | None = None
) -> dict:
    """Resolves a paused draft-approval checkpoint. action must be
    'approve' or 'revise'. Pass feedback when requesting a revision."""
    service = get_research_service()
    decision = {"action": action}
    if feedback:
        decision["feedback"] = feedback

    result = await service.resume_with_decision(thread_id, decision)
    return _summarize_result(thread_id, result)


@mcp.tool()
async def get_report(thread_id: str) -> str:
    """Returns the rendered Markdown report for a completed (or still
    in-progress) research run."""
    service = get_research_service()
    status_info = await service.get_status(thread_id)
    draft = status_info.get("draft")
    return draft or "No report available yet for this run."


@mcp.tool()
async def list_runs() -> list[dict]:
    """Lists every research run started so far, with its current status —
    useful for finding a thread_id to resume or inspect."""
    service = get_research_service()
    registry = get_run_registry_repository()

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
            {
                "thread_id": record.thread_id,
                "goal": record.goal,
                "created_at": record.created_at.isoformat(),
                "status": status,
            }
        )

    return summaries
