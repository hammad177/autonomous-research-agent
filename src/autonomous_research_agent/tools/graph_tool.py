from langchain_core.tools import tool

from autonomous_research_agent.services.graph_service import GraphService


def build_graph_lookup_tool(graph_service: GraphService):
    @tool
    def graph_lookup(entity_name: str) -> str:
        """Looks up relationships for a named entity (person, company,
        product, technology) in the knowledge graph built from ingested
        documents. Prefer this for questions about how entities relate to
        each other, not for general factual lookups."""
        facts = graph_service.lookup(entity_name)
        if not facts:
            return f"No relationships found for '{entity_name}' in the knowledge graph."
        return "\n".join(
            f"{f.subject} {f.predicate} {f.object} (source: {f.source})" for f in facts
        )

    return graph_lookup
