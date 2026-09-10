from pydantic import BaseModel, Field


class ReportSection(BaseModel):
    heading: str = Field(
        ..., description="Section heading, based on the sub-question it answers."
    )
    content: str = Field(
        ...,
        description="Well-written prose synthesizing the findings for this section.",
    )
    sources: list[str] = Field(
        ..., description="Which tools/sources backed this section's content."
    )


class Report(BaseModel):
    title: str = Field(
        ..., description="A concise title for the overall research goal."
    )
    summary: str = Field(
        ...,
        description="A short executive summary (2-4 sentences) of the overall findings.",
    )
    sections: list[ReportSection] = Field(
        ..., description="One section per researched sub-question."
    )
