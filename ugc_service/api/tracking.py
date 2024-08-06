from flask import Blueprint, request, jsonify

# from ..core.config import settings

api = Blueprint('api', __name__)


@api.route('/hello-world', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello, World!"})


@api.route('/config', methods=['GET'])
def get_config():
    return jsonify({
        # "project_name": settings.project_name,
        # "uvicorn_host": settings.uvicorn_host,
        # "uvicorn_port": settings.uvicorn_port
    })
