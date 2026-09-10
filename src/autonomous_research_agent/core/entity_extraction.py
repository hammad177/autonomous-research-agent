from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from autonomous_research_agent.config import settings
from autonomous_research_agent.schemas.graph import ExtractedGraph

EXTRACTION_PROMPT = (
    "Extract relationships between named entities (people, organizations, "
    "products, technologies, places) from the text below. Keep entity names "
    "short and consistent (e.g. always 'Anthropic', never mixing 'Anthropic' "
    "and 'Anthropic Inc.'). Only extract relationships explicitly stated or "
    "clearly implied — do not speculate. If none exist, return an empty list."
)


class EntityExtractor:
    def __init__(self):
        llm = ChatOpenAI(
            model=settings.CHAT_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0
        )
        self.structured_llm = llm.with_structured_output(ExtractedGraph)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", EXTRACTION_PROMPT),
                ("human", "{text}"),
            ]
        )
        self.chain = self.prompt | self.structured_llm

    def extract(self, text: str) -> ExtractedGraph:
        return self.chain.invoke({"text": text})
