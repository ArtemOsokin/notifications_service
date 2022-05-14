import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, Union
from uuid import UUID

from pydantic import Field, EmailStr, AnyHttpUrl, validator

from app.models.base import ORJSONModel


class SenderEnum(str, Enum):
    auth = 'auth'
    ugc = 'ugc'
    admin_panel = 'admin_panel'


class ChannelsEnum(str, Enum):
    email = 'email'
    sms = 'sms'
    websocket = 'websocket'
    push = 'push'


class PriorityEnum(str, Enum):
    high = 'high'
    medium = 'medium'
    low = 'low'


class CollectionEnum(str, Enum):
    admin_published_message = 'admin_published_message'
    auth_published_message = 'auth_published_message'
    ugc_published_message = 'ugc_published_message'


class AdminNotificationPayload(ORJSONModel):
    mailing_id: UUID = Field(..., description='Уникальный идентификатор задачи рассылки')
    total_chunk: int = Field(..., description='Количество частей уведомления задачи рассылки')
    chunk_id: int = Field(..., description='Номер текущей части уведомления задачи рассылки')
    is_promo: bool = Field(..., description='Флаг рекламной рассылки')
    priority: PriorityEnum = Field(..., description='Приоритет отправки уведомления')
    template_id: UUID = Field(..., description='Уникальный идентификатор шаблона уведомления')
    context: dict = Field({}, description='Статический контекст шаблона уведомления')
    user_ids: List[UUID] = Field(
        ...,
        description='Список уникальных идентификаторов пользователей - получателей '
        'уведомления',
    )


class AuthNotificationPayload(ORJSONModel):
    user_id: UUID = Field(..., description='Уникальный идентификатор пользователя')
    user_email: EmailStr = Field(..., description='Адрес электронной почты пользователя')
    username: str = Field(..., description='логин пользователя')
    first_name: Optional[str] = Field(None, description='имя пользователя')
    last_name: Optional[str] = Field(None, description='фамилия пользователя')
    token: str = Field(..., description='токен для подтверждения e-mail')
    callback_url: AnyHttpUrl = Field(
        ..., description='ccылка для подтверждения адреса электронной почты'
    )


class BaseNotification(ORJSONModel):
    id: UUID = Field(
        default_factory=uuid.uuid4,
        alias='_id',
        description='Уникальный идентификатор уведомления',
    )
    sender: SenderEnum = Field(..., description='Сервис, являющийся источником уведомления')
    template_type: str = Field(..., description='Вид шаблона уведомления')
    channel: ChannelsEnum = Field(..., description='Канал отправки уведомления пользователю')
    request_id: Optional[str] = Field(None, description='Request-ID запроса')
    payload: Union[AdminNotificationPayload, AuthNotificationPayload] = Field(
        ...,
        description='Содержание уведомления, состав и типы полей зависят от сервиса-источника',
    )
    created_at: datetime = Field(
        datetime.utcnow(), title='Время создания', description='Время создания уведомления'
    )

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True

    @validator('payload', pre=True)
    def build_payload(
        cls, v, values
    ) -> Union[AdminNotificationPayload, AuthNotificationPayload]:
        if values['sender'] == SenderEnum.auth.value:
            v = AuthNotificationPayload(**v)
        elif values['sender'] == SenderEnum.admin_panel.value:
            v = AdminNotificationPayload(**v)
        return v


#
# a = {
#     "sender": "auth",
#     "template_type": "wellcome_letter",
#     "channel": "email",
#     "request_id": "1234567",
#     "payload": {
#         "user_id": UUID("bc29d5e8-56b0-42cf-a872-b5cf8cda0489"),
#         "user_email": "test@example.com",
#         "username": "test_user",
#         "first_name": "first_name_user",
#         "last_name": "last_name_user",
#         "token": "token1234",
#         "callback_url": "http://auth/api/v1/confirm",
#     }
# }
