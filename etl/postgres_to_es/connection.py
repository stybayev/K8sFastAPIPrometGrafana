from contextlib import contextmanager

import psycopg2
from config import DBParams
from psycopg2.extras import DictCursor


@contextmanager
def postgres_connection(params: DBParams):
    conn = psycopg2.connect(
        host=params.host,
        port=params.port,
        dbname=params.db,
        user=params.user,
        password=params.password,
        cursor_factory=DictCursor,
    )
    try:
        yield conn
    finally:
        conn.close()
