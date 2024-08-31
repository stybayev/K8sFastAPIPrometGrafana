from fastapi import APIRouter, Depends, HTTPException, status

from rating_review_service.schema.review import Review, ReviewResponse, ReviewLike
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


@router.post("/review/like/", status_code=status.HTTP_201_CREATED)
async def add_review_like(review_like: ReviewLike, service: ReviewService = Depends(get_review_service)):
    """
    Добавление лайка или дизлайка к рецензии.
    """
    await service.add_review_like(review_like)
    return {"message": "Лайк/дизлайк добавлен"}


@router.get("/review/{review_id}/likes")
async def get_review_likes(review_id: str, service: ReviewService = Depends(get_review_service)):
    """
    Получение количества лайков и дизлайков для рецензии.
    """
    result = await service.get_review_likes_dislikes(review_id)
    return result
