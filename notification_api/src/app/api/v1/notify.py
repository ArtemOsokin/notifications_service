from logging import getLogger
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.core.oauth import get_user_id
from app.db.kafka_storage import KafkaStorageError
from app.models.notify import Notification
from app.services.notify import FilmUGCService, get_film_ugc_service

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
    notify_service: NotifyService = Depends(get_notify_service),
):
    try:
        await film_ugc_service.post(bookmark)
        return status.HTTP_202_ACCEPTED
    except KafkaStorageError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Storage not available',
        )
