from functools import lru_cache

from fastapi import Depends

from app.db.rabbitmq import get_rabbitmq, RabbitMQAdapter
from app.services.admin_mailing_service import AdminMailingNotificationService
from app.services.auth_mailing_service import AuthMailingNotificationService


@lru_cache
def get_admin_mailing_service(
    rabbitmq: RabbitMQAdapter = Depends(get_rabbitmq),
) -> AdminMailingNotificationService:
    return AdminMailingNotificationService(rabbitmq=rabbitmq)


@lru_cache
def get_auth_mailing_service(
    rabbitmq: RabbitMQAdapter = Depends(get_rabbitmq),
) -> AuthMailingNotificationService:
    return AuthMailingNotificationService(rabbitmq=rabbitmq)
