from typing import Dict, Any
from flask_jwt_extended import get_jwt_identity
from functools import lru_cache
from kafka.errors import NoBrokersAvailable
from core.kafka import get_kafka_producer, send_to_kafka
from schema.event import EventResponse
import logging

logger = logging.getLogger(__name__)


class EventService:
    def __init__(self):
        pass

    def _determine_topic(self, event_type: str) -> str:
        """
        Логика определения топика в зависимости от типа события
        """
        if event_type == "click":
            return "click-events"
        elif event_type == "page_view":
            return "page-view-events"
        elif event_type == "custom_event":
            return "custom-events"
        else:
            raise ValueError("Unknown event type")

    def track_event(self, body: Dict[str, Any]) -> EventResponse:
        """
        Отслеживание события и отправка его в Kafka
        """
        user_id = get_jwt_identity()
        event_type = body["event_type"]
        topic = self._determine_topic(event_type)

        event = {
            "user_id": user_id,
            **body
        }

        try:
            with get_kafka_producer() as producer:
                send_to_kafka(producer, topic, key=user_id, value=event)
        except NoBrokersAvailable:
            logger.error("Kafka brokers are not available. Event will not be sent.")
            raise

        # Возвращаем ответ
        response = EventResponse(
            user_id=user_id,
            event_type=event_type,
            timestamp=body["timestamp"],
            data=body["data"],
            source=body["source"]
        )

        return response


@lru_cache()
def get_event_service() -> EventService:
    return EventService()
