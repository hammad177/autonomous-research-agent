from autonomous_research_agent.agents.state import AgentState


async def planner_node_placeholder(state: AgentState) -> AgentState:
    return {"trace": [f"planner: received goal '{state['goal']}'"]}
