from uuid import UUID

from pydantic import BaseModel


class DocumentCreatedPayload(BaseModel):
    document_id: UUID
    filename: str
    content_type: str
    size_bytes: int
    storage_key: str


class DocumentCreatedEvent(BaseModel):
    event_id: UUID
    event_type: str
    aggregate_type: str
    aggregate_id: UUID
    payload: DocumentCreatedPayload