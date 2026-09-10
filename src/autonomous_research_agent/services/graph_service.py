from autonomous_research_agent.core.entity_extraction import EntityExtractor
from autonomous_research_agent.repositories.graph_repository import GraphRepository
from autonomous_research_agent.schemas.graph import GraphFact


class GraphService:
    def __init__(self, graph_repo: GraphRepository):
        self.graph_repo = graph_repo
        self.extractor = EntityExtractor()

    def extract_and_store(self, text: str, source: str) -> int:
        extracted = self.extractor.extract(text)
        for rel in extracted.relationships:
            self.graph_repo.add_relationship(
                rel.subject, rel.predicate, rel.object, source=source
            )
        return len(extracted.relationships)

    def replace_source(self, text: str, source: str) -> int:
        self.graph_repo.delete_by_source(source)
        return self.extract_and_store(text, source)

    def lookup(self, entity_name: str) -> list[GraphFact]:
        return self.graph_repo.find_related(entity_name)
