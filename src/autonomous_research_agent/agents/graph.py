from langgraph.graph import StateGraph, END

from autonomous_research_agent.agents.state import AgentState
from autonomous_research_agent.agents.nodes.planner_node import make_planner_node
from autonomous_research_agent.agents.nodes.researcher_node import (
    researcher_node_placeholder,
)
from autonomous_research_agent.agents.nodes.critic_node import critic_node_placeholder
from autonomous_research_agent.agents.nodes.writer_node import writer_node_placeholder
from autonomous_research_agent.agents.checkpointer import get_checkpointer


def build_research_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", make_planner_node())
    graph.add_node("researcher", researcher_node_placeholder)
    graph.add_node("critic", critic_node_placeholder)
    graph.add_node("writer", writer_node_placeholder)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "critic")
    graph.add_edge("critic", "writer")
    graph.add_edge("writer", END)

    return graph.compile(checkpointer=get_checkpointer())
