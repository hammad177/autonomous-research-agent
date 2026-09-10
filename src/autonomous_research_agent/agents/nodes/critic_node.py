from autonomous_research_agent.agents.state import AgentState
from autonomous_research_agent.llm.critic_agent import build_critic_agent
from autonomous_research_agent.common.constants import MAX_REVISION_CYCLES


def make_critic_node():
    agent = build_critic_agent()

    async def critic_node(state: AgentState) -> AgentState:
        revision_count = state.get("revision_count", 0)

        if revision_count >= MAX_REVISION_CYCLES:
            return {
                "critic_verdict": "approve",
                "trace": [
                    f"critic: revision cap ({MAX_REVISION_CYCLES}) reached, forcing approval"
                ],
            }

        findings_text = "\n\n".join(
            f"Sub-question: {f['sub_question']}\nFindings: {f['content']}\nSource used: {f['source']}"
            for f in state["findings"]
        )
        prompt = f"Research goal: {state['goal']}\n\nFindings so far:\n{findings_text}"

        result = await agent.run(prompt)
        verdict = result.output

        if verdict.verdict == "approve":
            return {
                "critic_verdict": "approve",
                "trace": ["critic: approved all findings"],
            }

        return {
            "critic_verdict": "needs_more_research",
            "critic_feedback": verdict.feedback,
            "weak_sub_questions": verdict.weak_sub_questions,
            "revision_count": revision_count + 1,
            "trace": [
                f"critic: flagged {len(verdict.weak_sub_questions)} sub-question(s) "
                f"for revision — {verdict.feedback}"
            ],
        }

    return critic_node
