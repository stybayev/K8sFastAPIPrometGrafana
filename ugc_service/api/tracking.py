from typing import Any

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate
from flasgger import swag_from
from schema.event import EventData, EventResponse
from core.swagger_config import track_event_spec

from services.tracking import get_event_service

api = Blueprint('api', __name__)


@api.route('/track_event/', methods=['POST'])
@jwt_required()
@validate()
@swag_from(track_event_spec)
def track_event(body: EventData) -> tuple[Any, int]:
    """
    Эндпоинт для отслеживания пользовательских событий
    """
    event_service = get_event_service()
    try:
        response = event_service.track_event(body.dict())
        return jsonify(response.dict()), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
