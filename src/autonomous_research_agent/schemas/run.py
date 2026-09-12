from datetime import datetime
from pydantic import BaseModel


class RunSummary(BaseModel):
    thread_id: str
    goal: str
    created_at: datetime
    status: str


class RunListResponse(BaseModel):
    runs: list[RunSummary]
