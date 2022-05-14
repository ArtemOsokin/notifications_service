import logging
from functools import lru_cache
from typing import Optional

from pika import BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel

from app.core.base import Queues
from app.core.config import settings

connection: Optional[BlockingConnection] = None

logger = logging.getLogger(__name__)


class RabbitMQAdapter:
    channel: Optional[BlockingChannel] = None

    def __init__(self, conn: BlockingConnection):
        self.conn = conn
        self.channel = self.conn.channel()
        self.channel.exchange_declare(
            exchange=settings.RABBIT.EXCHANGE,
            exchange_type=settings.RABBIT.EXCHANGE_TYPE,
            durable=True,
        )
        for queue in Queues:
            self.channel.queue_declare(queue=queue.value, durable=True)
            self.channel.queue_bind(
                queue=queue.value,
                exchange=settings.RABBIT.EXCHANGE,
                routing_key=queue.routing_key,
            )
            logger.info(
                'Binding queue "%s" to exchange "%s" with routing_key "%s"',
                queue.value,
                settings.RABBIT.EXCHANGE,
                queue.routing_key,
            )
        logger.info('Connected to queues RabbitMQ')
        self.channel.confirm_delivery()


# type: ignore
@lru_cache
def get_rabbitmq() -> RabbitMQAdapter:
    return RabbitMQAdapter(connection)
