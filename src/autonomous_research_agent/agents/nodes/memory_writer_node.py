from autonomous_research_agent.agents.state import AgentState
from autonomous_research_agent.services.memory_service import MemoryService


def make_memory_writer_node(memory_service: MemoryService):
    async def memory_writer_node(state: AgentState) -> AgentState:
        memory_service.store_run_summary(state["goal"], state["findings"])
        return {"trace": ["memory: stored this run's findings for future recall"]}

    return memory_writer_node
