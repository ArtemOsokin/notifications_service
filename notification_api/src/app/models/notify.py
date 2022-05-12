# type: ignore

import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.models.base import ORJSONModel


class Notification(ORJSONModel):
    _notification_id: UUID = Field(uuid.uuid4(), description='Уникальный идентификатор уведомления')
    mailing_id: Optional[UUID] = Field(None, description='Уникальный идентификатор задачи рассылки')
    total_chunk: int = Field(..., description='Количество частей уведомления задачи рассылки')
    chunk_id: int = Field(..., description='Номер текущей части уведомления задачи рассылки')
    title: Optional[str] = Field(None, description='Наименование задачи рассылки')
    is_promo: bool = Field(..., description='Флаг рекламной рассылки')
    priority: str = Field(..., description='Приоритет отправки уведомления')
    template_id: UUID = Field(..., description='Уникальный идентификатор шаблона уведомления')
    context: dict = Field({}, description='Статический контекст шаблона уведомления')
    user_ids: list[UUID] = Field(..., description='Список уникальных идентификаторов пользователей - получателей '
                                                  'уведомления')
    _created_at: datetime = Field(
        datetime.utcnow(), title='Время создания', description='Время создания уведомления'
    )

