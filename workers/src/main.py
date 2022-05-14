from base_worker import BaseWorker
from rabbitmq import RabbitBroker
from sendgrid_service import SendGridMailer
import logging
import asyncio

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

class EmailWorker(BaseWorker):

    def __init__(self):
        self.amqp_url = 'amqp://guest:guest@localhost:5672/%2F'
        self.consumer = RabbitBroker(self.amqp_url, self.do_action)
        self.mailer = SendGridMailer()

    async def connect_to_queue(self) -> None:
        self.consumer.run()

    async def do_action(self, body) -> None:
        if body.need_enrich:
            await self.enrich_data()
        self.mailer.send_mail(body.sender, body.recipient, body.subj, body.msg_content)

    async def enrich_data(self) -> None:
        pass


async def main():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    worker = EmailWorker()
    await worker.connect_to_queue()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    loop.run_forever()
    # loop.run_until_complete(main())
    # asyncio.run(main())

