from enum import Enum

class ShardedCollections(Enum):
    LIKES_COLLECTION = ("likesCollection", {"movie_id": "hashed"})
    REVIEW_COLLECTION = ("reviewCollection", {"movie_id": "hashed"})
    REVIEW_LIKES_COLLECTION = ("reviewLikesCollection", {"review_id": "hashed"})

    def __init__(self, collection_name, shard_key):
        self.collection_name = collection_name
        self.shard_key = shard_key
