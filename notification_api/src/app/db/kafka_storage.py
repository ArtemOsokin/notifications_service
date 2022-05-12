import asyncio
import logging
import ssl
from abc import ABC, abstractmethod
from typing import Any, Optional

import backoff
from aiokafka import AIOKafkaProducer
from kafka.errors import KafkaError, RequestTimedOutError

from app.core.backoff_handler import backoff_hdlr, backoff_hdlr_success
from app.core.config import settings

logger = logging.getLogger(__name__)

if settings.KAFKA.RUN_IN_YANDEX_CLOUD:
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=settings.KAFKA.PATH_CERTIFICATE)


class KafkaProducer:
    _instance: Optional[AIOKafkaProducer] = None

    @property
    def instance(self) -> AIOKafkaProducer:
        if not self._instance:
            if not settings.KAFKA.RUN_IN_YANDEX_CLOUD:
                self._instance = AIOKafkaProducer(
                    loop=asyncio.get_event_loop(),
                    client_id=settings.KAFKA.CLIENT_ID,
                    bootstrap_servers=f'{settings.KAFKA.HOST}:{settings.KAFKA.PORT}',
                    request_timeout_ms=settings.KAFKA.PRODUCER_TIMEOUT_MS,
                )
            else:
                self._instance = AIOKafkaProducer(
                    loop=asyncio.get_event_loop(),
                    client_id=settings.KAFKA.CLIENT_ID,
                    bootstrap_servers=f'{settings.KAFKA.HOST_YC}:{settings.KAFKA.PORT_YC}',
                    request_timeout_ms=settings.KAFKA.PRODUCER_TIMEOUT_MS,
                    security_protocol=settings.KAFKA.SECURITY_PROTOCOL,
                    sasl_mechanism=settings.KAFKA.SASL_MECHANISM,
                    sasl_plain_password=settings.KAFKA.PRODUCER_PASSWORD,
                    sasl_plain_username=settings.KAFKA.PRODUCER_USERNAME,
                    ssl_context=ssl_context,
                )
        return self._instance


kafka_producer = KafkaProducer()


class KafkaStorageError(Exception):
    pass


class AbstractStorage(ABC):
    @abstractmethod
    async def send(self, topic, key, value) -> Any:
        pass


class KafkaStorage(AbstractStorage):
    conn: KafkaProducer

    def __init__(self) -> None:
        self.kafka_producer: AIOKafkaProducer = kafka_producer.instance

    @backoff.on_exception(
        wait_gen=backoff.expo,
        max_tries=settings.BACKOFF.RETRIES,
        max_time=settings.BACKOFF.MAX_TIME,
        exception=RequestTimedOutError,
        on_backoff=backoff_hdlr,
        on_success=backoff_hdlr_success,
    )
    async def send(self, topic, key, value):
        try:
            await self.kafka_producer.send(topic=topic, key=key, value=value)
        except RequestTimedOutError as timeout_error:
            logger.error('TimedOutError when adding a message %s to the topic %s', value, topic, repr(timeout_error))
            raise timeout_error
        except KafkaError as queue_error:
            logger.error('KafkaError when adding a message %s to the topic %s', value, topic, repr(queue_error))
            return
        logger.debug('Successfully sent a message %s to the topic %s', value, topic)


def get_storage() -> AbstractStorage:
    return KafkaStorage()









