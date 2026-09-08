from autonomous_research_agent.agents.state import AgentState
from autonomous_research_agent.llm.planner_agent import build_planner_agent


def make_planner_node():
    agent = build_planner_agent()

    async def planner_node(state: AgentState) -> AgentState:
        goal = state["goal"]
        feedback = state.get("planner_feedback")

        prompt = goal
        if feedback:
            prompt = (
                f"{goal}\n\nA previous plan was rejected with this feedback: "
                f"{feedback}\nProduce an improved plan that addresses it."
            )

        result = await agent.run(prompt)
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
