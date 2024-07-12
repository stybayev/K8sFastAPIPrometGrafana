DEBUG_ENV = "./.env.development"

AUTH_USER_MODEL = "custom_auth.models.User"

AUTHENTICATION_BACKENDS = [
    'custom_auth.models.CustomBackend',
]
