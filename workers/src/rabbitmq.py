import asyncio
import sys

from aio_pika import ExchangeType, connect
from aio_pika.abc import AbstractIncomingMessage

from base_worker import MessageBroker
from message_model import Queues

import logging

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

class RabbitBroker(MessageBroker):

    EXCHANGE = 'email'
    EXCHANGE_TYPE = ExchangeType.DIRECT
    QUEUE = 'text'
    ROUTING_KEY = 'example.text'

    def __init__(self, amqp_url, action_cb):
        self.action_cb = action_cb
        self._reconnect_delay = 0
        self._amqp_url = amqp_url

    async def run(self):
        await self.connect_to_broker()

    async def on_message(self, message: AbstractIncomingMessage) -> None:
        async with message.process():
            print(" [x] %r:%r" % (message.routing_key, message.body))
            await self.action_cb(message.body)


    async def connect_to_broker(self) -> None:
        # Perform connection
        connection = await connect(self._amqp_url)

        async with connection:
            # Creating a channel
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)

            # Declare an exchange
            direct_logs_exchange = await channel.declare_exchange(
                self.EXCHANGE, self.EXCHANGE_TYPE,
            )

            for queue in Queues:
                new_queue = await channel.declare_queue(name=queue.value, durable=True)
                await new_queue.bind(direct_logs_exchange, routing_key=queue.routing_key)
                await new_queue.consume(self.on_message)

            print(" [*] Waiting for messages.")
            await asyncio.Future()