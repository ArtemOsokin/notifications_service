import asyncio
import logging
from functools import partial

from aio_pika import connect
from aio_pika.abc import AbstractIncomingMessage

from base_worker import MessageBroker
from message_model import Queues
from settings import rabbit_settings


class RabbitBroker(MessageBroker):
    def __init__(self):
        self.connection = None
        self.queue_callbacks = {}

    async def run(self):
        await self.connect_to_broker()

    async def connect_to_queue(self, queue: Queues, queue_callback) -> None:
        self.queue_callbacks[queue.value] = queue_callback
        loop = asyncio.get_event_loop()
        task = loop.create_task(self._connect_to_queue(queue))
        await task

    async def on_message(
        self, message: AbstractIncomingMessage, queue_name: str = None
    ) -> None:
        async with message.process():
            logging.debug(" [x] %r:%r" % (message.routing_key, message.body))
            logging.debug("on_message callback calls %s" % queue_name)
            await self.queue_callbacks[queue_name](message.body)

    async def connect_to_broker(self) -> None:
        # Perform connection
        self.connection = await connect(
            host=rabbit_settings.HOST,
            port=rabbit_settings.PORT,
            login=rabbit_settings.USERNAME,
            password=rabbit_settings.PASSWORD,
        )

    async def _connect_to_queue(self, queue: Queues) -> None:
        logging.info(" [ ] Connecting to queue %s...", queue.value)
        # Creating a channel
        channel = await self.connection.channel()
        await channel.set_qos(prefetch_count=1)

        # Declare an exchange
        direct_logs_exchange = await channel.declare_exchange(
            rabbit_settings.EXCHANGE, rabbit_settings.EXCHANGE_TYPE, durable=True
        )

        new_queue = await channel.declare_queue(name=queue.value, durable=True)
        await new_queue.bind(direct_logs_exchange, routing_key=queue.routing_key)
        await new_queue.consume(partial(self.on_message, queue_name=queue.value))

        logging.info(" [*] Connected to queue %s for messages.", queue.value)
        await asyncio.Future()
