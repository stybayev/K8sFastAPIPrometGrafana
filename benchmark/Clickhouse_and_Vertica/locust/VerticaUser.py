import os
import random
import time
import uuid

import pandas as pd
import vertica_python
from locust import HttpUser, task, between, SequentialTaskSet, events

vertica_config = {
    'host': os.getenv('VERTICA_HOST'),
    'port': os.getenv("VERTICA_PORT"),
    'user': os.getenv('VERTICA_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('VERTICA_DB'),
    'autocommit': True,
    'tlsmode': 'disable',
    'connection_timeout': 5
}


class FewDataVerticaTest(SequentialTaskSet):
    def connect_db(self):
        self.connection = vertica_python.connect(**vertica_config)
        self.cursor = self.connection.cursor()

    def on_start(self):
        self.connect_db()
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {os.getenv("NAME_FEW_TABLE_VERTICA")} (
                user_id INTEGER NOT NULL,
                movie_id VARCHAR(256) NOT NULL,
                viewed_frame INTEGER NOT NULL
            );
        ''')

    @task
    def insert_data(self):
        start_time = time.time()
        try:
            self.cursor.execute(f'''
                INSERT INTO {os.getenv("NAME_FEW_TABLE_VERTICA")} (user_id, movie_id, viewed_frame)
                VALUES ({random.randint(1, 10000)}, '{uuid.uuid4()}', {random.randint(1, 10000)})
            ''')

            duration = time.time() - start_time
            events.request.fire(
                request_type='DB Insert',
                name="INSERT FEW DATA",
                response_time=duration * 1000,
                response_length=0
            )
        except vertica_python.errors.InterfaceError as e:
            events.request.fire(
                request_type="DB Insert",
                name="INSERT FEW DATA",
                response_time=0,
                response_length=0,
                exception=e
            )
            self.connect_db()

    @task
    def select_data(self):
        start_time = time.time()
        try:
            self.cursor.execute(f'''
                SELECT user_id, movie_id, viewed_frame
                FROM {os.getenv("NAME_FEW_TABLE_VERTICA")}
                LIMIT 1
            ''')
            duration = time.time() - start_time
            events.request.fire(
                request_type='DB Select',
                name='SELECT FEW DATA',
                response_time=duration * 1000,
                response_length=0
            )
        except vertica_python.errors.InterfaceError as e:
            events.request.fire(
                request_type="DB Select",
                name="SELECT FEW DATA",
                response_time=0,
                response_length=0,
                exception=e
            )
            self.connect_db()

    @task
    def aggregate_data(self):
        start_time = time.time()
        try:
            self.cursor.execute(f'''
                SELECT AVG(viewed_frame)
                FROM {os.getenv("NAME_FEW_TABLE_VERTICA")}
                LIMIT 1
            ''')
            duration = time.time() - start_time
            events.request.fire(
                request_type='DB Aggregate',
                name='AGGREGATE FEW DATA',
                response_time=duration * 1000,
                response_length=0
            )
        except vertica_python.errors.InterfaceError as e:
            events.request.fire(
                request_type="DB Aggregate",
                name="AGGREGATE FEW DATA",
                response_time=0,
                response_length=0,
                exception=e
            )
            self.connect_db()


class BigDataVerticaTest(SequentialTaskSet):
    data_insert = iter(
        pd.read_csv(
            os.getenv("PATH_FILE_DATA"),
            header=None,
            chunksize=int(os.getenv('CHUNK_SIZE'))
        )
    )

    def connect_db(self):
        self.connection = vertica_python.connect(**vertica_config)
        self.cursor = self.connection.cursor()

    def on_start(self):
        self.connect_db()
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {os.getenv("NAME_BD_TABLE_VERTICA")} (
                user_id INTEGER NOT NULL,
                movie_id VARCHAR(256) NOT NULL,
                viewed_frame INTEGER NOT NULL
            );
        ''')

    @task
    def insert_big_data(self):
        try:
            df = next(self.data_insert)
        except StopIteration:
            return
        values = [tuple(row) for row in df.values]
        placeholders = ', '.join(['%s'] * len(df.columns))
        start_time = time.time()
        try:
            self.cursor.executemany(f'''
                INSERT INTO {os.getenv("NAME_BD_TABLE_VERTICA")} (user_id, movie_id, viewed_frame) 
                VALUES ({placeholders})
            ''', values)
            duration = time.time() - start_time
            events.request.fire(
                request_type='DB Big Insert',
                name='INSERT BIG DATA',
                response_time=duration * 1000,
                response_length=0
            )
        except vertica_python.errors.InterfaceError as e:
            events.request.fire(
                request_type="DB Big Insert",
                name="INSERT BIG DATA",
                response_time=0,
                response_length=0,
                exception=e
            )
            self.connect_db()

    @task
    def select_big_data(self):
        start_time = time.time()
        try:
            self.cursor.execute(f'''
                SELECT user_id, movie_id, viewed_frame
                FROM {os.getenv("NAME_BD_TABLE_VERTICA")}
                LIMIT 1
            ''')
            duration = time.time() - start_time
            events.request.fire(
                request_type='DB Big Select',
                name='SELECT BIG DATA',
                response_time=duration * 1000,
                response_length=0
            )
        except vertica_python.errors.InterfaceError as e:
            events.request.fire(
                request_type="DB Big Select",
                name="SELECT BIG DATA",
                response_time=0,
                response_length=0,
                exception=e
            )
            self.connect_db()

    @task
    def aggregate_big_data(self):
        start_time = time.time()
        try:
            self.cursor.execute(f'''
                SELECT AVG(viewed_frame)
                FROM {os.getenv("NAME_BD_TABLE_VERTICA")}
            ''')
            duration = time.time() - start_time
            events.request.fire(
                request_type='DB Big Aggregate',
                name='AGGREGATE BIG DATA',
                response_time=duration * 1000,
                response_length=0
            )
        except vertica_python.errors.InterfaceError as e:
            events.request.fire(
                request_type="DB Big Aggregate",
                name="AGGREGATE BIG DATA",
                response_time=0,
                response_length=0,
                exception=e
            )
            self.connect_db()


class VerticaUser(HttpUser):
    wait_time = between(1, 2)
    host = f'http://{os.getenv("VERTICA_HOST")}:{os.getenv("VERTICA_PORT")}'
    tasks = {FewDataVerticaTest: 1, BigDataVerticaTest: 1}
