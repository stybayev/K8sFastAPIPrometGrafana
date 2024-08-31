import os
import sentry_sdk

from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from split_settings.tools import include
from django_admin.app.config.sentry_hook import before_send
from .components import constants

sentry_sdk.init(
    dsn=os.getenv("DJANGO_SENTRY_DSN"),
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    send_default_pii=True,  # Включает передачу данных о пользователе
    before_send=before_send,
)

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get("DEBUG", "False") == "True"

if DEBUG:
    load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")

ALLOWED_HOSTS = (
    os.environ.get("ALLOWED_HOSTS").split(",")
    if os.environ.get("ALLOWED_HOSTS")
    else ["127.0.0.1"]
)

INTERNAL_IPS = (
    os.environ.get("INTERNAL_HOSTS").split(",")
    if os.environ.get("INTERNAL_HOSTS")
    else ["127.0.0.1"]
)

AWS_ACCESS_KEY_ID = os.environ.get("MINIO_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.environ.get("MINIO_SECRET_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("BACKET_NAME")
AWS_S3_ENDPOINT_URL = os.environ.get("MINIO_HOST")

FILE_SERVICE_URL = os.environ.get("FILE_SERVICE_URL")

include("components/apps.py")
include("components/constants.py")
include("components/database.py")
include("components/templates.py")
include("components/validators.py")
include("components/middlewares.py")
include("components/internationalization.py")
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
if DEBUG:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "staticfiles")]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
