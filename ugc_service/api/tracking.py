from typing import Any

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate
from flasgger import swag_from
from schema.event import EventData, EventResponse, InternalEventData
from core.swagger_config import track_event_spec, internal_track_event_spec
from kafka.errors import NoBrokersAvailable

from services.tracking import get_event_service

api = Blueprint('api', __name__)


@api.route('/external_track_event/', methods=['POST'])
@jwt_required()
@validate()
@swag_from(track_event_spec)
def track_event(body: EventData) -> tuple[Any, int]:
    """
    Внешний эндпоинт для отслеживания пользовательских событий.
    """
    event_service = get_event_service()
    try:
        response = event_service.track_event(body.dict(), user_id=None)
        return jsonify(response.dict()), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except NoBrokersAvailable:
        return jsonify(
            {"status": "error", "message": "Service is temporarily unavailable. Please try again later."}), 503


@api.route('/internal_track_event/', methods=['POST'])
@validate()
@swag_from(internal_track_event_spec)
def internal_track_event(body: InternalEventData) -> tuple[Any, int]:
    """
    Внутренний эндпоинт для пользовательских событий.
    """
    event_service = get_event_service()
    try:
        response = event_service.track_event(body.dict(), user_id=body.user_id)
        return jsonify(response.dict()), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except NoBrokersAvailable:
        return jsonify(
            {"status": "error", "message": "Service is temporarily unavailable. Please try again later."}), 503
