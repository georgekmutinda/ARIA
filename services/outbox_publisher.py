import json

import aio_pika
from aio_pika import Message

from data.repositories.outbox_repository import OutboxRepository
from services.messaging import RabbitMQ


class OutboxPublisher:

    def __init__(
        self,
        repository: OutboxRepository,
        rabbit: RabbitMQ,
    ) -> None:
        self.repository = repository
        self.rabbit = rabbit

    async def publish_pending_events(self) -> int:
        events = self.repository.get_pending_events()

        published_count = 0

        for event in events:
            payload = {
                "event_id": str(event.id),
                "event_type": event.event_type,
                "aggregate_type": event.aggregate_type,
                "aggregate_id": str(event.aggregate_id),
                "payload": event.payload,
            }

            message = Message(
                body=json.dumps(payload).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                message_id=str(event.id),
                content_type="application/json",
            )

            routing_key = self._get_routing_key(event.event_type)

            await self.rabbit.exchange.publish(
                message,
                routing_key=routing_key,
            )

            event.published_at = event.created_at

            published_count += 1

        self.repository.db.commit()

        return published_count

    @staticmethod
    def _get_routing_key(event_type: str) -> str:
        routing_keys = {
            "DocumentCreated": "document.created",
        }

        try:
            return routing_keys[event_type]
        except KeyError:
            raise ValueError(
                f"Unsupported event type: {event_type}"
            )