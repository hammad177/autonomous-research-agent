from typing import AsyncGenerator
from langgraph.types import Command


class ResearchService:
    def __init__(self, graph):
        self.graph = graph

    def _config(self, thread_id: str) -> dict:
        return {"configurable": {"thread_id": thread_id}}

    async def start(self, thread_id: str, goal: str) -> dict:
        return await self.graph.ainvoke({"goal": goal}, config=self._config(thread_id))

    async def resume_with_decision(self, thread_id: str, decision: dict) -> dict:
        return await self.graph.ainvoke(
            Command(resume=decision), config=self._config(thread_id)
        )

    async def stream_start(
        self, thread_id: str, goal: str
    ) -> AsyncGenerator[dict, None]:
        """Yields one raw update dict per node as it completes, instead of
        waiting for the whole graph to finish. stream_mode='updates' gives
        {node_name: partial_state} per event — the same shape each node
        function already returns, just surfaced incrementally."""
        async for chunk in self.graph.astream(
            {"goal": goal}, config=self._config(thread_id), stream_mode="updates"
        ):
            yield chunk

    async def stream_resume(
        self, thread_id: str, decision: dict
    ) -> AsyncGenerator[dict, None]:
        async for chunk in self.graph.astream(
            Command(resume=decision),
            config=self._config(thread_id),
            stream_mode="updates",
        ):
            yield chunk

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
