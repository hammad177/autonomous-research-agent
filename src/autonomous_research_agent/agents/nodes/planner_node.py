from autonomous_research_agent.agents.state import AgentState
from autonomous_research_agent.llm.planner_agent import build_planner_agent
from autonomous_research_agent.services.memory_service import MemoryService


def make_planner_node(memory_service: MemoryService):
    agent = build_planner_agent()

    async def planner_node(state: AgentState) -> AgentState:
        goal = state["goal"]
        feedback = state.get("planner_feedback")
        past_memories = memory_service.search(goal, limit=3)

        prompt = goal
        if past_memories:
            memory_context = "\n".join(f"- {m.memory}" for m in past_memories)
            prompt = (
                f"{goal}\n\nRelevant findings from past research:\n{memory_context}\n"
                f"Build on this where relevant — don't re-plan sub-questions "
                f"that would just re-derive what's already known above."
            )

        if feedback:
            prompt += (
                f"\n\nA previous plan was rejected with this feedback: {feedback}\n"
                f"Produce an improved plan that addresses it."
            )

        result = await agent.run(prompt)
        plan = result.output

        sub_questions = [
            {"question": sq.question, "rationale": sq.rationale}
            for sq in plan.sub_questions
        ]

        trace_msg = f"planner: produced {len(sub_questions)} sub-questions"
        if past_memories:
            trace_msg += f" (informed by {len(past_memories)} past memories)"

        return {"sub_questions": sub_questions, "trace": [trace_msg]}

    return planner_node
