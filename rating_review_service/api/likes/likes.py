from fastapi import APIRouter, HTTPException, status, Depends
from rating_review_service.schema.likes import Like
from rating_review_service.services.likes import get_like_service, LikeService

router = APIRouter()


@router.post("/like/", status_code=status.HTTP_201_CREATED, response_model=Like)
async def like_movie(like: Like,
                     service: LikeService = Depends(get_like_service)):
    """
    Добавление или изменение лайков.
    """
    result = await service.add_or_update_like(like)
    if result:
        return like
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Не удалось добавить или обновить лайк")


@router.delete("/like/{user_id}/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_movie(user_id: str,
                       movie_id: str,
                       service: LikeService = Depends(get_like_service)):
    """
    Удаление лайков
    """
    result = await service.remove_like(user_id, movie_id)
    if result.deleted_count:
        return {"message": "Лайк удален успешно"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Лайк не найден")


@router.get("/likes/{movie_id}")
async def get_likes(movie_id: str, service: LikeService = Depends(get_like_service)):
    """
    Просмотр количества лайков и дизлайков у фильма;
    """
    result = await service.get_movie_likes(movie_id)
    return result


@router.get("/rating/{movie_id}")
async def get_average_rating(movie_id: str, service: LikeService = Depends(get_like_service)):
    result = await service.get_movie_average_rating(movie_id)
    return {"average_rating": result}
