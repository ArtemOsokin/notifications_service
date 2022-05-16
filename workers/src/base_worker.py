import abc
from typing import Callable, Optional

from message_model import Queues


class BaseWorker:
    @abc.abstractmethod
    def connect_to_queue(self) -> None:
        """Встать на прослушивание очереди сообщений"""
        pass

    @abc.abstractmethod
    def do_action(self, data: bytes) -> None:
        """Выполнить действие"""
        pass

    @abc.abstractmethod
    def enrich_data(self) -> None:
        """Обогатить данные"""
        pass


class Enricher:
    @abc.abstractmethod
    def connect_to_source(self) -> None:
        """Подключиться к источнику данных"""
        pass

    @abc.abstractmethod
    def get_data(self, request) -> Optional[tuple]:
        """Получить данные"""
        pass


class MessageBroker:
    @abc.abstractmethod
    def connect_to_broker(self) -> None:
        """Подключиться к брокеру сообщений"""
        pass

    @abc.abstractmethod
    def connect_to_queue(self, queue: Queues, callback: Callable) -> None:
        """Подключиться к очереди сообщений"""
        pass
