from fastapi import APIRouter, Depends, HTTPException, status

from rating_review_service.schema.review import Review, ReviewResponse
from rating_review_service.services.review import ReviewService, get_review_service

router = APIRouter()


@router.post("/review/", status_code=status.HTTP_201_CREATED, response_model=ReviewResponse)
async def add_review(review: Review, service: ReviewService = Depends(get_review_service)):
    """
    Добавление новой рецензии к фильму.
    """
    review_id = await service.add_review(review)
    if review_id:
        return ReviewResponse(
            id=review_id,
            movie_id=review.movie_id,
            user_id=review.user_id,
            text=review.text,
            publication_date=review.publication_date,
            author=review.author,
            rating=review.rating,
            likes=review.likes,
            dislikes=review.dislikes
        )
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Не удалось добавить рецензию")
