from mem0 import Memory

from autonomous_research_agent.config import settings
from autonomous_research_agent.schemas.memory import MemoryEntry


class MemoryService:
    def __init__(self):
        self.memory = Memory.from_config(
            {
                "llm": {
                    "provider": "openai",
                    "config": {
                        "model": settings.CHAT_MODEL,
                        "api_key": settings.OPENAI_API_KEY,
                    },
                },
                "embedder": {
                    "provider": "openai",
                    "config": {
                        "model": settings.EMBEDDING_MODEL,
                        "api_key": settings.OPENAI_API_KEY,
                    },
                },
            }
        )
        self.namespace = settings.MEMORY_NAMESPACE

    def store_run_summary(self, goal: str, findings: list[dict]) -> None:
        """Distills a completed run's findings into memory. Mem0 itself
        decides what's actually worth remembering from this text, rather
        than storing the raw findings verbatim."""
        findings_text = "\n".join(
            f"- {f['sub_question']}: {f['content'][:300]}" for f in findings
        )
        messages = [
            {"role": "user", "content": f"Research goal: {goal}"},
            {"role": "assistant", "content": f"Findings:\n{findings_text}"},
        ]
        self.memory.add(messages, user_id=self.namespace)

    def search(self, query: str, limit: int = 5) -> list[MemoryEntry]:
        results = self.memory.search(
            query, filters={"user_id": self.namespace}, limit=limit
        )
        entries = results.get("results", []) if isinstance(results, dict) else results
        return [
            MemoryEntry(
                id=r.get("id", ""), memory=r.get("memory", ""), score=r.get("score")
            )
            for r in entries
        ]

    def get_all(self) -> list[MemoryEntry]:
        results = self.memory.get_all(filters={"user_id": self.namespace})
        entries = results.get("results", []) if isinstance(results, dict) else results
        return [
            MemoryEntry(id=r.get("id", ""), memory=r.get("memory", ""), score=None)
            for r in entries
        ]
