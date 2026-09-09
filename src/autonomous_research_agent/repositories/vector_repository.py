import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    SparseVectorParams,
    Distance,
    PointStruct,
    SparseVector,
    Prefetch,
    FusionQuery,
    Fusion,
    FilterSelector,
    Filter,
    FieldCondition,
    MatchValue,
)
from fastembed import SparseTextEmbedding
from langchain_openai import OpenAIEmbeddings

from autonomous_research_agent.config import settings
from autonomous_research_agent.common.constants import (
    DENSE_VECTOR_NAME,
    SPARSE_VECTOR_NAME,
    EMBEDDING_DIMENSIONS,
)


class VectorRepository:
    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.dense_embedder = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )
        # Runs locally, no API cost — downloads the model on first use.
        self.sparse_embedder = SparseTextEmbedding(model_name="Qdrant/bm25")
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        if self.client.collection_exists(self.collection_name):
            return
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config={
                DENSE_VECTOR_NAME: VectorParams(
                    size=EMBEDDING_DIMENSIONS, distance=Distance.COSINE
                ),
            },
            sparse_vectors_config={
                SPARSE_VECTOR_NAME: SparseVectorParams(),
            },
        )

    def add_chunks(self, chunks: list[str], source: str, document_id: str) -> None:
        if not chunks:
            return

        dense_vectors = self.dense_embedder.embed_documents(chunks)
        sparse_vectors = list(self.sparse_embedder.embed(chunks))

        points = []
        for i, (chunk, dense, sparse) in enumerate(
            zip(chunks, dense_vectors, sparse_vectors)
        ):
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector={
                        DENSE_VECTOR_NAME: dense,
                        SPARSE_VECTOR_NAME: SparseVector(
                            indices=sparse.indices.tolist(),
                            values=sparse.values.tolist(),
                        ),
                    },
                    payload={
                        "text": chunk,
                        "source": source,
                        "document_id": document_id,
                        "chunk_index": i,
                    },
                )
            )

        self.client.upsert(collection_name=self.collection_name, points=points)

    def delete_by_document_id(self, document_id: str) -> None:
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="document_id", match=MatchValue(value=document_id)
                        ),
                    ]
                ),
            ),
        )

    def hybrid_search(self, query: str, top_k: int = 5) -> list[dict]:
        dense_query = self.dense_embedder.embed_query(query)
        sparse_query = list(self.sparse_embedder.embed([query]))[0]

        results = self.client.query_points(
            collection_name=self.collection_name,
            prefetch=[
                Prefetch(query=dense_query, using=DENSE_VECTOR_NAME, limit=top_k * 2),
                Prefetch(
                    query=SparseVector(
                        indices=sparse_query.indices.tolist(),
                        values=sparse_query.values.tolist(),
                    ),
                    using=SPARSE_VECTOR_NAME,
                    limit=top_k * 2,
                ),
            ],
            query=FusionQuery(fusion=Fusion.RRF),
            limit=top_k,
        )

        return [
            {
                "text": point.payload["text"],
                "source": point.payload["source"],
                "chunk_index": point.payload["chunk_index"],
                "score": point.score,
            }
            for point in results.points
        ]
