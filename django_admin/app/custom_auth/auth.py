import json
import logging

import requests
import jwt
from django.contrib.auth.backends import BaseBackend
from django.core.cache import cache
from custom_auth.models import User
from django.conf import settings
from custom_auth.enums import Roles
import uuid


class CustomBackend(BaseBackend):
    def decoded_token(self, access_token):
        """
        Метод для декодирония получаемого токена
        """
        try:
            decoded_token = jwt.decode(access_token, options={"verify_signature": False})
            return decoded_token
        except Exception as e:
            logging.info(e)
            return None

    def cache_tokens(self, username, tokens):
        """
        Метод для сохранения токена в кэш
        """
        cache.set(f'tokens_{username}', tokens, timeout=3600)

    def get_cached_tokens(self, username):
        """
        Метод для получения токена из кэша
        """
        return cache.get(f'tokens_{username}')

    def authenticate(self, request, username=None, password=None):
        payload = {'login': username, 'password': password}
        url = settings.AUTH_API_LOGIN_URL

        try:
            headers = {'X-Request-Id': str(uuid.uuid4())}
            response = requests.post(url, data=json.dumps(payload), headers=headers)
        except requests.exceptions.RequestException as e:
            logging.error(f"Auth service is not available: {e}")
            tokens = self.get_cached_tokens(username)
            if tokens:
                return self.authenticate_with_cached_tokens(username, tokens)
            return self.get_user_by_username(username)

        data = response.json()
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')

        self.cache_tokens(username, {'access_token': access_token, 'refresh_token': refresh_token})

        # Декодирование access токена
        decoded_token = self.decoded_token(access_token=access_token)
        user_id = decoded_token.get('id')
        first_name = decoded_token.get('first_name')
        last_name = decoded_token.get('last_name')
        roles = decoded_token.get('roles')

        try:
            user, created = User.objects.get_or_create(id=user_id, )
            user.login = username
            user.first_name = first_name
            user.last_name = last_name
            user.is_admin = Roles.ADMIN in roles
            user.is_active = True
            user.save()
        except Exception as e:
            logging.info(e)
            return None

        return user

    def authenticate_with_cached_tokens(self, username, tokens):
        decoded_token = self.decoded_token(access_token=tokens['access_token'])
        user_id = decoded_token.get('id')
        first_name = decoded_token.get('first_name')
        last_name = decoded_token.get('last_name')
        roles = decoded_token.get('roles')

        try:
            user = User.objects.get(id=user_id)
            user.login = username
            user.first_name = first_name
            user.last_name = last_name
            user.is_admin = Roles.ADMIN in roles
            user.is_active = True
            user.save()
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get_user_by_username(self, username):
        """
        Метод для поиска пользователя в базе данных, если токенов нет в кэше
        """
        try:
            return User.objects.get(login=username)
        except User.DoesNotExist:
            return None
