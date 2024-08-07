from flask import Blueprint, request, jsonify
from flasgger import swag_from
from core.config import settings

api = Blueprint('api', __name__)

@api.route('/hello-world', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Returns a greeting message',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Hello, World!'
                    }
                }
            }
        }
    }
})
def hello_world():
    return jsonify({"message": "Hello, World!"})

@api.route('/config', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Returns service configuration',
            'schema': {
                'type': 'object',
                'properties': {
                    'service_name': {
                        'type': 'string',
                        'example': 'my_service'
                    },
                    'service_uvicorn_host': {
                        'type': 'string',
                        'example': '127.0.0.1'
                    },
                    'service_uvicorn_port': {
                        'type': 'integer',
                        'example': 8000
                    }
                }
            }
        }
    }
})
def get_config():
    return jsonify({
        "service_name": settings.service_name,
        "service_uvicorn_host": settings.service_uvicorn_host,
        "service_uvicorn_port": settings.service_uvicorn_port
    })
