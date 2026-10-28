from dataclasses import dataclass

from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore


@dataclass(frozen=True)
class RetrievedChunk:
    """A retrieved text chunk with its relevance score and provenance."""

    point_id: str
    score: float
    document_id: str | None
    chunk_id: str | None
    chunk_index: int | None
    text: str
    start_offset: int | None
    end_offset: int | None
    filename: str | None
    content_type: str | None


class RetrievalService:
    """Coordinates query embedding and vector similarity search."""

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        self.embedding_service = (
            embedding_service
            if embedding_service is not None
            else EmbeddingService()
        )

        self.vector_store = (
            vector_store
            if vector_store is not None
            else VectorStore()
        )

    def retrieve(
        self,
        query: str,
        limit: int = 5,
    ) -> list[RetrievedChunk]:
        """Return the top matching chunks for a natural-language query."""

        if not query or not query.strip():
            raise ValueError("Query must not be empty.")

        if limit < 1:
            raise ValueError("Limit must be at least 1.")

        # 1. Convert the question into a vector.
        query_vector = self.embedding_service.embed_query(query)

        # 2. Search Qdrant for the nearest document-chunk vectors.
        points = self.vector_store.search(
            query_vector,
            limit=limit,
        )

        # 3. Convert Qdrant results into a stable application-level format.
        results: list[RetrievedChunk] = []

        for point in points:
            payload = point.payload or {}

            results.append(
                RetrievedChunk(
                    point_id=str(point.id),
                    score=float(point.score),
                    document_id=payload.get("document_id"),
                    chunk_id=payload.get("chunk_id"),
                    chunk_index=payload.get("chunk_index"),
                    text=payload.get("text", ""),
                    start_offset=payload.get("start_offset"),
                    end_offset=payload.get("end_offset"),
                    filename=payload.get("filename"),
                    content_type=payload.get("content_type"),
                )
            )

        return results

    def close(self) -> None:
        """Release the vector-store client's resources."""

        self.vector_store.close()