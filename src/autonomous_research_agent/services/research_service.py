from langgraph.types import Command


class ResearchService:
    def __init__(self, graph):
        self.graph = graph

    def _config(self, thread_id: str) -> dict:
        return {"configurable": {"thread_id": thread_id}}

    async def start(self, thread_id: str, goal: str) -> dict:
        return await self.graph.ainvoke({"goal": goal}, config=self._config(thread_id))

    async def resume_with_decision(self, thread_id: str, decision: dict) -> dict:
        """Resumes a paused run with a human decision — works for both the
        plan-approval and draft-approval interrupts, since both just pass
        whatever dict the corresponding node's interrupt() call expects."""
        return await self.graph.ainvoke(
            Command(resume=decision), config=self._config(thread_id)
        )

    async def get_status(self, thread_id: str) -> dict:
        snapshot = await self.graph.aget_state(self._config(thread_id))
        values = snapshot.values

        pending_interrupt = None
        for task in snapshot.tasks:
            if task.interrupts:
                pending_interrupt = task.interrupts[0].value
                break

        return {
            "goal": values.get("goal", ""),
            "pending_interrupt": pending_interrupt,
            "findings": values.get("findings", []),
            "critic_verdict": values.get("critic_verdict"),
            "revision_count": values.get("revision_count", 0),
            "draft": values.get("draft"),
            "trace": values.get("trace", []),
            "is_paused": bool(snapshot.next),
        }
