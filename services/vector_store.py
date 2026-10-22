import os
from uuid import UUID

from qdrant_client import QdrantClient, models

from data.db_models import Chunk


class VectorStore:
    def __init__(
        self,
        url: str | None = None,
        collection_name: str = "aria_chunks",
    ) -> None:
        self.collection_name = collection_name

        self.client = QdrantClient(
            url=url or os.getenv(
                "QDRANT_URL",
                "http://localhost:6333",
            )
        )

    def ensure_collection(self, vector_size: int) -> None:
        if not self.client.collection_exists(
            self.collection_name
        ):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE,
                ),
            )
            return

        collection = self.client.get_collection(
            self.collection_name
        )

        vector_config = collection.config.params.vectors

        if not hasattr(vector_config, "size"):
            raise ValueError(
                "ARIA expects a collection with one unnamed vector."
            )

        if vector_config.size != vector_size:
            raise ValueError(
                f"Collection dimension is {vector_config.size}, "
                f"but the embedding model returned {vector_size}. "
                "Use a separate collection for a different model."
            )

    def _get_document_point_ids(
        self,
        document_id: UUID,
    ) -> list:
        """Return all Qdrant point IDs belonging to a document."""
        point_ids = []
        offset = None

        query_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(
                        value=str(document_id)
                    ),
                )
            ]
        )

        while True:
            points, next_offset = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=query_filter,
                limit=256,
                offset=offset,
                with_payload=False,
                with_vectors=False,
            )

            point_ids.extend(point.id for point in points)

            if next_offset is None:
                break

            offset = next_offset

        return point_ids

    def replace_document_chunks(
        self,
        document_id: UUID,
        chunks: list[Chunk],
        vectors: list[list[float]],
    ) -> None:
        if len(chunks) != len(vectors):
            raise ValueError(
                "Each chunk must have exactly one embedding."
            )

        # This implementation expects non-empty extracted text.
        if not chunks:
            raise ValueError(
                "Cannot index a document without chunks."
            )

        self.ensure_collection(len(vectors[0]))

        points = []

        for chunk, vector in zip(chunks, vectors):
            metadata = chunk.metadata_json or {}

            payload = {
                **metadata,
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "start_offset": chunk.start_offset,
                "end_offset": chunk.end_offset,
            }

            points.append(
                models.PointStruct(
                    id=str(chunk.id),
                    vector=vector,
                    payload=payload,
                )
            )

        # Upsert inserts new points or overwrites points
        # with the same IDs.
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )

        # Remove stale points from earlier versions of this
        # document, but only after the new points were saved.
        current_ids = {str(chunk.id) for chunk in chunks}

        existing_ids = self._get_document_point_ids(
            document_id
        )

        stale_ids = [
            point_id
            for point_id in existing_ids
            if str(point_id) not in current_ids
        ]

        if stale_ids:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=stale_ids
                ),
                wait=True,
            )

    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
    ) -> list:
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True,
        )

        return results.points

    def close(self) -> None:
        self.client.close()