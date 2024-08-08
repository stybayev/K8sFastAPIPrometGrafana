from flask import Flask
from api.tracking import api
from core.swagger_config import configure_swagger

app = Flask(__name__)

configure_swagger(app)
app.register_blueprint(api, url_prefix='/tracking')
