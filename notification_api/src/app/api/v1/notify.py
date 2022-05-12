from logging import getLogger

from fastapi import APIRouter
from starlette import status

from app.models.notify import Notification

logger = getLogger(__name__)

router = APIRouter()


@router.post(
    '/send_notification',
    summary='Отправка уведомления пользователям',
    description='Валидация, приоритизация, сохранение в базе данных и отправка уведомления в очередь для обработки '
                'воркерами',
    operation_id='sendNotification',
    status_code=status.HTTP_201_CREATED
)
async def notification_add(
    notification: Notification,
):
    pass