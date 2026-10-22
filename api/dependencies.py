from fastapi import Depends, Request
from sqlalchemy.orm import Session

from core.database import get_db
from data.repositories.document_repository import DocumentRepository
from data.repositories.outbox_repository import OutboxRepository
from services.document_service import DocumentService


def get_inference_service(request: Request):
    return request.app.state.inference_service


def get_storage_service(request: Request):
    return request.app.state.storage_service


def get_document_service(
    db: Session = Depends(get_db),
    storage=Depends(get_storage_service),
) -> DocumentService:

    repository = DocumentRepository(db)
    outbox_repository = OutboxRepository(db)

    return DocumentService(
        repository=repository,
        outbox_repository=outbox_repository,
        storage=storage,
    )