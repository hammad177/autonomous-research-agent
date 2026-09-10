import operator
from typing import Annotated, TypedDict


class SubQuestion(TypedDict):
    question: str
    rationale: str


class Finding(TypedDict):
    sub_question: str
    content: str
    source: str


def merge_findings(existing: list[Finding], new: list[Finding]) -> list[Finding]:
    """Merges new findings in, REPLACING any existing finding for the same
    sub-question rather than appending a duplicate alongside it."""
    merged = {f["sub_question"]: f for f in existing}
    for f in new:
        merged[f["sub_question"]] = f
    return list(merged.values())


class AgentState(TypedDict, total=False):
    goal: str
    sub_questions: list[SubQuestion]
    plan_status: str  # "approved" | "rejected" — set by the human approval node
    planner_feedback: str  # carried back to the planner if the plan is rejected
    current_sub_question: (
        SubQuestion  # only set within a single parallel research branch
    )
    critic_feedback: str  # per-branch, passed into a re-research Send payload
    findings: Annotated[list[Finding], merge_findings]
    critic_verdict: str
    weak_sub_questions: list[str]
    draft: str
    revision_count: int
    draft: str  # the rendered Markdown version of the report
    report: (
        dict  # the structured Report, as a dict (JSON-serializable for checkpointing)
    )
    trace: Annotated[list[str], operator.add]
