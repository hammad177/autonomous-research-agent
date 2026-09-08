from autonomous_research_agent.agents.state import AgentState


async def critic_node_placeholder(state: AgentState) -> AgentState:
    return {"trace": ["critic: reviewed (placeholder, always approves)"]}
