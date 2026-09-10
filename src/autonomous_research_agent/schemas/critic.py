from typing import Literal
from pydantic import BaseModel, Field


class CriticVerdict(BaseModel):
    verdict: Literal["approve", "needs_more_research"] = Field(
        ...,
        description="Overall verdict on whether the findings sufficiently answer the research goal.",
    )
    feedback: str = Field(
        ...,
        description="Explanation of the verdict — what's missing, weak, or contradictory.",
    )
    weak_sub_questions: list[str] = Field(
        default_factory=list,
        description="Exact text of sub-questions whose findings are weak, under-sourced, or contradictory. Empty if verdict is 'approve'.",
    )
