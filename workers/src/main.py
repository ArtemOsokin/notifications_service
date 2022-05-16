import asyncio
import logging

import aiohttp
import aiopg
import orjson
from yarl import URL

from base_worker import BaseWorker
from base_worker import Enricher, MessageBroker
from html_render import render_html
from message_model import Queues
from rabbitmq import RabbitBroker
from sendgrid_service import SendGridMailer
from settings import postgres_settings, rest_api_settings
from websocket_module import WebSocketNotifier

LOGGER = logging.getLogger(__name__)


class PostgresEnricher(Enricher):
    def __init__(self):
        self.connection = None
        self.cursor = None

    async def connect_to_source(self) -> None:
        self.connection = await aiopg.connect(**postgres_settings)
        self.cursor = await self.connection.cursor()

    async def get_data(self, request) -> tuple:
        await self.cursor.execute(request)
        ret = await self.cursor.fetchall()
        return ret

    async def close_connection(self):
        self.connection.close()


class RESTEnricher:
    def __init__(self, base_url: URL):
        self._base_url = base_url
        self._client = aiohttp.ClientSession(raise_for_status=True)

    async def close(self) -> None:
        return await self._client.close()

    def _make_url(self, path: str) -> URL:
        return self._base_url / path

    async def fetch_data(self, url):
        async with self._client.get(self._make_url(url)) as resp:
            ret = await resp.json()
            return ret


class WelcomeEmailWorker(BaseWorker):
    def __init__(self, consumer: MessageBroker):
        self.consumer = consumer
        self.mailer = SendGridMailer()
        self.enricher = PostgresEnricher()

    async def connect_to_queue(self) -> None:
        await self.consumer.connect_to_queue(Queues.SEND_WELCOME, self.do_action)

    async def do_action(self, body) -> None:
        data_from_notification = orjson.loads(body)
        logging.debug(data_from_notification)
        template = await self.enrich_data()
        msg_content = await render_html(data_from_notification, template)

        await self.mailer.send_mail(
            "noreply@example.com",
            data_from_notification["payload"]["user_email"],
            "Добро пожаловать в Practix",
            msg_content,
        )

    async def enrich_data(self) -> str:
        await self.enricher.connect_to_source()
        html = await self.enricher.get_data(
            'SELECT html_template FROM "notification"."templates"'
            'WHERE template_type = "welcome_letter" AND channel = "email";'
        )
        await self.enricher.close_connection()
        return html[0]


class MailingWorker(BaseWorker):
    def __init__(self, consumer: MessageBroker):
        self.consumer = consumer
        self.mailer = SendGridMailer()
        self.enricher = PostgresEnricher()
        self.rest_enricher = RESTEnricher(rest_api_settings)
        self.template_id = None
        self.users = {}

    async def connect_to_queue(self) -> None:
        await self.consumer.connect_to_queue(Queues.SEND_MAILING_LOW, self.do_action)
        await self.consumer.connect_to_queue(Queues.SEND_MAILING_MEDIUM, self.do_action)
        await self.consumer.connect_to_queue(Queues.SEND_MAILING_HIGH, self.do_action)

    async def do_action(self, data) -> None:
        data_from_notification = orjson.loads(data)
        logging.debug(data_from_notification)
        self.template_id = data_from_notification["payload"]["template_id"]
        template = await self.enrich_data()
        for user_id in data_from_notification["payload"]["user_ids"]:
            user = await self.get_user_data(user_id)
            msg_content = await render_html(user, template)

            await self.mailer.send_mail(
                "noreply@example.com",
                user["email"],
                "Ежемесячная персональная статистика",
                msg_content,
            )

    async def get_user_data(self, user_id):
        try:
            user = await self.rest_enricher.fetch_data(f"user/{user_id}")
            return user
        finally:
            await self.rest_enricher.close()

    async def enrich_data(self) -> str:
        await self.enricher.connect_to_source()
        html = await self.enricher.get_data(
            f'SELECT html_template FROM "notification"."templates" WHERE id = {self.template_id};'
        )
        await self.enricher.close_connection()
        return html[0]


async def main():
    logging.basicConfig(level=logging.INFO)
    consumer = RabbitBroker()
    await consumer.run()
    welcome_worker = WelcomeEmailWorker(consumer)
    mailing_worker = MailingWorker(consumer)
    ws_notifier = WebSocketNotifier()
    await ws_notifier.connect()
    await welcome_worker.connect_to_queue()
    await mailing_worker.connect_to_queue()


if __name__ == "__main__":
    asyncio.run(main())
