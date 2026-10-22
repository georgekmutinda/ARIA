import asyncio

from core.database import SessionLocal
from data.repositories.outbox_repository import OutboxRepository
from services.messaging import RabbitMQ
from services.outbox_publisher import OutboxPublisher


RABBITMQ_URL = "amqp://aria:aria@localhost:5672/"


async def main():
    db = SessionLocal()

    rabbit = RabbitMQ(RABBITMQ_URL)

    try:
        await rabbit.connect()
        await rabbit.declare_ingestion_queue()

        repository = OutboxRepository(db)

        publisher = OutboxPublisher(
            repository=repository,
            rabbit=rabbit,
        )

        count = await publisher.publish_pending_events()

        print(f"Published {count} outbox event(s).")

    finally:
        await rabbit.close()
        db.close()


if __name__ == "__main__":
    asyncio.run(main())