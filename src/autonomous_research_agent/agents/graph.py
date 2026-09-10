from langgraph.graph import StateGraph, END
from langgraph.types import Send

from autonomous_research_agent.agents.state import AgentState
from autonomous_research_agent.agents.nodes.planner_node import make_planner_node
from autonomous_research_agent.agents.nodes.plan_approval_node import plan_approval_node
from autonomous_research_agent.agents.nodes.researcher_node import make_researcher_node
from autonomous_research_agent.agents.nodes.critic_node import make_critic_node
from autonomous_research_agent.agents.nodes.writer_node import make_writer_node
from autonomous_research_agent.agents.nodes.memory_writer_node import (
    make_memory_writer_node,
)
from autonomous_research_agent.agents.checkpointer import get_checkpointer
from autonomous_research_agent.repositories.vector_repository import VectorRepository
from autonomous_research_agent.services.graph_service import GraphService
from autonomous_research_agent.services.memory_service import MemoryService


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


def route_after_critic(state: AgentState):
    if state.get("critic_verdict") != "needs_more_research":
        return "writer"

    weak = state.get("weak_sub_questions", [])
    feedback = state.get("critic_feedback", "")
    sub_questions_by_text = {sq["question"]: sq for sq in state["sub_questions"]}

    sends = [
        Send(
            "researcher",
            {
                "current_sub_question": sub_questions_by_text[q],
                "critic_feedback": feedback,
            },
        )
        for q in weak
        if q in sub_questions_by_text
    ]

    # Safety net: if the critic named sub-questions that don't exactly
    # match the original text, fall back to writer rather than dropping
    # the run into a dead end with zero Sends dispatched.
    return sends if sends else "writer"


def build_research_graph(
    vector_repo: VectorRepository,
    graph_service: GraphService,
    memory_service: MemoryService,
):
    graph = StateGraph(AgentState)

    graph.add_node("planner", make_planner_node())
    graph.add_node("plan_approval", plan_approval_node)
    graph.add_node("researcher", make_researcher_node(vector_repo, graph_service))
    graph.add_node("critic", make_critic_node())
    graph.add_node("writer", make_writer_node())
    graph.add_node("memory_writer", make_memory_writer_node(memory_service))

    graph.set_entry_point("planner")
    graph.add_edge("planner", "plan_approval")
    graph.add_conditional_edges(
        "plan_approval", route_after_plan_approval, ["planner", "researcher"]
    )
    graph.add_edge("researcher", "critic")
    graph.add_conditional_edges("critic", route_after_critic, ["researcher", "writer"])
    graph.add_edge("writer", "memory_writer")
    graph.add_edge("memory_writer", END)

    return graph.compile(checkpointer=get_checkpointer())
