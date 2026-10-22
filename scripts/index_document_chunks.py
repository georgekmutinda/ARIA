import sys
from uuid import UUID

from core.database import SessionLocal
from data.repositories.chunk_repository import ChunkRepository
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: python -m scripts.index_document_chunks "
            "<DOCUMENT_UUID>"
        )
        raise SystemExit(2)

    document_id = UUID(sys.argv[1])
    db = SessionLocal()
    vector_store = VectorStore()

    try:
        repository = ChunkRepository(db)

        chunks = repository.get_by_document_id(
            document_id
        )

        if not chunks:
            raise ValueError(
                f"No chunks found for document {document_id}"
            )

        embedding_service = EmbeddingService()

        print(f"Found {len(chunks)} chunks.")
        print("Generating embeddings...")

        vectors = embedding_service.embed_documents(
            [chunk.text for chunk in chunks]
        )

        print(
            f"Generated {len(vectors)} embeddings "
            f"with {len(vectors[0])} dimensions."
        )

        vector_store.replace_document_chunks(
            document_id=document_id,
            chunks=chunks,
            vectors=vectors,
        )

        print(
            f"Indexed {len(chunks)} chunks for "
            f"document {document_id}."
        )

    finally:
        vector_store.close()
        db.close()


if __name__ == "__main__":
    main()