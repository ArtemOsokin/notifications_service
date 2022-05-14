from config import settings
import psycopg2
from psycopg2.extras import DictCursor


class Extractor:

    def extract(self, sql):
        with psycopg2.connect(dsn=settings.DB_DSN, cursor_factory=DictCursor) as connection:
            with connection.cursor() as cur:
                cur.execute(sql)
                try:
                    data = [dict(item) for item in cur.fetchall()]
                except psycopg2.ProgrammingError:
                    data = None
        return data
