from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from autonomous_research_agent.config import settings
from autonomous_research_agent.schemas.plan import ResearchPlan

SYSTEM_PROMPT = (
    "You are a research planning agent. Given a research goal, break it down "
    "into 3 to 6 concrete, individually researchable sub-questions that together "
    "fully cover the goal. Each sub-question must be specific enough to research "
    "independently, and the set of sub-questions should not overlap with each "
    "other. For each sub-question, give one short sentence explaining why it "
    "matters to the overall goal."
)


def build_planner_agent() -> Agent:
    model = OpenAIChatModel(
        settings.CHAT_MODEL,
        provider=OpenAIProvider(api_key=settings.OPENAI_API_KEY),
    )
    return Agent(
        model=model,
        output_type=ResearchPlan,
        system_prompt=SYSTEM_PROMPT,
        retries=3,
    )
