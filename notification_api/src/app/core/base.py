import logging
from enum import Enum

from pydantic import BaseSettings, Field

logger = logging.getLogger(__name__)


class APPSettings(BaseSettings):
    PROJECT_NAME: str = Field('Notification-service', description='Имя проекта')

    class Config:
        env_prefix = 'APP_'
        env_file = '.env'


class TracingSettings(BaseSettings):
    AGENT_HOST_NAME: str = Field('127.0.0.1', description='адрес хоста агента Jaeger')
    AGENT_PORT: int = Field(6831, description='номер порта агента Jaeger')
    ENABLED: bool = Field(False, description='Флаг влк./откл. трассировки')

    class Config:
        env_prefix = 'JAEGER_'


class AuthSettings(BaseSettings):
    SECRET_KEY: str = Field('super_big_secret', description='Секретный ключ JWT')
    ALGORITHM: str = Field('HS256', description='Алгоритм шифрования')

    class Config:
        env_prefix = 'AUTH_'


class BackoffSettings(BaseSettings):
    RETRIES: int = Field(
        5, description='количество повторных попыток подключения к внешним сервисам'
    )
    TTS: int = Field(2, description='Время ожидания до следующей попытки в секундах')
    MAX_TIME: int = Field(120, description='Максимальное время ожидания для попытки')

    class Config:
        env_prefix = 'BACKOFF_'
        env_file = '.env'


class MongoDBSettings(BaseSettings):
    DB_USER: str = Field('', description='Имя пользователя')
    DB_PASS: str = Field('', description='Пароль пользователя')
    DB_HOSTS: str = Field('', description='Список хостов Mongos')
    DB_NAME: str = Field('', description='Имя базы данных MongoDB')
    CACERT: str = Field('', description='Путь к файлу сертификата SSL')

    class Config:
        env_prefix = 'MONGO_'
        env_file = '.env'


class ExchangeTypeEnum(str, Enum):
    topic = 'topic'
    direct = 'direct'
    headers = 'headers'
    fanout = 'fanout'


class RabbitMQSettings(BaseSettings):
    USERNAME: str = Field('', description='Имя пользователя')
    PASSWORD: str = Field('', description='Пароль пользователя')
    HOST: str = Field('127.0.0.1', description='адрес хоста RabbitMQ')
    PORT: int = Field(5672, description='номер порта брокера RabbitMQ')
    HEARTBEAT: int = Field(600, description='Периодичность проверки состояния сервера RabbitMQ')
    BLOCKED_CONNECTION_TIMEOUT: int = Field(300, description='Таймаут для блокирующего соединения')
    EXCHANGE: str = Field('', description='Имя обменника RabbitMQ')
    EXCHANGE_TYPE: ExchangeTypeEnum = Field(ExchangeTypeEnum.direct, description='Тип обменника RabbitMQ')

    class Config:
        env_prefix = 'RABBIT_'
        env_file = '.env'
        use_enum_values = True


class RedisSettings(BaseSettings):
    HOST: str = Field('127.0.0.1', description='Адрес хоста DB Redis')
    PORT: str = Field(6379, description='Порт хоста DB Redis')

    class Config:
        env_prefix = 'REDIS_'
        env_file = '.env'


class CommonSettings(BaseSettings):
    LOG_LEVEL: str = Field('INFO', description='Уровень логирования сервисов приложения')
    APP: APPSettings = APPSettings()
    JAEGER: TracingSettings = TracingSettings()
    AUTH: AuthSettings = AuthSettings()
    BACKOFF: BackoffSettings = BackoffSettings()
    MONGO: MongoDBSettings = MongoDBSettings()
    RABBIT: RabbitMQSettings = RabbitMQSettings()
    REDIS: RedisSettings = RedisSettings()


# Список кортежей из значений ('имя очереди RabbitMQ', 'ключ маршрутизации')
queues = [
    ('emails.send-welcome', 'user.create.profile'),  # очередь для писем подтверждения e-mail при регистрации
    ('emails.send-mailing.high', 'mailing.create.important.event'),  # очередь для писем с важными сообщениями
    ('emails.send-mailing.low', 'mailing.create.promo.event'),  # очередь для писем рекламных рассылок
]