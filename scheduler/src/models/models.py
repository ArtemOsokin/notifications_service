from enum import Enum
from datetime import datetime
from uuid import UUID
from typing import Any, Dict, List, Optional

from pydantic.main import BaseModel


class Priority(Enum):
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'


class TimeStampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime


class Event(TimeStampMixin):
    id: UUID
    service: str
    title: str
    type_mailing: str
    status: str
    is_promo: bool
    priority: Priority
    template: UUID
    user_ids: Optional[List[str]]
    user_categories: Optional[List[str]]
    context: Dict[str, Any]
    scheduled_datetime: datetime
    execution_datetime: datetime

    class Config:
        use_enum_values = True
