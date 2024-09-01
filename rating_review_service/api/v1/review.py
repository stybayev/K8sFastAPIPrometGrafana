from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query

from rating_review_service.schema.review import Review, ReviewResponse, LikeDislikeResponse
from rating_review_service.services.review import ReviewService, get_review_service

router = APIRouter()


@router.post("/review/", status_code=status.HTTP_201_CREATED, response_model=ReviewResponse)
async def add_review(review: Review, service: ReviewService = Depends(get_review_service)):
    """
    Добавление новой рецензии к фильму.
    """
    review_id = await service.add_review(review)
    return ReviewResponse(
        id=review_id,
        movie_id=review.movie_id,
        user_id=review.user_id,
        text=review.text,
        publication_date=review.publication_date,
        author=review.author
    )


@router.post("/review/{review_id}/like", status_code=status.HTTP_200_OK, response_model=LikeDislikeResponse)
async def like_review(review_id: str, user_id: str, like: bool, service: ReviewService = Depends(get_review_service)):
    """
    Добавление лайка или дизлайка к рецензии.
    """
    result = await service.add_or_update_review_like(review_id, user_id, like)
    if result:
        return LikeDislikeResponse(
            review_id=review_id,
            user_id=user_id,
            like=like,
            message="Лайк/дизлайк добавлен"
        )
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Не удалось добавить лайк/дизлайк")


@router.get("/reviews/", response_model=List[ReviewResponse])
async def get_reviews(
        movie_id: str | None = None,
        sort_by: str | None = Query(
            None,
            description="Поле для сортировки: 'likes', 'dislikes', 'rating', 'publication_date'"),
        order: str | None = Query("desc", description="Порядок сортировки: 'asc' или 'desc'"),
        service: ReviewService = Depends(get_review_service)
):
    """
    Получение списка рецензий с возможностью гибкой сортировки.
    """
    reviews = await service.get_reviews(movie_id, sort_by, order)
    return reviews
