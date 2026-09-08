from autonomous_research_agent.agents.state import AgentState


async def writer_node_placeholder(state: AgentState) -> AgentState:
    return {
        "trace": ["writer: produced draft (placeholder)"],
        "draft": f"[placeholder draft for goal: {state['goal']}]",
    }
