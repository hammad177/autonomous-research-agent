from pydantic import BaseModel, Field


class SubQuestion(BaseModel):
    question: str = Field(
        ..., description="A single, concrete, researchable sub-question."
    )
    rationale: str = Field(
        ...,
        description="One short sentence on why this sub-question matters for the overall goal.",
    )


class ResearchPlan(BaseModel):
    sub_questions: list[SubQuestion] = Field(
        ...,
        min_length=3,
        max_length=6,
        description="3 to 6 non-overlapping sub-questions that together cover the research goal.",
    )
