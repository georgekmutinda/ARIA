from types import SimpleNamespace

import pytest

from services.retrieval_service import RetrievalService


class FakeEmbeddingService:
    def __init__(self):
        self.received_query = None

    def embed_query(self, query: str):
        self.received_query = query
        return [0.1, 0.2, 0.3]


class FakeVectorStore:
    def __init__(self):
        self.received_vector = None
        self.received_limit = None
        self.closed = False

    def search(self, query_vector, limit=5):
        self.received_vector = query_vector
        self.received_limit = limit

        return [
            SimpleNamespace(
                id="chunk-uuid-1",
                score=0.82,
                payload={
                    "document_id": "document-uuid-1",
                    "chunk_id": "chunk-uuid-1",
                    "chunk_index": 2,
                    "text": "A policy must protect personal data.",
                    "start_offset": 1600,
                    "end_offset": 1650,
                    "filename": "policy.txt",
                    "content_type": "text/plain",
                },
            )
        ]

    def close(self):
        self.closed = True


def test_retrieve_embeds_query_and_returns_source_information():
    embedding = FakeEmbeddingService()
    vector_store = FakeVectorStore()

    service = RetrievalService(
        embedding_service=embedding,
        vector_store=vector_store,
    )

    results = service.retrieve(
        "How should personal data be protected?",
        limit=3,
    )

    assert embedding.received_query == (
        "How should personal data be protected?"
    )

    assert vector_store.received_vector == [0.1, 0.2, 0.3]
    assert vector_store.received_limit == 3

    assert len(results) == 1

    result = results[0]
    assert result.score == pytest.approx(0.82)
    assert result.document_id == "document-uuid-1"
    assert result.chunk_index == 2
    assert result.text == "A policy must protect personal data."
    assert result.start_offset == 1600
    assert result.end_offset == 1650
    assert result.filename == "policy.txt"


def test_retrieve_rejects_empty_query():
    service = RetrievalService(
        embedding_service=FakeEmbeddingService(),
        vector_store=FakeVectorStore(),
    )

    with pytest.raises(ValueError, match="Query must not be empty"):
        service.retrieve("   ")


def test_retrieve_rejects_invalid_limit():
    service = RetrievalService(
        embedding_service=FakeEmbeddingService(),
        vector_store=FakeVectorStore(),
    )

    with pytest.raises(ValueError, match="Limit must be at least 1"):
        service.retrieve("What is personal data?", limit=0)