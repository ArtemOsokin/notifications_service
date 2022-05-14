from pydantic import (AnyUrl, BaseSettings, Field, PostgresDsn, RedisDsn,
                      validator)


class BaseDSNSettings(BaseSettings):
    USER: str = Field('postgres', description='Имя пользователя источника данных')
    PASSWORD: str = Field('postgres', description='Пароль пользователя источника данных')
    HOST: str = Field('127.0.0.1', description='Имя хоста источника данных')
    PORT: int = Field(5432, description='Номер порта источника данных')
    PROTOCOL: str = Field(
        'postgresql', description='Используемый протокол для подключения к источнику данных'
    )
    PATH: str = Field('', description='Путь к ресурсу источника данных')
    DSN: AnyUrl = None

    @validator('DSN', pre=True)
    def build_dsn(cls, v, values) -> str:
        if v:
            return v

        user = values['USER']
        password = values['PASSWORD']
        host = values['HOST']
        port = values['PORT']
        protocol = values['PROTOCOL']
        path = values['PATH']

        if user and password:
            return f'{protocol}://{user}:{password}@{host}:{port}/{path}'

        return f'{protocol}://{host}:{port}/{path}'


class RedisSettings(BaseDSNSettings):
    HOST: str = Field('127.0.0.1', description='Имя хоста с БД REDIS')
    PORT: int = Field(6379, description='Номер порта для подключения к REDIS')
    PROTOCOL: str = Field('redis', description='Протокол (драйвер)')
    DSN: RedisDsn = Field(None, description='Строка подключения к REDIS')

    class Config:
        env_prefix = 'REDIS_'


class DatabaseSettings(BaseDSNSettings):
    PROTOCOL: str = Field('postgresql', description='Протокол (драйвер)')
    DSN: PostgresDsn = Field(None, description='Строка подключения к Postgresql')
    SCHEMA: str = Field('auth', description='Имя используемой схемы базы данных')

    class Config:
        env_prefix = 'DB_'


class JWTSettings(BaseSettings):
    SECRET_KEY: str = Field('big_secret_team8', description='Секретный ключ JWT')
    ACCESS_TOKEN_EXPIRES: int = Field(20, description='Время жизни access-токена в минутах.')
    REFRESH_TOKEN_EXPIRES: int = Field(
        60 * 24 * 30, description='Время жизни refresh-токена в минутах.'
    )

    class Config:
        env_prefix = 'JWT_'


class SecuritySettings(BaseSettings):
    SECRET_KEY: str = Field('Dft5&#jP)*^HbCv@', description='Секретный ключ приложения')
    DEFAULT_ADMIN_EMAIL: str = Field(
        'admin@test.ru', description='Логин администратора по умолчанию'
    )
    DEFAULT_ADMIN_PASSWORD: str = Field(
        '#Super1234#', description='Пароль администратора по умолчанию'
    )
    DEFAULT_ADMIN_USERNAME: str = Field(
        'super_test', description='Пароль администратора по умолчанию'
    )

    class Config:
        env_prefix = 'SECURITY_'


class CacheSettings(BaseSettings):
    TTL: int = Field(60 * 60 * 3, description='Время кеширования')

    class Config:
        env_prefix = 'CACHE_'


class PaginationSettings(BaseSettings):
    PAGE_NUMBER: int = Field(1, description='Номер страницы по умолчанию при пагинации')
    PAGE_SIZE: int = Field(10, description='Количество объектов на странице по умолчанию')

    class Config:
        env_prefix = 'PAGINATION_'


class WSGISettings(BaseSettings):
    """Используются для задания конфигурации при запуске WSGI сервера приложения"""

    app: str = Field('app.main:app', description='Путь к экземпляру приложения')
    HOST: str = Field('0.0.0.0', description='Адрес хоста')
    PORT: int = Field(8088, description='Порт хоста')
    workers: int = 4

    class Config:
        env_prefix = 'WSGI_'


class LimiterSettings(BaseSettings):
    """Используется для задания конфигурации для RATE LIMIT"""

    RATELIMIT_DEFAULT: str = Field(
        '10/second;100/hour;400/day',
        description='Значение по умолчанию для ограничения скорости',
    )
    RATELIMIT_HEADERS_ENABLED: bool = Field(
        True, description='Позволяет возвращать заголовки с ограничением скорости'
    )


class GoogleSettings(BaseSettings):
    CLIENT_ID: str = Field('', description='ID приложения в OAuth Google')
    CLIENT_SECRET: str = Field('', description='Пароль приложения в OAuth Google')
    SERVER_METADATA_URL: str = Field(
        '', description='URL OpenID Connect Discovery Endpoint Google'
    )

    class Config:
        env_prefix = 'OAUTH_GOOGLE_'


class YandexSettings(BaseSettings):
    CLIENT_ID: str = Field('', description='ID приложения в OAuth Yandex')
    CLIENT_SECRET: str = Field('', description='Пароль приложения в OAuth Yandex')
    API_BASE_URL: str = Field(
        '', description='Конечная точка базового URL-адреса для упрощения запросов'
    )
    ACCESS_TOKEN_URL: str = Field(
        '', description='URL-адрес для запроса access-токена по логину и пароля'
    )
    AUTHORIZE_URL: str = Field('', description='URL-адрес для запроса кода подтверждения')
    USERINFO_ENDPOINT: str = Field(
        '', description='URL-адрес c информацией userinfo (OpenID Connect)'
    )

    class Config:
        env_prefix = 'OAUTH_YANDEX_'


class TracingSettings(BaseSettings):
    AGENT_HOST_NAME: str = Field('127.0.0.1', description='адрес хоста агента Jaeger')
    AGENT_PORT: int = Field(6831, description='номер порта агента Jaeger')
    ENABLED: bool = Field(False, description='Флаг влк./откл. трассировки')

    class Config:
        env_prefix = 'JAEGER_'


class OAuthSettings(BaseSettings):
    GOOGLE: GoogleSettings = GoogleSettings()
    YANDEX: YandexSettings = YandexSettings()


class CommonSettings(BaseSettings):
    FLASK_APP: str = 'app.main:app'
    DEBUG: bool = Field(True, description='Флаг режима отладки')
    TESTING: bool = Field(False, description='Флаг режима тестирования')
    LOG_LEVEL: str = Field('INFO', description='Уровень сообщений лога')

    REDIS: RedisSettings = RedisSettings()
    DB: DatabaseSettings = DatabaseSettings()
    JWT: JWTSettings = JWTSettings()
    SECURITY: SecuritySettings = SecuritySettings()
    CACHE: CacheSettings = CacheSettings()
    PAGINATION: PaginationSettings = PaginationSettings()
    WSGI: WSGISettings = WSGISettings()
    LIMITER: LimiterSettings = LimiterSettings()
    OAUTH: OAuthSettings = OAuthSettings()
    JAEGER: TracingSettings = TracingSettings()
