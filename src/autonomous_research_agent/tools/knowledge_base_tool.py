"""Knowledge base tool: hybrid (dense + sparse) search over ingested documents."""

from langchain_core.tools import tool

from autonomous_research_agent.repositories.vector_repository import VectorRepository


def build_knowledge_base_tool(vector_repo: VectorRepository):
    @tool
    def knowledge_base_search(query: str) -> str:
        """Searches the user's own ingested documents (PDFs/URLs) using hybrid
        semantic + keyword search. Prefer this first for questions likely
        covered by uploaded reference material."""
        results = vector_repo.hybrid_search(query, top_k=4)
        if not results:
            return "No relevant results found in the knowledge base."
        return "\n\n".join(f"[Source: {r['source']}]\n{r['text']}" for r in results)

    return knowledge_base_search
