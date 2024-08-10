from flask import Flask, request
from api.tracking import api
from core.swagger_config import configure_swagger
from flask_jwt_extended import JWTManager
from core.config import init_config
from core.middleware import check_blacklist

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
