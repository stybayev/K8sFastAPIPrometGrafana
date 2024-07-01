import logging
from datetime import datetime

from psycopg2.extensions import connection as _connection


class PostgresExtractor:
    """В этом классе данные, полученные из Postgres, преобразуются во внутренний формат."""

    def __init__(self, connection: _connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.related_cursor = connection.cursor()
        self.log = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def get_filmworks_query(filter_query: str = "") -> str:
        query = """
            SELECT
            fw.id,
            fw.title,
            fw.description,
            fw.rating AS imdb_rating,
            fw.type,
            fw.file,
            fw.label,
            fw.created,
            fw.modified,
            COALESCE (
               json_agg(
                   DISTINCT jsonb_build_object(
                       'person_role', pfw.role,
                       'person_id', p.id,
                       'person_name', p.full_name
                   )
               ) FILTER (WHERE p.id is not null),
               '[]'
            ) as persons,
            array_agg(DISTINCT g.name) as genres
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            {}
            GROUP BY fw.id, fw.title, fw.description, fw.rating, fw.type, fw.file, fw.label, fw.created, fw.modified
            ORDER BY fw.modified
        """.format(
            filter_query,
        )

        return query

    @staticmethod
    def get_persons_filmworks_query(filter_query: str = "") -> str:
        query = """
            SELECT
            p.id,
            p.modified,
            pfw.film_work_id
            FROM content.person p
            LEFT JOIN content.person_film_work pfw ON p.id = pfw.person_id
            {}
            ORDER BY p.modified
        """.format(
            filter_query,
        )

        return query

    @staticmethod
    def get_persons_query(filter_query: str = "") -> str:
        query = """
            SELECT DISTINCT
            p.id,
            p.full_name,
            p.modified
            FROM content.person p
            JOIN content.person_film_work pfw ON p.id = pfw.person_id
            {}
            ORDER BY p.modified
        """.format(
            filter_query,
        )

        return query

    @staticmethod
    def get_genres_filmworks_query(filter_query: str = "") -> str:
        query = """
            SELECT
            g.id,
            g.modified,
            gfw.film_work_id
            FROM content.genre g
            LEFT JOIN content.genre_film_work gfw ON g.id = gfw.genre_id
            {}
            ORDER BY g.modified
        """.format(
            filter_query,
        )

        return query

    @staticmethod
    def get_genres_query(filter_query: str = "") -> str:
        query = """
            SELECT DISTINCT
            g.id,
            g.name,
            g.description,
            g.modified
            FROM content.genre g
            JOIN content.genre_film_work gfw ON g.id = gfw.genre_id
            {}
            ORDER BY g.modified
        """.format(
            filter_query,
        )

        return query

    def get_filmworks(self, last_modified: datetime, fetch_limit: int = 50) -> list:
        """Получить обновленные по modified фильмы со всеми связанными данными за один запрос."""
        if last_modified:
            self.cursor.execute(
                self.get_filmworks_query(filter_query="WHERE fw.modified > %s"),
                [last_modified],
            )
        else:
            self.cursor.execute(self.get_filmworks_query())

        while rows := self.cursor.fetchmany(size=fetch_limit):
            yield rows

    def get_persons(self, last_modified: datetime, fetch_limit: int = 50) -> list:
        """Получить обновленные по modified персоны."""
        if last_modified:
            self.cursor.execute(
                self.get_persons_query(filter_query="WHERE p.modified > %s"),
                [last_modified],
            )
        else:
            self.cursor.execute(self.get_persons_query())

        while rows := self.cursor.fetchmany(size=fetch_limit):
            yield rows

    def get_genres(self, last_modified: datetime, fetch_limit: int = 50) -> list:
        """Получить обновленные по modified жанры."""
        if last_modified:
            self.cursor.execute(
                self.get_genres_query(filter_query="WHERE g.modified > %s"),
                [last_modified],
            )
        else:
            self.cursor.execute(self.get_genres_query())

        while rows := self.cursor.fetchmany(size=fetch_limit):
            yield rows

    def get_filmworks_by_ids(self, ids: list[str], fetch_limit: int = 50) -> list:
        """Получить обновленные фильмы по списку id со всеми связанными данными за один запрос."""
        self.related_cursor.execute(
            self.get_filmworks_query(filter_query="WHERE fw.id IN %s"),
            [tuple(ids)],
        )

        while rows := self.related_cursor.fetchmany(size=fetch_limit):
            yield rows

    def get_changed_filmworks_by_persons(
        self,
        last_modified: datetime,
        fetch_limit: int,
    ) -> dict:
        """Получить обновленных людей."""
        if last_modified:
            self.cursor.execute(
                self.get_persons_filmworks_query(filter_query="WHERE p.modified > %s"),
                [last_modified],
            )
        else:
            self.cursor.execute(self.get_persons_filmworks_query())

        while rows := self.cursor.fetchmany(size=fetch_limit):
            yield rows

    def get_changed_filmworks_by_genres(
        self,
        last_modified: datetime,
        fetch_limit: int,
    ) -> dict:
        """Получить обновленные жанры."""
        if last_modified:
            self.cursor.execute(
                self.get_genres_filmworks_query(filter_query="WHERE g.modified > %s"),
                [last_modified],
            )
        else:
            self.cursor.execute(self.get_genres_filmworks_query())

        while rows := self.cursor.fetchmany(size=fetch_limit):
            yield rows
