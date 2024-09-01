from functools import lru_cache
from rating_review_service.db.mongo import get_db
from rating_review_service.utils.enums import ShardedCollections
from rating_review_service.schema.likes import Like
from bson import ObjectId
from fastapi import Depends


class LikeService:
    def __init__(self, db):
        self.collection = db[ShardedCollections.LIKES_COLLECTION.collection_name]

    def to_object_id(self, id_str: str):
        return ObjectId(id_str) if ObjectId.is_valid(id_str) else id_str

    async def add_or_update_like(self, like: Like):
        user_id = self.to_object_id(like.user_id)
        movie_id = self.to_object_id(like.movie_id)

        result = await self.collection.update_one(
            {"user_id": user_id, "movie_id": movie_id},
            {"$set": {"rating": like.rating}},
            upsert=True
        )
        return result

    async def remove_like(self, user_id: str, movie_id: str):
        user_id = self.to_object_id(user_id)
        movie_id = self.to_object_id(movie_id)

        result = await self.collection.delete_one({"user_id": user_id, "movie_id": movie_id})
        return result

    async def get_movie_likes(self, movie_id: str):
        movie_id = self.to_object_id(movie_id)

        likes_count = await self.collection.count_documents({"movie_id": movie_id, "rating": 10})
        dislikes_count = await self.collection.count_documents({"movie_id": movie_id, "rating": 0})
        return {"likes": likes_count, "dislikes": dislikes_count}

    async def get_movie_average_rating(self, movie_id: str):
        movie_id = self.to_object_id(movie_id)

        pipeline = [
            {"$match": {"movie_id": movie_id}},
            {"$group": {"_id": "$movie_id", "average_rating": {"$avg": "$rating"}}}
        ]
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        if result:
            return result[0]["average_rating"]
        return None


@lru_cache()
def get_like_service(db=Depends(get_db)) -> LikeService:
    return LikeService(db)
