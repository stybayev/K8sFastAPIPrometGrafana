from functools import lru_cache

from bson import ObjectId
from rating_review_service.db.mongo import get_db
from rating_review_service.schema.review import Review
from rating_review_service.utils.enums import ShardedCollections
from fastapi import Depends, HTTPException, status



class ReviewService:
    def __init__(self, db):
        self.collection = db[ShardedCollections.REVIEW_COLLECTION.collection_name]

    def to_object_id(self, id_str: str):
        return ObjectId(id_str) if ObjectId.is_valid(id_str) else id_str

    async def add_review(self, review: Review):
        # Проверяем, является ли значение `movie_id` и `user_id` корректными ObjectId
        review_dict = review.dict()
        review_dict["movie_id"] = self.to_object_id(review.movie_id)
        review_dict["user_id"] = self.to_object_id(review.user_id)

        try:
            result = await self.collection.insert_one(review_dict)
            return str(result.inserted_id)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=str(e))


@lru_cache()
def get_review_service(db=Depends(get_db)) -> ReviewService:
    return ReviewService(db)
