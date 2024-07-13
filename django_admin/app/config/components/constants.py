import os

DEBUG_ENV = "./.env.development"

AUTH_USER_MODEL = "custom_auth.User"

AUTH_API_LOGIN_URL = os.getenv('AUTH_API_LOGIN_URL')

AUTHENTICATION_BACKENDS = [
    'custom_auth.auth.CustomBackend',
]
