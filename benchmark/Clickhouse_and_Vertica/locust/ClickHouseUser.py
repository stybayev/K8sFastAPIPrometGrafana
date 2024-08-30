import io
import os
import random
import uuid

import pandas as pd
from locust import HttpUser, task, between, SequentialTaskSet


class FewDataClickhouseTest(SequentialTaskSet):
    headers = {
        "X-ClickHouse-User": os.getenv("CLICKHOUSE_USER"),
        "X-ClickHouse-Key": os.getenv("CLICKHOUSE_PWD")
    }

    def on_start(self):
        query = f'''
            CREATE TABLE IF NOT EXISTS
            default.{os.getenv("NAME_FEW_TABLE_CH")} (
                user_id Int32 NOT NULL, 
                movie_id String NOT NULL, 
                viewed_frame Int32 NOT NULL
            )
            ENGINE = MergeTree()
            ORDER BY user_id
        '''

        self.client.post(
            "/?query=" + query,
            name='CREATE TABLE',
            headers=self.headers
        )

    @task
    def insert_data(self):
        query = f'''
            INSERT INTO default.{os.getenv("NAME_FEW_TABLE_CH")} (user_id, movie_id, viewed_frame) 
            VALUES (
                {random.randint(1, 10000)}, 
                '{uuid.uuid4()}', 
                {random.randint(1, 10000)}
            )
        '''
        self.client.post(
            "/?query=" + query,
            name='INSERT FEW',
            headers=self.headers
        )

    @task
    def select_data(self):
        query = f'''
            SELECT user_id, movie_id, viewed_frame
            FROM default.{os.getenv('NAME_FEW_TABLE_CH')}
            LIMIT 1
        '''

        self.client.get(
            "/?query=" + query,
            name='SELECT FEW',
            headers=self.headers
        )

    @task
    def aggregate_data(self):
        query = f'''
            SELECT AVG(viewed_frame)
            FROM default.{os.getenv('NAME_FEW_TABLE_CH')}
        '''
        self.client.get(
            "/?query=" + query,
            name="AGGREGATE FEW",
            headers=self.headers
        )


class BigDataClickhouseTest(SequentialTaskSet):
    headers = {
        "X-ClickHouse-User": os.getenv("CLICKHOUSE_USER"),
        "X-ClickHouse-Key": os.getenv("CLICKHOUSE_PWD")
    }
    data = pd.read_csv(
        os.getenv("PATH_FILE_DATA"),
        header=None,
        chunksize=int(os.getenv('CHUNK_SIZE'))
    )
    data_insert = iter(data)

    def on_start(self):
        query = f'''
            CREATE TABLE IF NOT EXISTS
            default.{os.getenv("NAME_BD_TABLE_CH")} (
                user_id Int32 NOT NULL, 
                movie_id String NOT NULL, 
                viewed_frame Int32 NOT NULL
            )
            ENGINE = MergeTree()
            ORDER BY user_id
        '''

        self.client.post(
            "/?query=" + query,
            name='CREATE TABLE',
            headers=self.headers
        )
        self.data_insert = iter(self.data)

    @task
    def insert_big_data(self):
        try:
            df = next(self.data_insert)
        except StopIteration:
            return
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, header=False)
        csv_data = csv_buffer.getvalue()
        self.client.post(
            f"/?query=INSERT INTO default.{os.getenv('NAME_BD_TABLE_CH')} (user_id, movie_id, viewed_frame) FORMAT CSV",
            data=csv_data,
            headers={
                "X-ClickHouse-User": os.getenv("CLICKHOUSE_USER"),
                "X-ClickHouse-Key": os.getenv("CLICKHOUSE_PWD"),
                "Content-Type": "text/plain"
            },
            name="INSERT BIG DATA"
        )

    @task
    def select_big_data(self):
        query = f'''
            SELECT user_id, movie_id, viewed_frame
            FROM default.{os.getenv("NAME_BD_TABLE_CH")}
            LIMIT 1
        '''

        self.client.get(
            "/?query=" + query,
            name='SELECT BIG DATA',
            headers=self.headers
        )

    @task
    def aggregate_data(self):
        query = f'''
            SELECT AVG(viewed_frame)
            FROM default.{os.getenv("NAME_BD_TABLE_CH")}
        '''
        self.client.get(
            "/?query=" + query,
            name="AGGREGATE BIG DATA",
            headers=self.headers
        )


class ClickHouseUser(HttpUser):
    wait_time = between(1, 2)
    host = f'http://{os.getenv("CLICKHOUSE_HOST")}:{os.getenv("CLICKHOUSE_PORT")}'
    tasks = {BigDataClickhouseTest: 1, FewDataClickhouseTest: 1}
