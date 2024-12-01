import os

import sentry_sdk
from flask import Flask, request
from api.tracking import api
from core.swagger_config import configure_swagger
from flask_jwt_extended import JWTManager
from core.config import init_config
from core.middleware import check_blacklist
from utils.sentry_hook import before_send
from prometheus_fastapi_instrumentator import Instrumentator

sentry_sdk.init(
    dsn=os.getenv("UGS_SERVICE_SENTRY_DSN"),
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    send_default_pii=True,  # Включает передачу данных о пользователе
    before_send=before_send,
)

app = Flask(__name__)

# Инициализируем конфигурацию приложения
init_config(app)

# Инициализируем JWT
jwt = JWTManager(app)

# Инициализируем Swagger
configure_swagger(app)

# Подключаем middleware для проверки blacklist токенов
app.before_request(check_blacklist)

# Регистрируем API
app.register_blueprint(api, url_prefix='/tracking')

Instrumentator().instrument(app).expose(app)
