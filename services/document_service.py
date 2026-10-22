from uuid import uuid4

from fastapi import UploadFile

from data.db_models import Document, OutboxEvent
from data.repositories.document_repository import DocumentRepository
from data.repositories.outbox_repository import OutboxRepository
from services.storage import StorageService


class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository,
        outbox_repository: OutboxRepository,
        storage: StorageService,
    ) -> None:
        self.repository = repository
        self.outbox_repository = outbox_repository
        self.storage = storage

    def create_document(
        self,
        file: UploadFile,
        size_bytes: int,
    ) -> Document:

        document_id = uuid4()

        storage_key = (
            f"documents/{document_id}/original"
        )

        self.storage.upload(
            object_name=storage_key,
            file_data=file.file,
            length=size_bytes,
            content_type=(
                file.content_type
                or "application/octet-stream"
            ),
        )

        document = Document(
            id=document_id,
            filename=file.filename or "unknown",
            content_type=(
                file.content_type
                or "application/octet-stream"
            ),
            size_bytes=size_bytes,
            storage_key=storage_key,
            status="pending",
        )

        event = OutboxEvent(
            event_type="DocumentCreated",
            aggregate_type="Document",
            aggregate_id=document_id,
            payload={
                "document_id": str(document_id),
                "filename": document.filename,
                "content_type": document.content_type,
                "size_bytes": document.size_bytes,
                "storage_key": document.storage_key,
            },
        )

        self.repository.create(document)
        self.outbox_repository.create(event)
        print("COMMITTING DOCUMENT + OUTBOX")

        self.repository.db.commit()
        print("COMpLETED COMMITTING DOCUMENT + OUTBOX")
        self.repository.db.refresh(document)

        return document