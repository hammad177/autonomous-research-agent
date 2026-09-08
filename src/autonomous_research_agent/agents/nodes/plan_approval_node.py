from langgraph.types import interrupt
from autonomous_research_agent.agents.state import AgentState


async def plan_approval_node(state: AgentState) -> AgentState:
    decision = interrupt(
        {
            "type": "plan_approval",
            "sub_questions": state["sub_questions"],
        }
    )

    action = decision.get("action", "approve")

    if action == "edit":
        return {
            "sub_questions": decision.get("sub_questions", state["sub_questions"]),
            "plan_status": "approved",
            "trace": ["human: edited and approved the research plan"],
        }

    if action == "reject":
        return {
            "plan_status": "rejected",
            "planner_feedback": decision.get("feedback", ""),
            "trace": ["human: rejected the plan, sending back to planner"],
        }

    return {
        "plan_status": "approved",
        "trace": ["human: approved the research plan as-is"],
    }
