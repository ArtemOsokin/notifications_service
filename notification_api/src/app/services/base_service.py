import logging
from abc import ABC, abstractmethod

import orjson
import pika
from fastapi import HTTPException
from pika.exceptions import UnroutableError
from starlette import status

from app.core.config import settings
from app.db.rabbitmq import RabbitMQAdapter
from app.models.notify import ChannelsEnum, SenderEnum, CollectionEnum

logger = logging.getLogger(__name__)


class AbstractService(ABC):
    @abstractmethod
    def publish_to_queue(self, message: dict, routing_key: str, request_id: str) -> bool:
        """Метод публикации сообщения в очередь"""
        pass


class BaseNotificationService(AbstractService):
    channel: ChannelsEnum
    sender: SenderEnum
    collection: CollectionEnum

    def __init__(self, rabbitmq: RabbitMQAdapter):
        self.rabbitmq = rabbitmq

    def publish_to_queue(self, message: dict, routing_key: str, request_id: str) -> bool:
        headers = {
            'X-Request-Id': request_id,
            'sender': self.sender.value,
            'channel': self.channel.value,
        }
        properties = pika.BasicProperties(
            app_id='notification-api-publisher',
            content_type='application/json',
            headers=headers,
            delivery_mode=2,
        )
        try:
            self.rabbitmq.channel.basic_publish(
                exchange=settings.RABBIT.EXCHANGE,
                routing_key=routing_key,
                body=orjson.dumps(message),
                properties=properties,
                mandatory=True,
            )
            logger.info('Message %s was published', message)
            return True
        except UnroutableError as pika_error:
            logger.error('Message not was published. Queue publishing error: %s', pika_error)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
