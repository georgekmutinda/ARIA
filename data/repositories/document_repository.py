from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from data.db_models import Document


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, document: Document) -> Document:
        self.db.add(document)
        return document

    def get_by_id(self, document_id: UUID) -> Document | None:
        statement = select(Document).where(
            Document.id == document_id
        )

        return self.db.scalars(statement).first()

    def update_status(
        self,
        document: Document,
        status: str,
    ) -> Document:
        document.status = status
        return document