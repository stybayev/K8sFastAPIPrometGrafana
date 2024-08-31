from enum import Enum

class ShardedCollections(Enum):
    LIKES_COLLECTION = ("likesCollection", {"movie_id": "hashed"})
    ANOTHER_COLLECTION = ("anotherCollection", {"anotherField": "hashed"})
    YET_ANOTHER_COLLECTION = ("yetAnotherCollection", {"yetAnotherField": 1})

    def __init__(self, collection_name, shard_key):
        self.collection_name = collection_name
        self.shard_key = shard_key
