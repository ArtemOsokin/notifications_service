import logging

from app.models.notify import ChannelsEnum, SenderEnum, CollectionEnum
from app.services.base_service import BaseNotificationService

logger = logging.getLogger(__name__)


class AdminMailingNotificationService(BaseNotificationService):
    channel = ChannelsEnum.email
    sender = SenderEnum.admin_panel
    collection = CollectionEnum.admin_published_message
