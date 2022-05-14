import logging

from app.models.notify import ChannelsEnum, SenderEnum, CollectionEnum
from app.services.base_service import BaseNotificationService

logger = logging.getLogger(__name__)


class AuthMailingNotificationService(BaseNotificationService):
    channel = ChannelsEnum.email
    sender = SenderEnum.auth
    collection = CollectionEnum.auth_published_message
