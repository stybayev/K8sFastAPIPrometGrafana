from flask import Blueprint, request, jsonify
from core.config import settings

api = Blueprint('api', __name__)


@api.route('/hello-world', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello, World!"})


@api.route('/config', methods=['GET'])
def get_config():
    return jsonify({
        "service_name": settings.service_name,
        "service_uvicorn_host": settings.service_uvicorn_host,
        "service_uvicorn_port": settings.service_uvicorn_port
    })
