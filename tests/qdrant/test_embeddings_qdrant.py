from uuid import uuid4

import ollama
from qdrant_client import QdrantClient, models


MODEL_NAME = "nomic-embed-text"
COLLECTION_NAME = "aria_chunks"

SAMPLE_TEXT = (
    "Data controllers must comply with applicable "
    "data protection requirements."
)


def main() -> None:
    # 1. Generate an embedding through Ollama.
    response = ollama.embed(
        model=MODEL_NAME,
        input=SAMPLE_TEXT,
    )

    vector = response["embeddings"][0]

    print(f"Embedding dimensions: {len(vector)}")

    # 2. Connect to Qdrant.
    client = QdrantClient(url="http://localhost:6333")

    try:
        # 3. Create the collection if it doesn't exist.
        if not client.collection_exists(COLLECTION_NAME):
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=len(vector),
                    distance=models.Distance.COSINE,
                ),
            )
            print(f"Created collection: {COLLECTION_NAME}")

        else:
            collection = client.get_collection(COLLECTION_NAME)
            vector_config = collection.config.params.vectors

            if vector_config.size != len(vector):
                raise ValueError(
                    "Embedding dimension mismatch. "
                    f"Collection expects {vector_config.size}, "
                    f"but Ollama returned {len(vector)}. "
                    "Use a separate collection for a different "
                    "embedding model."
                )

            print(f"Using collection: {COLLECTION_NAME}")

        # 4. Insert one temporary test point.
        point_id = str(uuid4())

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "text": SAMPLE_TEXT,
                        "source": "embedding_test",
                    },
                )
            ],
            wait=True,
        )

        # 5. Verify the point was saved.
        stored = client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[point_id],
            with_payload=True,
        )

        assert len(stored) == 1
        assert stored[0].payload["text"] == SAMPLE_TEXT

        # 6. Search using the same embedding.
        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=3,
            with_payload=True,
        ).points

        assert any(point.id == point_id for point in results)

        print("Embedding generated successfully.")
        print("Qdrant insert and retrieval succeeded.")
        print("Similarity search returned the test point.")

        # 7. Remove the temporary test data.
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=models.PointIdsList(
                points=[point_id],
            ),
            wait=True,
        )

        print("Temporary test point removed.")
        print("C9 infrastructure test passed.")

    finally:
        client.close()


if __name__ == "__main__":
    main()