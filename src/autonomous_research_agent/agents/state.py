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
    sub-question rather than appending a duplicate alongside it.

    This matters starting in Phase 7: when the critic sends a sub-question
    back for more research, the researcher re-runs and produces a new
    finding for that same sub-question. Plain operator.add (used through
    Phase 6) would keep BOTH the old, rejected finding and the new one
    side by side in the list — silently corrupting the final report with
    a stale, already-rejected finding. This reducer makes re-research
    correctly supersede the old result instead.
    """
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
    trace: Annotated[list[str], operator.add]
