import copy
import logging
import time
from typing import List, Generator
from uuid import UUID

import backoff
import requests

from config import settings
from db import Extractor
from models.models import Event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def partitions(list_name, step):
    for i in range(0, len(list_name), step):
        yield list_name[i: i + step]


class Scheduler:
    def __init__(self, extractor: Extractor):
        self.extractor = extractor

    @staticmethod
    def _chunker(event: Event) -> Generator[Event, None, None]:
        for part in partitions(event.user_ids, settings.CHUNK_SIZE):
            new_event = copy.deepcopy(event)
            new_event.user_ids = part
            yield new_event

    @backoff.on_exception(backoff.expo, requests.exceptions.ConnectionError,
                          max_time=settings.BACKOFF_MAX_TIME)
    def get_user_ids(self, user_categories: List[str]) -> List[str]:
        ids = []

        for category in user_categories:
            response = requests.get(settings.AUTH_API_URL + category)
            response.raise_for_status()

            data = response.json()
            ids.extend([user['id'] for user in data['users']])
        return ids

    def mark_event_as_in_processing(self, item_id: UUID):
        query = f"""update mailing_tasks
                           set status = 'In processing',
                           execution_datetime = current_timestamp
                           where id = {item_id}"""

        self.extractor.extract(query)

    def mark_event_as_cancel(self, item_id: UUID):
        query = f"""update mailing_tasks
                           set status = 'Cancel',
                           execution_datetime = current_timestamp
                           where id = {item_id};"""

        self.extractor.extract(query)

    def build_events(self, items: list) -> List[Event]:
        events = []

        for item in items:
            context = item['context']
            try:
                user_ids = context['user_ids']
                del context['user_ids']
            except KeyError:
                user_ids = []
            try:
                user_categories = context['user_categories']
                del context['user_categories']
            except KeyError:
                user_categories = []
            item['context'] = context
            event = Event(
                **item,
                user_ids=user_ids,
                user_categories=user_categories,
            )
            events.append(event)

        return events

    def get_ready_events(self) -> List[Event]:
        query = f"""select id, is_promo, priority, context, scheduled_datetime, template_id from mailing_tasks
                           where scheduled_datetime < current_timestamp
                           and status = 'Pending'
                           order by scheduled_datetime
                           limit {settings.BATCH_SIZE};"""

        items = self.extractor.extract(query)
        return self._build_events(items)

    @backoff.on_exception(backoff.expo, requests.exceptions.HTTPError,
                          max_time=settings.BACKOFF_MAX_TIME)
    def load(self, data):
        data = {'event': data}
        response = requests.post(settings.NOTIFICATION_API_URL, json=data)
        response.raise_for_status()

    def run(self):
        events = self.get_ready_events()
        for event in events:

            user_ids = self.get_user_ids(event.user_categories)
            event.user_ids.extend(user_ids)
            event.user_ids = list(set(user_ids))

            if not event.user_ids:
                self.mark_event_as_cancel(event.id)
                continue
            for chunk in self._chunker(event):
                self.load(chunk.dict(exclude={'user_categories'}))

            self.mark_event_as_in_processing(event.id)


def main():
    scheduler = Scheduler(Extractor())

    while True:
        scheduler.run()
        time.sleep(settings.SLEEP_TIME)


if __name__ == '__main__':
    main()
