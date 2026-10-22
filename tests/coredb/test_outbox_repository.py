from uuid import uuid4

from sqlalchemy import delete

from core.database import SessionLocal
from data.db_models import OutboxEvent
from data.repositories.outbox_repository import OutboxRepository


def test_get_pending_events():
    db = SessionLocal()
    event_id = uuid4()

    try:
        event = OutboxEvent(
            id=event_id,
            event_type="DocumentCreated",
            aggregate_type="Document",
            aggregate_id=uuid4(),
            payload={"document_id": str(uuid4())},
            published_at=None,
        )

        db.add(event)
        db.commit()

        repository = OutboxRepository(db)
        events = repository.get_pending_events()

        assert any(item.id == event_id for item in events)
        assert all(item.published_at is None for item in events)

    finally:
        db.rollback()
        db.execute(
            delete(OutboxEvent).where(
                OutboxEvent.id == event_id
            )
        )
        db.commit()
        db.close()