import asyncio
from uuid import uuid4

from services.messaging import RabbitMQ


RABBITMQ_URL = "amqp://aria:aria@127.0.0.1:5672/%2f"


async def main():
    rabbit = RabbitMQ(RABBITMQ_URL)
    await rabbit.connect()
    await rabbit.declare_ingestion_queue()

    document_id = str(uuid4())
    event_id = str(uuid4())

    print("📤 [PUBLISHER] Sending document event package to RabbitMQ...")
    await rabbit.publish_document_created(
        event_id=event_id,
        document_id=document_id,
        filename="smoke_test.txt",
        content_type="text/plain",
        size_bytes=128,
        storage_key=f"documents/{document_id}/original",
    )
    print("📢 [PUBLISHER] Message routing complete.")
    await rabbit.close()


if __name__ == "__main__":
    asyncio.run(main())