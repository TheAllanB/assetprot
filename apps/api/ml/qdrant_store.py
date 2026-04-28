"""
Concrete Qdrant-backed VectorStore implementation.

Implements the VectorStore protocol so services depend on the
abstraction, not Qdrant directly (DIP).
"""

import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


class QdrantVectorStore:
    """Concrete VectorStore backed by Qdrant (DIP — implements VectorStore protocol)."""

    def __init__(self, client: QdrantClient) -> None:
        self._client = client

    def init_collection(self, collection_name: str, vector_size: int = 512) -> None:
        """Ensure a collection exists (idempotent)."""
        existing = {c.name for c in self._client.get_collections().collections}
        if collection_name not in existing:
            self._client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def upsert(
        self, collection: str, asset_id: str, org_id: str, vector: list[float]
    ) -> str:
        """Upsert a single embedding vector. Returns the point ID."""
        point_id = str(uuid.uuid4())
        self._client.upsert(
            collection_name=collection,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={"asset_id": asset_id, "org_id": org_id},
                )
            ],
        )
        return point_id

    def search(
        self, collection: str, vector: list[float], score_threshold: float, limit: int = 10
    ) -> list[dict]:
        """Search for similar vectors. Returns flat dicts with asset_id + score."""
        results = self._client.search(
            collection_name=collection,
            query_vector=vector,
            score_threshold=score_threshold,
            limit=limit,
        )
        return [{"asset_id": r.payload["asset_id"], "score": r.score} for r in results]


# ── Legacy free-function API (delegates to class for backward compat) ────────

def init_collection(client: QdrantClient, collection_name: str, vector_size: int = 512) -> None:
    QdrantVectorStore(client).init_collection(collection_name, vector_size)


def upsert_embedding(
    client: QdrantClient, collection_name: str, asset_id: str, org_id: str, vector: list[float]
) -> str:
    return QdrantVectorStore(client).upsert(collection_name, asset_id, org_id, vector)


def search_similar(
    client: QdrantClient, collection_name: str, vector: list[float],
    score_threshold: float, limit: int = 10
) -> list[dict]:
    return QdrantVectorStore(client).search(collection_name, vector, score_threshold, limit)
