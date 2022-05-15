import asyncio
import sys

from aio_pika import ExchangeType, connect
from aio_pika.abc import AbstractIncomingMessage

from base_worker import MessageBroker
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
        connection = await connect("amqp://guest:guest@localhost/")

        async with connection:
            # Creating a channel
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)

            # Declare an exchange
            direct_logs_exchange = await channel.declare_exchange(
                self.EXCHANGE, self.EXCHANGE_TYPE,
            )

            # Declaring random queue
            queue = await channel.declare_queue(durable=True)

            await queue.bind(direct_logs_exchange, routing_key="low")
            await queue.bind(direct_logs_exchange, routing_key="medium")
            await queue.bind(direct_logs_exchange, routing_key="high")

            # Start listening the random queue
            await queue.consume(self.on_message)

            print(" [*] Waiting for messages. To exit press CTRL+C")
            await asyncio.Future()