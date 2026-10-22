from io import BytesIO

from fastapi.testclient import TestClient

from api.app import create_app
from api.dependencies import get_storage_service

from core.database import SessionLocal
from data.db_models import Document, OutboxEvent


class MockStorageService:

    def upload(
        self,
        object_name,
        file_data,
        length,
        content_type,
    ):
        return None


app = create_app()

app.dependency_overrides[get_storage_service] = (
    lambda: MockStorageService()
)

client = TestClient(app)


def test_document_upload_creates_outbox_event():

    response = client.post(
        "/documents",
        files={
            "file": (
                "test.txt",
                BytesIO(b"Hello ARIA"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 202

    document_id = response.json()["document_id"]

    db = SessionLocal()

    try:
        document = db.get(Document, document_id)

        assert document is not None
        assert document.filename == "test.txt"

        event = (
            db.query(OutboxEvent)
            .filter(
                OutboxEvent.aggregate_id == document.id
            )
            .first()
        )

        assert event is not None
        assert event.event_type == "DocumentCreated"
        assert event.aggregate_type == "Document"
        assert event.published_at is None

        assert event.payload["document_id"] == str(document.id)

    finally:
        db.close()