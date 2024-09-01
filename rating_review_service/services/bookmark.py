from functools import lru_cache
from bson import ObjectId
from fastapi import Depends, HTTPException, status
from rating_review_service.db.mongo import get_db
from rating_review_service.schema.bookmark import Bookmark
from rating_review_service.utils.enums import ShardedCollections


class BookmarkService:
    def __init__(self, db):
        self.collection = db[ShardedCollections.BOOKMARKS_COLLECTION.collection_name]

    def to_object_id(self, id_str: str):
        return ObjectId(id_str) if ObjectId.is_valid(id_str) else id_str

    async def add_bookmark(self, bookmark: Bookmark):
        bookmark_dict = bookmark.dict()
        bookmark_dict["user_id"] = self.to_object_id(bookmark.user_id)
        bookmark_dict["movie_id"] = self.to_object_id(bookmark.movie_id)
        try:
            result = await self.collection.insert_one(bookmark_dict)
            return str(result.inserted_id)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def remove_bookmark(self, user_id: str, movie_id: str):
        user_id = self.to_object_id(user_id)
        movie_id = self.to_object_id(movie_id)
        result = await self.collection.delete_one({"user_id": user_id, "movie_id": movie_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Закладка не найдена")
        return True

    async def get_bookmarks(self, user_id: str):
        user_id = self.to_object_id(user_id)
        bookmarks = await self.collection.find({"user_id": user_id}).to_list(length=None)
        return bookmarks


@lru_cache()
def get_bookmark_service(db=Depends(get_db)) -> BookmarkService:
    return BookmarkService(db)
