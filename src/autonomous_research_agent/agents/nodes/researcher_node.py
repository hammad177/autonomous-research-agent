from langchain_core.messages import HumanMessage, ToolMessage

from autonomous_research_agent.agents.state import AgentState
from autonomous_research_agent.llm.researcher_agent import build_researcher_agent
from autonomous_research_agent.repositories.vector_repository import VectorRepository


def _extract_tools_used(messages: list) -> list[str]:
    return sorted({m.name for m in messages if isinstance(m, ToolMessage) and m.name})


def make_researcher_node(vector_repo: VectorRepository):
    agent = build_researcher_agent(vector_repo)

    async def researcher_node(state: AgentState) -> AgentState:
        sq = state["current_sub_question"]
        question = sq["question"]

        result = await agent.ainvoke({"messages": [HumanMessage(content=question)]})
        messages = result["messages"]
        final_answer = messages[-1].content
        tools_used = _extract_tools_used(messages)
        source = ", ".join(tools_used) if tools_used else "general_knowledge"

        finding = {"sub_question": question, "content": final_answer, "source": source}

        return {
            "findings": [finding],
            "trace": [f"researcher: answered '{question}' using [{source}]"],
        }

    return researcher_node
