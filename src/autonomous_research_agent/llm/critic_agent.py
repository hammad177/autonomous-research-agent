from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from autonomous_research_agent.config import settings
from autonomous_research_agent.schemas.critic import CriticVerdict

SYSTEM_PROMPT = (
    "You are a critical reviewer evaluating research findings against a "
    "research goal. For each sub-question's findings, judge whether it is "
    "well-sourced, specific, and actually answers the sub-question — not "
    "vague, generic, or unsupported. If ALL findings are solid, return "
    "verdict 'approve' with empty weak_sub_questions. If ANY findings are "
    "weak, contradictory, or insufficiently sourced, return verdict "
    "'needs_more_research', explain why in feedback, and list the EXACT "
    "text of the weak sub-question(s) — copy them exactly as given, do not "
    "paraphrase them."
)


def build_critic_agent() -> Agent:
    model = OpenAIChatModel(
        settings.CHAT_MODEL,
        provider=OpenAIProvider(api_key=settings.OPENAI_API_KEY),
    )
    return Agent(
        model=model,
        output_type=CriticVerdict,
        system_prompt=SYSTEM_PROMPT,
        retries=3,
    )
