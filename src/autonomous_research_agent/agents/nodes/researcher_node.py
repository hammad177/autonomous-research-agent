from langchain_core.messages import HumanMessage, ToolMessage

from autonomous_research_agent.agents.state import AgentState
from autonomous_research_agent.llm.researcher_agent import build_researcher_agent
from autonomous_research_agent.repositories.vector_repository import VectorRepository


def _extract_tools_used(messages: list) -> list[str]:
    return sorted({m.name for m in messages if isinstance(m, ToolMessage) and m.name})


def make_researcher_node(vector_repo: VectorRepository):
    agent = build_researcher_agent(vector_repo)

    async def researcher_node(state: AgentState) -> AgentState:
        findings = []
        trace = []

        for sq in state["sub_questions"]:
            question = sq["question"]
            result = await agent.ainvoke({"messages": [HumanMessage(content=question)]})
            messages = result["messages"]
            final_answer = messages[-1].content
            tools_used = _extract_tools_used(messages)
            source = ", ".join(tools_used) if tools_used else "general_knowledge"

            findings.append(
                {
                    "sub_question": question,
                    "content": final_answer,
                    "source": source,
                }
            )
            trace.append(f"researcher: answered '{question}' using [{source}]")

        return {"findings": findings, "trace": trace}

    return researcher_node
