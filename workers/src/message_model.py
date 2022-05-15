from __future__ import annotations

from pydantic import BaseModel
from enum import IntEnum, Enum

class Queues(str, Enum):
    # Declaring the additional attributes here keeps mypy happy.
    routing_key: str
    description: str

    def __new__(cls, queue_name: str, routing_key: str = "", description: str = "") -> Queues:

        obj = str.__new__(cls, queue_name)
        obj._value_ = queue_name

        obj.routing_key = routing_key
        obj.description = description
        return obj

    SEND_WELCOME = (
        'emails.send-welcome',
        'user.create.profile',
        'очередь для писем подтверждения e-mail при регистрации',
    )
    SEND_MAILING_HIGH = (
        'emails.send-mailing.high',
        'mailing.create.important.event',
        'очередь для писем с важными сообщениями',
    )
    SEND_MAILING_MEDIUM = (
        'emails.send-mailing.medium',
        'mailing.create.common.event',
        'очередь для писем с обычной важностью',
    )
    SEND_MAILING_LOW = (
        'emails.send-mailing.low',
        'mailing.create.promo.event',
        'очередь для писем рекламных рассылок',
    )

class Message(BaseModel):
    pass
