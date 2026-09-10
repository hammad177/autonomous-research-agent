from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from autonomous_research_agent.config import settings
from autonomous_research_agent.schemas.report import Report

SYSTEM_PROMPT = (
    "You are a research report writer. Given a research goal and a set of "
    "approved findings (one per sub-question), synthesize them into a "
    "well-organized report. Write one section per sub-question, using the "
    "sub-question as the basis for the section heading (rephrased as a "
    "clear title, not repeated verbatim). Write in clear, professional "
    "prose — do not simply copy the raw finding text, synthesize it. Do "
    "not introduce any facts not present in the given findings. List which "
    "source(s) backed each section based on what's given. Write a short "
    "executive summary covering the overall conclusion across all sections."
)


def build_writer_agent() -> Agent:
    model = OpenAIChatModel(
        settings.CHAT_MODEL,
        provider=OpenAIProvider(api_key=settings.OPENAI_API_KEY),
    )
    return Agent(
        model=model,
        output_type=Report,
        system_prompt=SYSTEM_PROMPT,
        retries=3,
    )
