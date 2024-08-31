from fastapi import APIRouter, Depends, HTTPException, status
from rating_review_service.schema.bookmark import Bookmark, BookmarkResponse, BookmarksListResponse
from rating_review_service.services.bookmark import BookmarkService, get_bookmark_service

router = APIRouter()


@router.post("/bookmark/", status_code=status.HTTP_201_CREATED, response_model=BookmarkResponse)
async def add_bookmark(bookmark: Bookmark, service: BookmarkService = Depends(get_bookmark_service)):
    """
    Добавление фильма в закладки.
    """
    bookmark_id = await service.add_bookmark(bookmark)
    return BookmarkResponse(bookmark_id=bookmark_id)


@router.delete("/bookmark/{user_id}/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_bookmark(user_id: str, movie_id: str, service: BookmarkService = Depends(get_bookmark_service)):
    """
    Удаление фильма из закладок.
    """
    await service.remove_bookmark(user_id, movie_id)
    return


@router.get("/bookmarks/{user_id}", response_model=BookmarksListResponse)
async def get_bookmarks(user_id: str, service: BookmarkService = Depends(get_bookmark_service)):
    """
    Просмотр списка закладок.
    """
    bookmarks = await service.get_bookmarks(user_id)
    return BookmarksListResponse(bookmarks=bookmarks)
