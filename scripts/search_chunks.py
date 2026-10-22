import sys

from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore


def main() -> None:
    query = " ".join(sys.argv[1:]).strip()

    if not query:
        query = input("Enter your question: ").strip()

    if not query:
        raise ValueError("Search query cannot be empty.")

    embedding_service = EmbeddingService()
    vector_store = VectorStore()

    try:
        query_vector = embedding_service.embed_query(query)

        results = vector_store.search(
            query_vector=query_vector,
            limit=5,
        )

        if not results:
            print("No matching chunks found.")
            return

        for result in results:
            payload = result.payload or {}

            print(f"\nScore: {result.score:.4f}")
            print(f"Document: {payload.get('document_id')}")
            print(f"Chunk: {payload.get('chunk_index')}")
            print(f"Text: {payload.get('text', '')[:500]}")

    finally:
        vector_store.close()


if __name__ == "__main__":
    main()