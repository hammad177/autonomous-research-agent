from neo4j import GraphDatabase
from autonomous_research_agent.config import settings
from autonomous_research_agent.schemas.graph import GraphFact


class GraphRepository:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
        )
        self.database = settings.NEO4J_DATABASE

    def close(self) -> None:
        self.driver.close()

    def add_relationship(
        self, subject: str, predicate: str, obj: str, source: str
    ) -> None:
        rel_type = predicate.strip().upper().replace(" ", "_").replace("-", "_")
        query = (
            "MERGE (a:Entity {name: $subject}) "
            "MERGE (b:Entity {name: $object}) "
            f"MERGE (a)-[r:`{rel_type}` {{source: $source}}]->(b)"
        )
        with self.driver.session(database=self.database) as session:
            session.run(query, subject=subject, object=obj, source=source)

    def delete_by_source(self, source: str) -> None:
        query = "MATCH ()-[r {source: $source}]-() DELETE r"
        with self.driver.session(database=self.database) as session:
            session.run(query, source=source)
        cleanup = "MATCH (n:Entity) WHERE NOT (n)--() DELETE n"
        with self.driver.session(database=self.database) as session:
            session.run(cleanup)

    def find_related(self, entity_name: str, max_hops: int = 2) -> list[GraphFact]:
        query = (
            f"MATCH (a:Entity)-[r*1..{max_hops}]-(b:Entity) "
            "WHERE toLower(a.name) CONTAINS toLower($entity_name) "
            "UNWIND r AS rel "
            "RETURN startNode(rel).name AS subject, type(rel) AS predicate, "
            "endNode(rel).name AS object, rel.source AS source "
            "LIMIT 25"
        )
        with self.driver.session(database=self.database) as session:
            result = session.run(query, entity_name=entity_name)
            return [
                GraphFact(
                    subject=r["subject"],
                    predicate=r["predicate"],
                    object=r["object"],
                    source=r["source"] or "unknown",
                )
                for r in result
            ]

    def list_entities(self, limit: int = 50) -> list[str]:
        query = "MATCH (n:Entity) RETURN n.name AS name LIMIT $limit"
        with self.driver.session(database=self.database) as session:
            result = session.run(query, limit=limit)
            return [r["name"] for r in result]
