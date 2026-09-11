from langgraph.types import interrupt
from autonomous_research_agent.agents.state import AgentState


async def draft_approval_node(state: AgentState) -> AgentState:
    decision = interrupt(
        {
            "type": "draft_approval",
            "draft": state["draft"],
        }
    )

    action = decision.get("action", "approve")

    if action == "revise":
        return {
            "draft_status": "revise",
            "draft_feedback": decision.get("feedback", ""),
            "trace": ["human: requested revisions to the draft report"],
        }

    return {
        "draft_status": "approved",
        "trace": ["human: approved the final report"],
    }
