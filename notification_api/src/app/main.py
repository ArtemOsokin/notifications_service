import logging
from logging import config as logging_config
from urllib.parse import quote_plus as quote

import backoff
import pika
from pika import exceptions
import uvicorn as uvicorn
from fastapi import Depends, FastAPI
from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from app.api.v1 import notify
from app.core.backoff_handler import backoff_hdlr, backoff_hdlr_success
from app.core.config import settings
from app.core.logger import LOGGING
from app.core.oauth import decode_jwt
from app.db import mongodb
from app.jaeger_service import init_tracer

logging_config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    redoc_url='/api/redoc',
    default_response_class=ORJSONResponse,
)

init_tracer(app)

url = 'mongodb://{user}:{pw}@{hosts}/?authSource={auth_src}'.format(
    user=quote(settings.MONGO.DB_USER),
    pw=quote(settings.MONGO.DB_PASS),
    hosts=settings.MONGO.DB_HOSTS,
    auth_src=settings.MONGO.DB_NAME,
)


@app.on_event('startup')
async def startup_mongodb():
    mongodb.mongo_client = backoff.on_exception(
        wait_gen=backoff.expo,
        max_tries=settings.BACKOFF.RETRIES,
        max_time=settings.BACKOFF.MAX_TIME,
        exception=exceptions.AMQPConnectionError,
        on_backoff=backoff_hdlr,
        on_success=backoff_hdlr_success,
    )(AsyncIOMotorClient)(url, tlsCAFile=settings.MONGO.CACERT)


@app.on_event('startup')
def init_queue():
    global connection
    global channel

    credentials = pika.PlainCredentials(
        settings.RABBIT.USERNAME,
        settings.RABBIT.PASSWORD,
    )
    parameters = pika.ConnectionParameters(
        host=settings.RABBIT.HOST,
        port=settings.RABBIT.PORT,
        virtual_host='/',
        credentials=credentials,
        heartbeat=settings.RABBIT.HEARTBEAT,
        blocked_connection_timeout=settings.RABBIT.BLOCKED_CONNECTION_TIMEOUT
    )

    @backoff.on_exception(
        wait_gen=backoff.expo,
        max_tries=settings.BACKOFF.RETRIES,
        max_time=settings.BACKOFF.MAX_TIME,
        exception=exceptions.AMQPConnectionError,
        on_backoff=backoff_hdlr,
        on_success=backoff_hdlr_success,
    )
    def _connect():
        return pika.BlockingConnection(parameters=parameters)

    connection = _connect()
    channel = connection.channel()

    channel.exchange_declare(
        exchange=settings.RABBIT.EXCHANGE,
        exchange_type=settings.RABBIT.EXCHANGE_TYPE,
        durable=True,
    )
    channel.queue_declare(queue=settings.RABBIT.HIGH_EVENTS_QUEUE_NAME, durable=True)
    channel.queue_declare(queue=settings.RABBIT.MEDIUM_EVENTS_QUEUE_NAME, durable=True)
    channel.queue_declare(queue=settings.RABBIT.LOW_EVENTS_QUEUE_NAME, durable=True)

    logger.info('Connected to queues RabbitMQ')


@app.on_event('shutdown')
async def shutdown_mongodb():
    mongodb.mongo_client.close()


@app.on_event('shutdown')
def shutdown_event():
    logger.info('Close connection to queues RabbitMQ')
    connection.close()


app.include_router(
    notify.router,
    prefix='/api/v1/notifier',
    tags=['Сервис уведомлений'],
    dependencies=[Depends(decode_jwt)],
)

if __name__ == '__main__':
    uvicorn.run(
        'main:app', host='0.0.0.0', port=8080, log_config=LOGGING, log_level=logging.INFO,
    )
