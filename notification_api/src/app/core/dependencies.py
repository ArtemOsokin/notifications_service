from functools import lru_cache

from fastapi import Depends

from app.db.rabbitmq import get_rabbitmq, RabbitMQAdapter
from app.services.admin_mailing_service import AdminMailingNotificationService


@lru_cache
def get_admin_mailing_service(
    rabbitmq: RabbitMQAdapter = Depends(get_rabbitmq),
) -> AdminMailingNotificationService:
    return AdminMailingNotificationService(rabbitmq=rabbitmq)
