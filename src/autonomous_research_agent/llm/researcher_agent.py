from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from autonomous_research_agent.config import settings
from autonomous_research_agent.repositories.vector_repository import VectorRepository
from autonomous_research_agent.tools.calculator_tool import calculator
from autonomous_research_agent.tools.web_search_tool import build_web_search_tool
from autonomous_research_agent.tools.knowledge_base_tool import (
    build_knowledge_base_tool,
)

RESEARCHER_SYSTEM_PROMPT = (
    "You are a research agent answering one specific sub-question. Choose "
    "whichever tool(s) fit the question: use the knowledge base for anything "
    "possibly covered by the user's own uploaded documents, web search for "
    "current or general external information, and the calculator only for "
    "numeric computation. You may use more than one tool if needed. Give a "
    "clear, well-sourced final answer."
)


def build_researcher_agent(vector_repo: VectorRepository):
    llm_model = ChatOpenAI(
        model=settings.CHAT_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0.2
    )
    tools = [
        build_knowledge_base_tool(vector_repo),
        build_web_search_tool(),
        calculator,
    ]
    return create_agent(
        model=llm_model, tools=tools, system_prompt=RESEARCHER_SYSTEM_PROMPT
    )
