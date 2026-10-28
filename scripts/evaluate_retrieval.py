
import os
from statistics import mean
from uuid import NAMESPACE_URL, uuid4, uuid5

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from services.embedding_service import EmbeddingService


PASSAGES = [
    {
        "key": "library_duration",
        "filename": "library_rules.txt",
        "text": (
            "Library borrowing: Registered students may borrow "
            "up to five books at a time. The standard borrowing "
            "period is fourteen days."
        ),
    },
    {
        "key": "library_late_fee",
        "filename": "library_rules.txt",
        "text": (
            "Library overdue policy: A returned book that is late "
            "incurs a daily overdue fine of 20 shillings for each "
            "day beyond the due date."
        ),
    },
    {
        "key": "data_retention",
        "filename": "data_protection.txt",
        "text": (
            "Personal data retention: Personal information should "
            "not be retained longer than necessary for its stated "
            "purpose. When retention is no longer justified, the "
            "data should be securely deleted or anonymised where "
            "appropriate and legally permitted."
        ),
    },
    {
        "key": "account_security",
        "filename": "account_security.txt",
        "text": (
            "Account security: Use a unique, strong password for "
            "each account and enable multi-factor authentication. "
            "These measures reduce the risk of unauthorised access "
            "if a password is compromised."
        ),
    },
    {
        "key": "aria_messaging",
        "filename": "aria_architecture.txt",
        "text": (
            "ARIA ingestion: The outbox publisher sends "
            "DocumentCreated events to the aria.events exchange "
            "using the document.created routing key. RabbitMQ "
            "routes matching messages to the aria.ingestion queue, "
            "where the ingestion worker consumes them."
        ),
    },
    {
        "key": "aria_outbox",
        "filename": "aria_architecture.txt",
        "text": (
            "Transactional outbox: ARIA records document metadata "
            "and a pending outbox event in one PostgreSQL "
            "transaction. A separate publisher sends pending "
            "events to RabbitMQ. This avoids losing the record "
            "of work when the message broker is unavailable "
            "during the original database transaction."
        ),
    },
    {
        "key": "aria_chunking",
        "filename": "aria_chunking.txt",
        "text": (
            "ARIA chunking: The FixedSizeChunker uses a maximum "
            "chunk size of 1000 characters and an overlap of "
            "200 characters. The window advances by 800 "
            "characters between successive chunks."
        ),
    },
    {
        "key": "aria_embeddings",
        "filename": "aria_embeddings.txt",
        "text": (
            "ARIA embeddings: Ollama runs the nomic-embed-text "
            "embedding model locally. In the current configuration, "
            "each document chunk is represented by a vector with "
            "768 numerical dimensions, which ARIA indexes in Qdrant."
        ),
    },
    {
        "key": "payment_idempotency",
        "filename": "payment_processing.txt",
        "text": (
            "Payment webhook idempotency: A payment service may "
            "receive the same webhook more than once. Recording "
            "a unique event or transaction identifier allows "
            "the service to recognise duplicate deliveries and "
            "avoid applying the same payment operation twice."
        ),
    },
]


BENCHMARK = [
    {
        "question": "How long can students borrow library books?",
        "relevant": {"library_duration"},
    },
    {
        "question": "What charge applies when a library book is overdue?",
        "relevant": {"library_late_fee"},
    },
    {
        "question": "When should personal information be deleted?",
        "relevant": {"data_retention"},
    },
    {
        "question": "How can a user reduce the risk of account compromise?",
        "relevant": {"account_security"},
    },
    {
        "question": "Which RabbitMQ queue receives ARIA document events?",
        "relevant": {"aria_messaging"},
    },
    {
        "question": "Why does ARIA use a transactional outbox?",
        "relevant": {"aria_outbox"},
    },
    {
        "question": "What chunk size and overlap does ARIA use?",
        "relevant": {"aria_chunking"},
    },
    {
        "question": "Which model creates ARIA's 768-dimensional vectors?",
        "relevant": {"aria_embeddings"},
    },
    {
        "question": "How does payment processing prevent duplicate webhooks?",
        "relevant": {"payment_idempotency"},
    },
]


def main() -> None:
    embedding_service = EmbeddingService()

    client = QdrantClient(
        url=os.getenv("QDRANT_URL", "http://localhost:6333")
    )

    # Each run gets a disposable collection. The existing
    # aria_chunks collection is not modified.
    collection_name = f"aria_eval_{uuid4().hex[:12]}"
    collection_created = False

    try:
        print("Generating benchmark document embeddings...")

        vectors = embedding_service.embed_documents(
            [passage["text"] for passage in PASSAGES]
        )

        if len(vectors) != len(PASSAGES):
            raise RuntimeError(
                "The embedding count does not match the passage count."
            )

        vector_size = len(vectors[0])

        if any(len(vector) != vector_size for vector in vectors):
            raise RuntimeError("Embedding dimensions are inconsistent.")

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )
        collection_created = True

        points = []

        for passage, vector in zip(PASSAGES, vectors):
            point_id = str(
                uuid5(NAMESPACE_URL, f"aria-eval:{passage['key']}")
            )

            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "key": passage["key"],
                        "filename": passage["filename"],
                        "text": passage["text"],
                    },
                )
            )

        client.upsert(
            collection_name=collection_name,
            points=points,
            wait=True,
        )

        print(f"Indexed {len(points)} benchmark passages.")
        print(f"Embedding dimensions: {vector_size}")

        rankings = []

        print("\nRetrieval results")
        print("=" * 70)

        for case in BENCHMARK:
            query_vector = embedding_service.embed_query(
                case["question"]
            )

            response = client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=5,
                with_payload=True,
            )

            results = response.points
            ranked_keys = [
                point.payload["key"]
                for point in results
            ]

            rank = next(
                (
                    position
                    for position, key in enumerate(ranked_keys, start=1)
                    if key in case["relevant"]
                ),
                None,
            )

            rankings.append(rank)

            print(f"\nQuestion: {case['question']}")
            print(f"Relevant passage rank: {rank or 'Not in top 5'}")

            for position, point in enumerate(results[:3], start=1):
                payload = point.payload or {}
                print(
                    f"  {position}. {payload.get('key')} "
                    f"(score={point.score:.4f})"
                )

        print("\nBenchmark summary")
        print("=" * 70)

        for k in (1, 3, 5):
            hits = sum(
                rank is not None and rank <= k
                for rank in rankings
            )
            print(f"Hit@{k}: {hits}/{len(BENCHMARK)} ({hits / len(BENCHMARK):.1%})")

        reciprocal_ranks = [
            1 / rank if rank is not None else 0
            for rank in rankings
        ]

        print(f"MRR@5: {mean(reciprocal_ranks):.4f}")

    finally:
        try:
            if collection_created:
                client.delete_collection(collection_name)
                print("\nTemporary benchmark collection removed.")
        finally:
            client.close()


if __name__ == "__main__":
    main()
