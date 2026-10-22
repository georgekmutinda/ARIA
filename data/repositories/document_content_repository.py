from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from data.db_models import DocumentContent

class DocumentContentRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def save(
        self,
        document_id: UUID,
        text: str,
        extraction_method: str,
        extraction_version: str,
    ) -> DocumentContent:

        statement = (
            select(DocumentContent)
            .where(
                DocumentContent.document_id == document_id
            )
        )

        existing = self.db.scalars(statement).first()

        if existing is None:
            existing = DocumentContent(
                document_id=document_id,
                text=text,
                extraction_method=extraction_method,
                extraction_version=extraction_version,
                character_count=len(text),
            )
            self.db.add(existing)
        else:
            existing.text = text
            existing.extraction_method = extraction_method
            existing.extraction_version = extraction_version
            existing.character_count = len(text)

        return existing

    # ➕ Added to resolve the test failure
    def get_by_document_id(self, document_id: UUID) -> DocumentContent | None:
        """Fetches the extracted content for a specific document ID."""
        statement = (
            select(DocumentContent)
            .where(DocumentContent.document_id == document_id)
        )
        return self.db.scalars(statement).first()
