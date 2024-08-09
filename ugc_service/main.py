from flask import Flask
from api.tracking import api
from core.swagger_config import configure_swagger
from flask_jwt_extended import JWTManager

from core.config import init_config

app = Flask(__name__)

# def init_redis():
#     redis_conn = Redis(host=settings.redis_host, port=settings.redis_port)
#     g.redis_conn = redis_conn
#
# @app.before_first_request
# def initialize_resources():
#     init_redis()
#
# @app.teardown_request
# def close_resources(exception=None):
#     redis_conn = g.pop('redis_conn', None)
#     if redis_conn is not None:
#         redis_conn.close()

# Инициализируем конфигурацию приложения
init_config(app)

# Инициализируем JWT
jwt = JWTManager(app)

# Инициализируем Swagger
configure_swagger(app)

# Регистрируем API
app.register_blueprint(api, url_prefix='/tracking')
