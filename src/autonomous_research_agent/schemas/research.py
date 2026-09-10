from typing import Literal
from pydantic import BaseModel, Field

from autonomous_research_agent.schemas.plan import SubQuestion


class ResearchStartRequest(BaseModel):
    goal: str = Field(
        ..., min_length=1, description="The research goal to investigate."
    )


class PlanDecisionRequest(BaseModel):
    action: Literal["approve", "edit", "reject"]
    sub_questions: list[SubQuestion] | None = Field(
        default=None,
        description="Required when action is 'edit' — the corrected sub-questions.",
    )
    feedback: str | None = Field(
        default=None,
        description="Optional when action is 'reject' — guidance for the planner's next attempt.",
    )


class Finding(BaseModel):
    sub_question: str
    content: str
    source: str


class ResearchStatusResponse(BaseModel):
    thread_id: str
    goal: str
    status: Literal["awaiting_plan_approval", "in_progress", "completed"]
    pending_plan: dict | None = None
    findings: list[Finding] = []
    critic_verdict: str | None = None
    revision_count: int = 0
    draft: str | None = None
    trace: list[str] = []
