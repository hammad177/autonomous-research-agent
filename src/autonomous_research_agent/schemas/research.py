from pydantic import BaseModel, Field


class ResearchStartRequest(BaseModel):
    goal: str = Field(
        ..., min_length=1, description="The research goal to investigate."
    )


class ResearchRunResponse(BaseModel):
    thread_id: str
    goal: str
    trace: list[str]
    draft: str | None = None
