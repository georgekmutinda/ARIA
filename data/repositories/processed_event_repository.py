from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from data.db_models import ProcessedEvent


class ProcessedEventRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def is_processed(self, event_id: UUID) -> bool:
        statement = select(ProcessedEvent.event_id).where(
            ProcessedEvent.event_id == event_id
        )

        return self.db.scalars(statement).first() is not None

    def record(self, event_id: UUID) -> None:
        statement = (
            insert(ProcessedEvent)
            .values(event_id=event_id)
            .on_conflict_do_nothing(
                index_elements=["event_id"]
            )
        )

        self.db.execute(statement)