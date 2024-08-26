import os
import random
import time
from uuid import uuid4

from locust import HttpUser, between, SequentialTaskSet, task, events
from pymongo import MongoClient

MONGO_URI = (f"mongodb://{os.getenv('MONGO_INITDB_ROOT_USERNAME')}:"
             f"{os.getenv('MONGO_INITDB_ROOT_PASSWORD')}@mongodb:{os.getenv('MONGO_PORT')}")


class MongoTest(SequentialTaskSet):
    client = MongoClient(MONGO_URI)
    database = client[os.getenv('MONGO_INITDB_DATABASE')]
    collection_like = database['likes']
    collection_users = database['users']
    collection_films = database['films']

    @task
    def write(self):
        data_insert = {
            'user_id': str(uuid4()),
            'movie_id': str(uuid4()),
            'like': random.choice([0, 10])
        }
        start_time = time.time()
        self.collection_like.insert_one(data_insert)
        duration = time.time() - start_time
        events.request.fire(
            request_type='Mongo Insert',
            name='Mongo Insert Data',
            response_time=duration * 1000,
            response_length=0
        )

    @task
    def read(self):
        user_document = self.collection_users.find_one()
        start_time = time.time()
        res = self.collection_like.find({'user_id': user_document['user_id']})
        duration = time.time() - start_time
        events.request.fire(
            request_type='Mongo Select',
            name='Mongo Select Data',
            response_time=duration * 1000,
            response_length=0
        )

    @task
    def aggregate(self):
        movie_document = self.collection_films.find_one()
        pipeline = [
            {"$match": {"movie_id": movie_document['movie_id'], 'likes': 10}},
            {"$group": {"_id": "$movie_id", "count": {"$sum": 1}}}
        ]
        start_time = time.time()
        agg_cursor = self.collection_like.aggregate(pipeline)
        duration = time.time() - start_time
        events.request.fire(
            request_type='Mongo Aggregate',
            name='Mongo aggregate data',
            response_time=duration * 1000,
            response_length=0
        )


class MongoUser(HttpUser):
    wait_time = between(1, 2)
    host = f'http://{os.getenv("MONGO_HOST")}:{os.getenv("MONGO_PORT")}'
    tasks = {MongoTest: 1}
