from base_worker import BaseWorker
from rabbitmq import RabbitBroker
from sendgrid_service import SendGridMailer
import logging
import asyncio
from websocket_module import WebSocketNotifier

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

class EmailWorker(BaseWorker):

    def __init__(self):
        self.amqp_url = 'amqp://guest:guest@localhost:5672/%2F'
        self.consumer = RabbitBroker(self.amqp_url, self.do_action)
        self.mailer = SendGridMailer()

    async def connect_to_queue(self) -> None:
        await self.consumer.run()

    async def do_action(self, body) -> None:
        if body.need_enrich:
            await self.enrich_data()
        self.mailer.send_mail(body.sender, body.recipient, body.subj, body.msg_content)

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

