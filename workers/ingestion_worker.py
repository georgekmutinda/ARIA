import asyncio
import json
import os
import tempfile
from pathlib import Path
from uuid import uuid4

import aio_pika

from core.database import SessionLocal
from data.db_models import Chunk
from data.repositories.chunk_repository import ChunkRepository
from data.repositories.document_content_repository import (
    DocumentContentRepository,
)
from data.repositories.document_repository import DocumentRepository
from data.repositories.processed_event_repository import (
    ProcessedEventRepository,
)
from services.chunking import FixedSizeChunker
from services.embedding_service import EmbeddingService
from services.events import DocumentCreatedEvent
from services.extraction import ExtractionService
from services.messaging import RabbitMQ
from services.storage import StorageService
from services.vector_store import VectorStore


chunker = FixedSizeChunker(
    chunk_size=1000,
    overlap=200,
)

extractor = ExtractionService()
embedding_service = EmbeddingService()


def create_storage_service() -> StorageService:
    return StorageService(
        endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        bucket_name=os.getenv("MINIO_BUCKET_NAME", "aria"),
        secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
    )


storage = create_storage_service()


async def process_message(
    message: aio_pika.IncomingMessage,
) -> None:
    # Development behavior: failed messages are rejected,
    # not automatically retried. We'll add retry/DLQ handling next.
    async with message.process(requeue=False):
        raw_event = json.loads(message.body)
        event = DocumentCreatedEvent.model_validate(raw_event)

        if event.event_type != "DocumentCreated":
            raise ValueError(f"Unsupported event: {event.event_type}")

        if event.payload.document_id != event.aggregate_id:
            raise ValueError("Document ID does not match event aggregate ID.")

        db = SessionLocal()
        vector_store = None

        document_repository = DocumentRepository(db)
        content_repository = DocumentContentRepository(db)
        chunk_repository = ChunkRepository(db)
        processed_repository = ProcessedEventRepository(db)

        try:
            # 1. Skip events already completed.
            if processed_repository.is_processed(event.event_id):
                print(f"⏭️ Already processed: {event.event_id}")
                return

            # 2. Load document metadata.
            document = document_repository.get_by_id(event.aggregate_id)

            if document is None:
                raise ValueError(f"Document not found: {event.aggregate_id}")

            document_id = document.id
            storage_key = document.storage_key
            content_type = document.content_type
            filename = document.filename

            # 3. Mark processing.
            document_repository.update_status(document, "processing")
            db.commit()

            print(f"🔄 Processing document {document_id}...")

            # 4. Download and extract.
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir) / "original_document"

                await asyncio.to_thread(
                    storage.download_to_file,
                    storage_key,
                    temp_path,
                )

                print(f"📥 Downloaded {storage_key}")

                text = await asyncio.to_thread(
                    extractor.extract,
                    temp_path,
                    content_type,
                )

            if not text.strip():
                raise ValueError(f"No extractable text: {document_id}")

            print(f"📄 Extracted {len(text)} characters")

            # 5. Chunk.
            chunk_results = chunker.chunk(text)

            if not chunk_results:
                raise ValueError(f"No chunks generated: {document_id}")

            print(f"✂️ Created {len(chunk_results)} chunks")

            # Assign IDs explicitly because Qdrant uses these IDs too.
            chunk_models = [
                Chunk(
                    id=uuid4(),
                    document_id=document_id,
                    chunk_index=result.index,
                    text=result.text,
                    start_offset=result.start_offset,
                    end_offset=result.end_offset,
                    metadata_json={
                        "content_type": content_type,
                        "filename": filename,
                    },
                )
                for result in chunk_results
            ]

            # 6. Prepare PostgreSQL changes.
            extraction_method = (
                "pypdf"
                if content_type == "application/pdf"
                else "text-decoder"
            )

            content_repository.save(
                document_id=document_id,
                text=text,
                extraction_method=extraction_method,
                extraction_version="1.0",
            )

            chunk_repository.delete_by_document_id(document_id)
            chunk_repository.create_many(chunk_models)

            # Execute SQL now, but don't commit these changes yet.
            db.flush()

            # 7. Generate embeddings using Ollama.
            print("🧠 Generating embeddings...")

            vectors = await asyncio.to_thread(
                embedding_service.embed_documents,
                [chunk.text for chunk in chunk_models],
            )

            print(
                f"Generated {len(vectors)} embeddings "
                f"with {len(vectors[0])} dimensions."
            )

            # 8. Index the chunks and vectors in Qdrant.
            vector_store = VectorStore()

            await asyncio.to_thread(
                vector_store.replace_document_chunks,
                document_id,
                chunk_models,
                vectors,
            )

            print(f"🔎 Indexed {len(chunk_models)} chunks in Qdrant")

            # 9. Commit final PostgreSQL state.
            document_repository.update_status(document, "processed")
            processed_repository.record(event.event_id)

            db.commit()

            print(f"✅ Document {document_id} processed successfully")

        except Exception:
            db.rollback()

            # Preserve a useful document status if possible.
            try:
                failed_document = document_repository.get_by_id(
                    event.aggregate_id
                )

                if (
                    failed_document is not None
                    and failed_document.status != "processed"
                ):
                    document_repository.update_status(
                        failed_document,
                        "failed",
                    )
                    db.commit()

            except Exception as status_error:
                db.rollback()
                print(f"⚠️ Could not save failure status: {status_error}")

            raise

        finally:
            if vector_store is not None:
                await asyncio.to_thread(vector_store.close)

            db.close()


async def main() -> None:
    rabbit = RabbitMQ(
        "amqp://aria:aria@127.0.0.1:5672/%2f",
    )

    try:
        await rabbit.connect()
        queue = await rabbit.declare_ingestion_queue()
        await queue.consume(process_message)

        print("👂 ARIA ingestion worker listening for messages...")
        await asyncio.Future()

    finally:
        await rabbit.close()


if __name__ == "__main__":
    asyncio.run(main())