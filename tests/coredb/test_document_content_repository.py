from uuid import uuid4

from core.database import SessionLocal
from data.db_models import Document, DocumentContent
from data.repositories.document_content_repository import (
    DocumentContentRepository,
)


def test_document_content_is_saved():

    db = SessionLocal()

    document_id = uuid4()

    document = Document(
        id=document_id,
        filename="content-test.txt",
        content_type="text/plain",
        size_bytes=12,
        storage_key=f"documents/{document_id}/original",
        status="processing",
    )

    db.add(document)
    db.commit()

    try:
        repository = DocumentContentRepository(db)

        content = repository.save(
            document_id=document_id,
            text="Hello ARIA",
            extraction_method="text-decoder",
            extraction_version="1.0",
        )

        db.commit()

        saved = repository.get_by_document_id(
            document_id
        )

        assert saved is not None
        assert saved.text == "Hello ARIA"
        assert saved.character_count == 10
        assert saved.extraction_method == "text-decoder"

    finally:
        db.close()
        
def test_document_content_can_be_updated():
    db = SessionLocal()

    document_id = uuid4()

    document = Document(
        id=document_id,
        filename="update-test.txt",
        content_type="text/plain",
        size_bytes=10,
        storage_key=f"documents/{document_id}/original",
        status="processing",
    )

    db.add(document)
    db.commit()

    try:
        repository = DocumentContentRepository(db)

        first = repository.save(
            document_id=document_id,
            text="Original text",
            extraction_method="text-decoder",
            extraction_version="1.0",
        )

        db.commit()

        second = repository.save(
            document_id=document_id,
            text="Updated text",
            extraction_method="text-decoder",
            extraction_version="1.1",
        )

        db.commit()

        saved = repository.get_by_document_id(document_id)

        assert saved is not None
        assert saved.id == first.id
        assert second.id == first.id
        assert saved.text == "Updated text"
        assert saved.extraction_version == "1.1"
        assert saved.character_count == len("Updated text")

    finally:
        db.close()