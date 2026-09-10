from pydantic import BaseModel, Field


class Relationship(BaseModel):
    subject: str = Field(..., description="The source entity.")
    predicate: str = Field(
        ..., description="The relationship type, e.g. 'works_at', 'located_in'."
    )
    object: str = Field(..., description="The target entity.")


class ExtractedGraph(BaseModel):
    relationships: list[Relationship] = Field(
        ..., description="Relationships between entities found in the text."
    )


class GraphFact(BaseModel):
    subject: str
    predicate: str
    object: str
    source: str
