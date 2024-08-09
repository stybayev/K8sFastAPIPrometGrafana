from flask import Flask
from api.tracking import api
from core.swagger_config import configure_swagger
from flask_jwt_extended import JWTManager

from core.config import init_config

app = Flask(__name__)

# Инициализируем конфигурацию приложения
init_config(app)

# Инициализируем JWT
jwt = JWTManager(app)

# Инициализируем Swagger
configure_swagger(app)

# Регистрируем API
app.register_blueprint(api, url_prefix='/tracking')
