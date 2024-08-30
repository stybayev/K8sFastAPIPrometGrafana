import os
import random
import time
from uuid import uuid4

import psycopg2
from locust import HttpUser, between, SequentialTaskSet, task, events


class PostgresTest(SequentialTaskSet):
    conn = psycopg2.connect(
        dbname='postgres',
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT')
    )
    cursor = conn.cursor()

    def on_stop(self):
        self.cursor.close()
        self.conn.close()

    @task
    def write(self):
        data_insert = (str(uuid4()), str(uuid4()), random.choice([0, 10]))
        start_time = time.time()
        self.cursor.execute('''
            INSERT INTO content.likes (user_id, movie_id, likes)
            VALUES (%s, %s, %s)
        ''', data_insert)
        self.conn.commit()
        duration = time.time() - start_time
        events.request.fire(
            request_type='Postgres Insert',
            name='Postgres Insert Data',
            response_time=duration * 1000,
            response_length=0
        )

    @task
    def read(self):
        self.cursor.execute('''
            SELECT user_id
            FROM content.users
            LIMIT 1
        ''')
        user_id = self.cursor.fetchone()[0]
        start_time = time.time()
        self.cursor.execute(f'''
            SELECT user_id, movie_id, likes
            FROM content.likes
            WHERE user_id = '{user_id}'
        ''')
        duration = time.time() - start_time
        events.request.fire(
            request_type='Postgres Select',
            name='Postgres Select Data',
            response_time=duration * 1000,
            response_length=0
        )

    @task
    def aggregate(self):
        self.cursor.execute('''
            SELECT movie_id
            FROM content.films
            LIMIT 1
        ''')
        movie_id = self.cursor.fetchone()[0]
        start_time = time.time()
        self.cursor.execute(f'''
            SELECT COUNT(*)
            FROM content.likes
            WHERE movie_id = '{movie_id}' AND likes = 10
        ''')
        duration = time.time() - start_time
        events.request.fire(
            request_type='Postgres Aggregate',
            name='Postgres Agg Data',
            response_time=duration * 1000,
            response_length=0
        )


class PostgresUser(HttpUser):
    wait_time = between(1, 2)
    host = f'http://{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}'
    tasks = {PostgresTest: 1}
