from autonomous_research_agent.agents.state import AgentState
from autonomous_research_agent.llm.planner_agent import build_planner_agent


def make_planner_node():
    agent = build_planner_agent()

    async def planner_node(state: AgentState) -> AgentState:
        result = await agent.run(state["goal"])
        plan = result.output

        sub_questions = [
            {"question": sq.question, "rationale": sq.rationale}
            for sq in plan.sub_questions
        ]

        return {
            "sub_questions": sub_questions,
            "trace": [f"planner: produced {len(sub_questions)} sub-questions"],
        }

    return planner_node
