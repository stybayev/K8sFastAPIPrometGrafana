import http
import json
import logging

import requests

from django.contrib.auth.backends import BaseBackend

import jwt
from custom_auth.models import User

from django.conf import settings

from custom_auth.enums import Roles


class CustomBackend(BaseBackend):

    def decoded_token(self, access_token):
        try:
            decoded_token = jwt.decode(access_token, options={"verify_signature": False})
            return decoded_token
        except Exception as e:
            logging.info(e)
            return None

    def authenticate(self, request, username=None, password=None):
        payload = {'login': username, 'password': password}
        url = settings.AUTH_API_LOGIN_URL
        response = requests.post(url, data=json.dumps(payload))

        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()
        access_token = data.get('access_token')

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

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
