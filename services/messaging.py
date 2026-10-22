import json
from uuid import uuid4

import aio_pika
from aio_pika import ExchangeType, Message


class RabbitMQ:
    def __init__(self, url: str, exchange_name: str = "aria.events"):
        self.url = url
        self.exchange_name = exchange_name
        self.connection = None
        self.channel = None
        self.exchange = None

    async def connect(self):
        # FIX: Bypass URL string parsing bugs completely.
        # We explicitly supply connection values directly to the connection layer.
        self.connection = await aio_pika.connect_robust(
            host="127.0.0.1",
            port=5672,
            login="aria",
            password="aria",
            virtualhost="/"  # Explicitly names the root virtual host
        )

        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)
        self.exchange = await self.channel.declare_exchange(
            self.exchange_name,
            ExchangeType.DIRECT,
            durable=True,
        )

    async def declare_ingestion_queue(self):
        queue = await self.channel.declare_queue("aria.ingestion", durable=True)
        await queue.bind(self.exchange, routing_key="document.created")
        return queue

    async def publish_document_created(
        self,
        event_id: str | None = None,
        document_id: str | None = None,
        filename: str = "test_document.txt",
        content_type: str = "text/plain",
        size_bytes: int = 128,
        storage_key: str | None = None,
    ):
        if event_id is None:
            event_id = str(uuid4())
        if document_id is None:
            document_id = str(uuid4())
        if storage_key is None:
            storage_key = f"documents/{document_id}/original"

        payload = {
            "event_id": event_id,
            "event_type": "DocumentCreated",
            "aggregate_type": "Document",
            "aggregate_id": document_id,
            "payload": {
                "document_id": document_id,
                "filename": filename,
                "content_type": content_type,
                "size_bytes": size_bytes,
                "storage_key": storage_key,
            },
        }

        message = Message(
            body=json.dumps(payload).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
        )
        await self.exchange.publish(message, routing_key="document.created")

    async def close(self):
        if self.connection:
            await self.connection.close()
