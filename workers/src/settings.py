from enum import Enum

from pydantic import BaseSettings, Field


class ExchangeTypeEnum(str, Enum):
    topic = "topic"
    direct = "direct"
    headers = "headers"
    fanout = "fanout"


class RabbitMQSettings(BaseSettings):
    USERNAME: str = Field("", description="Имя пользователя")
    PASSWORD: str = Field("", description="Пароль пользователя")
    HOST: str = Field("127.0.0.1", description="адрес хоста RabbitMQ")
    PORT: int = Field(5672, description="номер порта брокера RabbitMQ")
    HEARTBEAT: int = Field(
        600, description="Периодичность проверки состояния сервера RabbitMQ"
    )
    BLOCKED_CONNECTION_TIMEOUT: int = Field(
        300, description="Таймаут для блокирующего соединения"
    )
    EXCHANGE: str = Field("", description="Имя обменника RabbitMQ")
    EXCHANGE_TYPE: ExchangeTypeEnum = Field(
        ExchangeTypeEnum.direct, description="Тип обменника RabbitMQ"
    )

    class Config:
        env_prefix = "RABBIT_"
        env_file = ".env"
        use_enum_values = True


class PostgresSettings(BaseSettings):
    HOST: str = Field("127.0.0.1")
    PORT: str = Field("5432")
    BASE_NAME: str = Field("")
    USER: str = Field("")
    PASSWORD: str = Field("")

    class Config:
        env_prefix = "POSTGRES_"
        env_file = ".env"
        use_enum_values = True


class RESTApiSettings(BaseSettings):
    AUTH_API_URL: str = Field("http://auth-api:8088/api/v1/")

    class Config:
        env_prefix = "REST_"
        env_file = ".env"
        use_enum_values = True


postgres_settings = PostgresSettings()
rabbit_settings = RabbitMQSettings()
rest_api_settings = RESTApiSettings()
