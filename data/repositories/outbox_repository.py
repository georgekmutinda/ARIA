from sqlalchemy import select
from sqlalchemy.orm import Session

from data.db_models import OutboxEvent


class OutboxRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, event: OutboxEvent) -> OutboxEvent:
        self.db.add(event)
        return event

    def get_pending_events(
        self,
        limit: int = 100,
    ) -> list[OutboxEvent]:

        statement = (
            select(OutboxEvent)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.created_at)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())
    
    
    
if __name__ == "__main__":
    print("🚀 Script executed successfully! The OutboxRepository module was loaded without errors.")
