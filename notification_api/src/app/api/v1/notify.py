from logging import getLogger

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse

from app.core.base import Queues
from app.core.dependencies import get_admin_mailing_service
from app.models.notify import BaseNotification, SenderEnum

logger = getLogger(__name__)

router = APIRouter()


@router.post(
    '/send_notification',
    summary='Отправка уведомления пользователям',
    description='Валидация, приоритизация, сохранение в базе данных и отправка уведомления в очередь для обработки '
    'воркерами',
    operation_id='sendNotification',
    status_code=status.HTTP_201_CREATED,
)
async def notification_add(
    notification: BaseNotification,
    request: Request,
    mailing_service=Depends(get_admin_mailing_service),
):
    global routing_key
    if notification.sender != SenderEnum.admin_panel.value:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='')
    if notification.request_id is None:
        notification.request_id = request.headers.get('X-Request-Id')
    if notification.payload.priority == 'high':
        routing_key = Queues.SEND_MAILING_HIGH.routing_key
    elif notification.payload.priority == 'medium':
        routing_key = Queues.SEND_MAILING_MEDIUM.routing_key
    elif notification.payload.priority == 'low':
        routing_key = Queues.SEND_MAILING_LOW.routing_key
    message = jsonable_encoder(notification)
    logger.info('Message: %s', message)
    if mailing_service.publish_to_queue(
        message=message, routing_key=routing_key, request_id=notification.request_id
    ):
        new_notification = await request.app.mongodb[
            mailing_service.collection.value
        ].insert_one(message)
        created_task = await request.app.mongodb[mailing_service.collection.value].find_one(
            {'_id': new_notification.inserted_id}
        )

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_task)
