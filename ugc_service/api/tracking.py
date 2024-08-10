from typing import Any

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate
from flasgger import swag_from

from schema.event import EventData, EventResponse

api = Blueprint('api', __name__)


@api.route('/track_event/', methods=['POST'])
@jwt_required()
@validate()
@swag_from({
    "parameters": [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
            "description": "JWT Token for Authorization"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "event_type": {
                        "type": "string",
                        "description": "Type of the event"
                    },
                    "timestamp": {
                        "type": "string",
                        "description": "Timestamp of the event"
                    },
                    "data": {
                        "type": "object",
                        "description": "Additional data for the event"
                    },
                    "source": {
                        "type": "string",
                        "description": "Source of the event"
                    }
                },
                "required": ["event_type", "timestamp", "data", "source"]
            },
            "description": "Event data in body"
        }
    ],
    "responses": {
        "200": {
            "description": "Event tracked successfully"
        }
    }
})
def track_event(body: EventData) -> tuple[Any, int]:
    """
    Эндпоинт для отслеживания пользовательских событий
    """
    user_id = get_jwt_identity()

    event = {
        "user_id": user_id,
        **body.dict()
    }

    response = EventResponse(**event)

    return jsonify(response.dict()), 200
