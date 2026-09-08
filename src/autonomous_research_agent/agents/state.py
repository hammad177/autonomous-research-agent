"""Shared state schema passed between every node in the research graph."""

import operator
from typing import Annotated, TypedDict


class SubQuestion(TypedDict):
    question: str
    rationale: str


class Finding(TypedDict):
    sub_question: str
    content: str
    source: str


class AgentState(TypedDict, total=False):
    goal: str
    sub_questions: list[SubQuestion]
    plan_status: str  # "approved" | "rejected" — set by the human approval node
    planner_feedback: str  # carried back to the planner if the plan is rejected
    findings: Annotated[list[Finding], operator.add]
    draft: str
    revision_count: int
    trace: Annotated[list[str], operator.add]
