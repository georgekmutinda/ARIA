import pytest

from core.database import SessionLocal
from data.db_models import Document, OutboxEvent


def test_document_and_outbox_rollback_together():
    db = SessionLocal()

    document_id = __import__("uuid").uuid4()

    document = Document(
        id=document_id,
        filename="rollback-test.txt",
        content_type="text/plain",
        size_bytes=10,
        storage_key=f"documents/{document_id}/original",
        status="pending",
    )

    event = OutboxEvent(
        event_type="DocumentCreated",
        aggregate_type="Document",
        aggregate_id=document_id,
        payload={
            "document_id": str(document_id),
            "filename": "rollback-test.txt",
        },
    )

    try:
        db.add(document)
        db.add(event)

        # Simulate something going wrong before commit.
        raise RuntimeError("Simulated failure")

    except RuntimeError:
        db.rollback()

    finally:
        db.close()

    # New session: check what actually became durable.
    db = SessionLocal()

    try:
        assert db.get(Document, document_id) is None

        event_exists = (
            db.query(OutboxEvent)
            .filter(
                OutboxEvent.aggregate_id == document_id
            )
            .first()
        )

        assert event_exists is None

    finally:
        db.close()