import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class MyUserManager(BaseUserManager):
    def create_user(self, login, password=None):
        if not login:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(login))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None):
        user = self.create_user(login, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    login = models.EmailField(_('login'), max_length=255, unique=True)
    password = models.CharField(_('password'), max_length=255)
    first_name = models.CharField(_('first name'), max_length=50, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'login'

    objects = MyUserManager()

    def __str__(self):
        return self.login

    class Meta:
        db_table = 'auth"."users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


import http
import json
from enum import StrEnum, auto

import requests
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class Roles(StrEnum):
    ADMIN = auto()
    SUBSCRIBER = auto()


class CustomBackend(BaseBackend):
    def authenticate(self, request, login=None, password=None):
        print(123)
        AUTH_API_LOGIN_URL = 'http://0.0.0.0:8082/api/v1/auth/users/login'

        url = 'http://0.0.0.0:8082/api/v1/auth/users/login'
        payload = {'login': login, 'password': password}
        response = requests.post(url, data=json.dumps(payload))
        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()

        try:
            user, created = User.objects.get_or_create(id=data['id'], )
            user.login = data.get('login')
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            user.is_admin = data.get('role') == Roles.ADMIN
            user.is_active = data.get('is_active')
            user.save()
        except Exception:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None