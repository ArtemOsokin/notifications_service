from logging import getLogger

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse

from app.core.base import Queues
from app.core.dependencies import get_admin_mailing_service, get_auth_mailing_service
from app.models.notify import BaseNotification, SenderEnum

logger = getLogger(__name__)

router = APIRouter()


@router.post(
    '/send_notification',
    summary='Отправка на обработку уведомлений по рассылкам, создаваемых администратором',
    description='Валидация, приоритизация, сохранение в базе данных и отправка уведомления в очередь для обработки '
    'воркерами',
    operation_id='sendAdminNotification',
    status_code=status.HTTP_201_CREATED,
)
async def mailing_notification_add(
    notification: BaseNotification,
    request: Request,
    mailing_service=Depends(get_admin_mailing_service),
):
    if notification.sender != SenderEnum.admin_panel.value:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail='Endpoint only for mailing notifications created by the manager',
        )

    global routing_key
    # Проверка повторного направления ранее отправленного уведомления. Проверка наивная, без учета, что может измениться
    # состав user_id в чанках
    notification_ = await request.app.mongodb[mailing_service.collection.value].find_one(
        {'payload.mailing_id': str(notification.payload.mailing_id)}
    )
    if notification_ and (
        notification_['payload']['total_chunk'] == notification.payload.total_chunk
        and notification_['payload']['chunk_id'] == notification.payload.chunk_id  # noqa
    ):
        logger.debug('Notification in db: %s', notification_)
        raise HTTPException(
            status.HTTP_208_ALREADY_REPORTED,
            detail='Such a mailing notification has already been sent earlier',
        )

    if notification.request_id is None:
        notification.request_id = request.headers.get('X-Request-Id')
    if notification.payload.priority == 'high':
        routing_key = Queues.SEND_MAILING_HIGH.routing_key
    elif notification.payload.priority == 'medium':
        routing_key = Queues.SEND_MAILING_MEDIUM.routing_key
    elif notification.payload.priority == 'low':
        routing_key = Queues.SEND_MAILING_LOW.routing_key

    message = jsonable_encoder(notification)
    logger.debug('Message: %s', message)
    if mailing_service.publish_to_queue(
        message=message, routing_key=routing_key, request_id=notification.request_id
    ):
        new_notification = await request.app.mongodb[
            mailing_service.collection.value
        ].insert_one(message)
        created_notification = await request.app.mongodb[
            mailing_service.collection.value
        ].find_one({'_id': new_notification.inserted_id})
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_notification)

    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post(
    '/user_registration',
    summary='Отправка сообщений от сервиса авторизации',
    description='Валидация, приоритизация, сохранение в базе данных и отправка уведомления в очередь для обработки '
    'воркерами',
    operation_id='sendAuthNotification',
    status_code=status.HTTP_201_CREATED,
)
async def auth_notification_add(
    notification: BaseNotification,
    request: Request,
    mailing_service=Depends(get_auth_mailing_service),
):
    if notification.sender != SenderEnum.auth.value:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail='Endpoint only for mailing notifications authorization service',
        )

    # Проверка повторного направления ранее отправленного уведомления.
    notification_ = await request.app.mongodb[mailing_service.collection.value].find_one(
        {
            'payload.user_id': str(notification.payload.user_id),
            'payload.token': notification.payload.token,
        }
    )
    if notification_:
        logger.debug('Notification in db: %s', notification_)
        raise HTTPException(
            status.HTTP_208_ALREADY_REPORTED,
            detail='The notification with the id <{0}> has already been sent for processing: {1}'.format(
                notification_['_id'], notification_['created_at'],
            ),
        )

    if notification.request_id is None:
        notification.request_id = request.headers.get('X-Request-Id')
    routing_key = Queues.SEND_WELCOME.routing_key
    message = jsonable_encoder(notification)
    logger.debug('Message: %s', message)
    if mailing_service.publish_to_queue(
        message=message, routing_key=routing_key, request_id=notification.request_id
    ):
        new_notification = await request.app.mongodb[
            mailing_service.collection.value
        ].insert_one(message)
        created_notification = await request.app.mongodb[
            mailing_service.collection.value
        ].find_one({'_id': new_notification.inserted_id})
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_notification)

    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
