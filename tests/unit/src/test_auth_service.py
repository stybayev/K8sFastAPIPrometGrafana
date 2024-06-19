# from unittest.mock import AsyncMock
#
# from auth.models.users import User
# from auth.schema.users import UserCreate, UserResponse
# from fastapi import status
# import pytest
#
#
# @pytest.mark.anyio
# async def test_register_user_success(async_client, user_service, override_dependencies):
#     """
#     Тест успешной регистрации пользователя
#     """
#     user_data = {
#         "login": "testuser",
#         "password": "testpassword",
#         "first_name": "Test",
#         "last_name": "User"
#     }
#     user_create = UserCreate(**user_data)
#     new_user = User(id=1, **user_data)
#
#     user_service.get_by_login = AsyncMock(return_value=None)
#     user_service.create_user = AsyncMock(return_value=new_user)
#
#     response = await async_client.post("/users", json=user_data)
#     response_data = response.json()
#
#     assert response.status_code == status.HTTP_201_CREATED
#     assert response_data['login'] == user_create.login
#     assert response_data['first_name'] == user_create.first_name
#     assert response_data['last_name'] == user_create.last_name