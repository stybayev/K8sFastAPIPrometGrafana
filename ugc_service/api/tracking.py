from typing import Any

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate
from flasgger import swag_from

from schema.event import EventData, EventResponse
from kafka import KafkaProducer
import json

producer = KafkaProducer(bootstrap_servers=['kafka-0:9092'])


def send_to_kafka(topic: str, key: str, value: dict):
    producer.send(
        topic=topic,
        key=key.encode('utf-8'),
        value=json.dumps(value).encode('utf-8')
    )


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

    # Логика определения топика в зависимости от типа события
    event_type = body.event_type
    if event_type == "click":
        topic = "click-events"
    elif event_type == "page_view":
        topic = "page-view-events"
    elif event_type == "custom_event":
        topic = "custom-events"
    else:
        return jsonify({"status": "error", "message": "Unknown event type"}), 400

    event = {
        "user_id": user_id,
        **body.dict()
    }

    # Отправляем событие в соответствующий топик Kafka
    send_to_kafka(topic, key=user_id, value=event)

    # Создаем корректный EventResponse, передавая все нужные данные напрямую
    response = EventResponse(
        user_id=user_id,
        event_type=body.event_type,
        timestamp=body.timestamp,
        data=body.data,
        source=body.source
    )

    return jsonify(response.dict()), 200
