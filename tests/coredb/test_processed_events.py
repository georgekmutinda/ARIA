from uuid import uuid4

from sqlalchemy import delete

from core.database import SessionLocal
from data.db_models import ProcessedEvent
from data.repositories.processed_event_repository import (
    ProcessedEventRepository,
)


def test_same_event_can_only_be_recorded_once():
    event_id = uuid4()
    db = SessionLocal()

    try:
        repository = ProcessedEventRepository(db)

        # The event should initially be absent.
        assert repository.is_processed(event_id) is False

        # First recording: insert the event.
        repository.record(event_id)
        db.commit()

        assert repository.is_processed(event_id) is True

        # Second recording: duplicate should be ignored.
        repository.record(event_id)
        db.commit()

        count = (
            db.query(ProcessedEvent)
            .filter(ProcessedEvent.event_id == event_id)
            .count()
        )

        assert count == 1

    finally:
        # Remove this test's record so repeated test runs
        # do not accumulate test data.
        db.rollback()

        db.execute(
            delete(ProcessedEvent).where(
                ProcessedEvent.event_id == event_id
            )
        )
        db.commit()
        db.close()