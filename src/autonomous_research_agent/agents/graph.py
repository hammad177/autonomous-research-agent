from langgraph.graph import StateGraph, END
from langgraph.types import Send

from autonomous_research_agent.agents.state import AgentState
from autonomous_research_agent.agents.nodes.planner_node import make_planner_node
from autonomous_research_agent.agents.nodes.plan_approval_node import plan_approval_node
from autonomous_research_agent.agents.nodes.researcher_node import make_researcher_node
from autonomous_research_agent.agents.nodes.critic_node import critic_node_placeholder
from autonomous_research_agent.agents.nodes.writer_node import writer_node_placeholder
from autonomous_research_agent.agents.checkpointer import get_checkpointer
from autonomous_research_agent.repositories.vector_repository import VectorRepository


def route_after_plan_approval(state: AgentState):
    if state["plan_status"] == "rejected":
        return "planner"

    # One Send per sub-question = one parallel branch. Each branch runs
    # the "researcher" node with only {"current_sub_question": sq} as its
    # input — not the full graph state — and whatever it returns gets
    # merged back via the findings/trace reducers once every branch finishes.
    return [
        Send("researcher", {"current_sub_question": sq})
        for sq in state["sub_questions"]
    ]


def build_research_graph(vector_repo: VectorRepository):
    graph = StateGraph(AgentState)

    graph.add_node("planner", make_planner_node())
    graph.add_node("plan_approval", plan_approval_node)
    graph.add_node("researcher", make_researcher_node(vector_repo))
    graph.add_node("critic", critic_node_placeholder)
    graph.add_node("writer", writer_node_placeholder)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "plan_approval")
    graph.add_conditional_edges(
        "plan_approval",
        route_after_plan_approval,
        ["planner", "researcher"],
    )
    graph.add_edge("researcher", "critic")
    graph.add_edge("critic", "writer")
    graph.add_edge("writer", END)

    return graph.compile(checkpointer=get_checkpointer())
