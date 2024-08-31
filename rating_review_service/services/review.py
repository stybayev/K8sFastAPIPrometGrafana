from functools import lru_cache

from bson import ObjectId
from rating_review_service.db.mongo import get_db
from rating_review_service.schema.review import Review, ReviewLike
from rating_review_service.utils.enums import ShardedCollections
from fastapi import Depends, HTTPException, status


class ReviewService:
    def __init__(self, db):
        self.review_collection = db[ShardedCollections.REVIEW_COLLECTION.collection_name]
        self.review_likes_collection = db[ShardedCollections.REVIEW_LIKES_COLLECTION.collection_name]

    def to_object_id(self, id_str: str):
        return ObjectId(id_str) if ObjectId.is_valid(id_str) else id_str

    async def add_review(self, review: Review):
        review_dict = review.dict()
        review_dict["movie_id"] = self.to_object_id(review.movie_id)
        review_dict["user_id"] = self.to_object_id(review.user_id)
        try:
            result = await self.review_collection.insert_one(review_dict)
            return str(result.inserted_id)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=str(e))

    async def add_or_update_review_like(self, review_id: str, user_id: str, like: bool):
        review_id = self.to_object_id(review_id)
        user_id = self.to_object_id(user_id)

        result = await self.review_likes_collection.update_one(
            {"review_id": review_id, "user_id": user_id},
            {"$set": {"like": like}},
            upsert=True
        )

        return result.upserted_id or result.modified_count > 0

    async def get_review_likes_dislikes(self, review_id: str):
        review_id = self.to_object_id(review_id)
        likes_count = await self.review_likes_collection.count_documents({"review_id": review_id, "like": True})
        dislikes_count = await self.review_likes_collection.count_documents({"review_id": review_id, "like": False})
        return {"likes": likes_count, "dislikes": dislikes_count}


@lru_cache()
def get_review_service(db=Depends(get_db)) -> ReviewService:
    return ReviewService(db)
