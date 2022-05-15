import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_DSN: dict = {
        'dbname': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST'),
        'port': os.environ.get('DB_PORT'),
        'options': '-c search_path=public,content,notification'
    }

    NOTIFICATION_API_URL: str = 'http://notification_api:8080/api/v1/send_notification'
    AUTH_API_URL: str = 'http://auth-api:8088/api/v1/admin/'
    BATCH_SIZE = 100
    SLEEP_TIME = 5
    BACKOFF_MAX_TIME = 10
    CHUNK_SIZE = 10


settings = Settings()
