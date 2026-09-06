from fastapi import APIRouter
from neo4j import GraphDatabase
from qdrant_client import QdrantClient

from autonomous_research_agent.config import settings

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/")
def health_check():
    status = {"app": "ok", "neo4j": "unknown", "qdrant": "unknown", "openai": "unknown"}

    try:
        driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
        )
        driver.verify_connectivity()
        driver.close()
        status["neo4j"] = "ok"
    except Exception as e:
        status["neo4j"] = f"unreachable: {e}"

    try:
        client = QdrantClient(url=settings.QDRANT_URL)
        client.get_collections()
        status["qdrant"] = "ok"
    except Exception as e:
        status["qdrant"] = f"unreachable: {e}"

    status["openai"] = "ok" if settings.OPENAI_API_KEY else "missing API key"

    return status
