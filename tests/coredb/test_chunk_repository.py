from uuid import uuid4

from sqlalchemy import delete

from core.database import SessionLocal
from data.db_models import Chunk, Document
from data.repositories.chunk_repository import ChunkRepository


def test_chunks_are_saved_in_document_order():
    db = SessionLocal()
    document_id = uuid4()

    try:
        # Create a document for the chunks.
        document = Document(
            id=document_id,
            filename="chunk-test.txt",
            content_type="text/plain",
            size_bytes=30,
            storage_key=f"documents/{document_id}/original",
            status="processing",
        )

        db.add(document)
        db.commit()

        repository = ChunkRepository(db)

        chunks = [
            Chunk(
                document_id=document_id,
                chunk_index=0,
                text="first chunk",
                start_offset=0,
                end_offset=11,
                metadata_json={
                    "filename": "chunk-test.txt",
                },
            ),
            Chunk(
                document_id=document_id,
                chunk_index=1,
                text="second chunk",
                start_offset=11,
                end_offset=23,
                metadata_json={
                    "filename": "chunk-test.txt",
                },
            ),
        ]

        repository.create_many(chunks)
        db.commit()

        saved = repository.get_by_document_id(document_id)

        assert len(saved) == 2
        assert saved[0].chunk_index == 0
        assert saved[1].chunk_index == 1

        assert saved[0].text == "first chunk"
        assert saved[1].text == "second chunk"

        assert saved[0].start_offset == 0
        assert saved[1].start_offset == 11

    finally:
        # Clean up the rows created by this test.
        db.rollback()

        db.execute(
            delete(Chunk).where(
                Chunk.document_id == document_id
            )
        )
        db.execute(
            delete(Document).where(
                Document.id == document_id
            )
        )

        db.commit()
        db.close()