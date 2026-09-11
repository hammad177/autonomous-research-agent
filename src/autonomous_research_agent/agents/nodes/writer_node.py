from autonomous_research_agent.agents.state import AgentState
from autonomous_research_agent.llm.writer_agent import build_writer_agent
from autonomous_research_agent.schemas.report import Report
from autonomous_research_agent.core.report_rendering import render_report_markdown


def make_writer_node():
    agent = build_writer_agent()

    async def writer_node(state: AgentState) -> AgentState:
        findings_text = "\n\n".join(
            f"Sub-question: {f['sub_question']}\nFindings: {f['content']}\nSource: {f['source']}"
            for f in state["findings"]
        )
        prompt = (
            f"Research goal: {state['goal']}\n\nApproved findings:\n{findings_text}"
        )

        feedback = state.get("draft_feedback")
        if feedback:
            previous_report = state.get("report", {})
            prompt += (
                f"\n\nA previous draft was reviewed and needs revision. "
                f"Previous draft title: {previous_report.get('title', 'N/A')}\n"
                f"Revision feedback: {feedback}\n"
                f"Produce an improved report that addresses this feedback."
            )

        result = await agent.run(prompt)
        report: Report = result.output
        markdown = render_report_markdown(report)

        return {
            "report": report.model_dump(),
            "draft": markdown,
            "trace": [f"writer: produced report with {len(report.sections)} sections"],
        }

    return writer_node
