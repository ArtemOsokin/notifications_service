import asyncio
import logging
import os

import orjson

from base_worker import BaseWorker
from rabbitmq import RabbitBroker
from sendgrid_service import SendGridMailer
from websocket_module import WebSocketNotifier

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

class EmailWorker(BaseWorker):

    def __init__(self):
        rabbit_host = os.environ.get('RABBIT_HOST')
        self.amqp_url = 'amqp://rabbit:rabbit_password@notification_rabbitmq:5672/%2F'
        self.consumer = RabbitBroker(self.amqp_url, self.do_action)
        self.mailer = SendGridMailer()

    async def connect_to_queue(self) -> None:
        await self.consumer.run()

    async def do_action(self, body) -> None:
        notification = orjson.loads(body)
        if notification.need_enrich:
            await self.enrich_data()
        await self.mailer.send_mail(notification.payoad.sender,
                                    notification.payoad.user_email,
                                    notification.subj,
                                    notification.msg_content)

    async def enrich_data(self) -> None:
        pass


async def main():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    worker = EmailWorker()
    ws_notifier = WebSocketNotifier()
    await ws_notifier.connect()
    await worker.connect_to_queue()

if __name__ == '__main__':
    asyncio.run(main())

