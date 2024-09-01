import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from datetime import datetime
from rating_review_service.services.review import ReviewService


@pytest.mark.anyio
async def test_add_review_success(rating_review_async_client: AsyncClient, review_service: ReviewService):
    review_data = {
        "movie_id": "test_movie_id",
        "user_id": "test_user_id",
        "text": "This is a test review.",
        "publication_date": "2024-09-01T00:00:00Z",
        "author": "Test Author"
    }

    with patch.object(ReviewService, 'add_review', new_callable=AsyncMock) as mock_add_review:
        mock_add_review.return_value = "test_review_id"

        response = await rating_review_async_client.post("/review/", json=review_data)

        assert response.status_code == 201

        data = response.json()

        assert data['id'] == "test_review_id"
        assert data['movie_id'] == review_data['movie_id']
        assert data['user_id'] == review_data['user_id']
        assert data['text'] == review_data['text']

        expected_date = datetime.fromisoformat(review_data['publication_date'].replace("Z", "+00:00"))
        actual_date = datetime.fromisoformat(data['publication_date'])

        assert expected_date == actual_date
        assert data['author'] == review_data['author']


@pytest.mark.anyio
async def test_get_non_existent_review_returns_404(rating_review_async_client: AsyncClient):
    review_id = "non_existent_review_id"
    with patch.object(ReviewService, 'get_reviews', new_callable=AsyncMock) as mock_get_reviews:
        mock_get_reviews.return_value = None

        response = await rating_review_async_client.get(f"/review/{review_id}")

        assert response.status_code == 404

        data = response.json()
        assert data['detail'] == "Not Found"


@pytest.mark.anyio
async def test_like_review_success(rating_review_async_client: AsyncClient):
    review_id = "test_review_id"
    user_id = "test_user_id"
    like = True

    with patch.object(ReviewService, 'add_or_update_review_like',
                      new_callable=AsyncMock) as mock_add_or_update_review_like:
        mock_add_or_update_review_like.return_value = True

        response = await rating_review_async_client.post(f"/review/{review_id}/like",
                                                         params={"user_id": user_id, "like": like})

        assert response.status_code == 200

        data = response.json()
        assert data['review_id'] == review_id
        assert data['user_id'] == user_id
        assert data['like'] == like
        assert data['message'] == "Лайк/дизлайк добавлен"


@pytest.mark.anyio
async def test_like_review_internal_server_error(rating_review_async_client: AsyncClient):
    review_id = "test_review_id"
    user_id = "test_user_id"
    like = True

    with patch.object(ReviewService, 'add_or_update_review_like',
                      new_callable=AsyncMock) as mock_add_or_update_review_like:
        mock_add_or_update_review_like.return_value = False

        response = await rating_review_async_client.post(f"/review/{review_id}/like",
                                                         params={"user_id": user_id, "like": like})

        assert response.status_code == 500

        data = response.json()
        assert data['detail'] == "Не удалось добавить лайк/дизлайк"


@pytest.mark.anyio
async def test_get_reviews_success(rating_review_async_client: AsyncClient):
    reviews_data = [
        {
            "id": "test_review_id_1",
            "movie_id": "test_movie_id_1",
            "user_id": "test_user_id_1",
            "text": "This is a test review 1.",
            "publication_date": "2024-09-01T00:00:00Z",
            "author": "Test Author 1",
            "likes": 10,
            "dislikes": 2,
            "user_rating": 5
        },
        {
            "id": "test_review_id_2",
            "movie_id": "test_movie_id_2",
            "user_id": "test_user_id_2",
            "text": "This is a test review 2.",
            "publication_date": "2024-09-02T00:00:00Z",
            "author": "Test Author 2",
            "likes": 5,
            "dislikes": 0,
            "user_rating": 4
        }
    ]

    with patch.object(ReviewService, 'get_reviews', new_callable=AsyncMock) as mock_get_reviews:
        mock_get_reviews.return_value = reviews_data

        response = await rating_review_async_client.get("/reviews/", params={"sort_by": "likes", "order": "asc"})

        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2
        assert data[0]['id'] == reviews_data[0]['id']
        assert data[0]['movie_id'] == reviews_data[0]['movie_id']
        assert data[0]['user_id'] == reviews_data[0]['user_id']
        assert data[0]['text'] == reviews_data[0]['text']
        assert data[0]['likes'] == reviews_data[0]['likes']
        assert data[0]['dislikes'] == reviews_data[0]['dislikes']
        assert data[0]['user_rating'] == reviews_data[0]['user_rating']
        assert data[0]['author'] == reviews_data[0]['author']

        assert data[1]['id'] == reviews_data[1]['id']
        assert data[1]['movie_id'] == reviews_data[1]['movie_id']
        assert data[1]['user_id'] == reviews_data[1]['user_id']
        assert data[1]['text'] == reviews_data[1]['text']
        assert data[1]['likes'] == reviews_data[1]['likes']
        assert data[1]['dislikes'] == reviews_data[1]['dislikes']
        assert data[1]['user_rating'] == reviews_data[1]['user_rating']
        assert data[1]['author'] == reviews_data[1]['author']


@pytest.mark.anyio
async def test_get_reviews_not_found(rating_review_async_client: AsyncClient):
    with patch.object(ReviewService, 'get_reviews', new_callable=AsyncMock) as mock_get_reviews:
        mock_get_reviews.return_value = []

        response = await rating_review_async_client.get("/reviewss/", params={"sort_by": "likes", "order": "asc"})

        assert response.status_code == 404

        data = response.json()
        assert data['detail'] == "Not Found"
