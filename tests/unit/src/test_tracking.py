import json
from http import HTTPStatus
from unittest.mock import MagicMock


def test_external_track_event_success(client, mock_event_service):
    mock_event_service.track_event.return_value.dict.return_value = {
        "user_id": "123",
        "event_type": "click",
        "timestamp": "2024-08-13T00:00:00Z",
        "data": {},
        "source": "web"
    }

    event_data = {
        "event_type": "click",
        "timestamp": "2024-08-13T00:00:00Z",
        "data": {},
        "source": "web"
    }

    response = client.post('/tracking/external_track_event/',
                           data=json.dumps(event_data),
                           content_type='application/json',
                           headers={"Authorization": "Bearer testtoken"})

    assert response.status_code == HTTPStatus.OK
    assert response.json == mock_event_service.track_event.return_value.dict.return_value


def test_external_track_event_bad_request(client, mock_event_service):
    mock_event_service.track_event.side_effect = ValueError("Invalid event data")

    event_data = {
        "event_type": "invalid_type",
        "timestamp": "2024-08-13T00:00:00Z",
        "data": {},
        "source": "web"
    }

    response = client.post('/tracking/external_track_event/',
                           data=json.dumps(event_data),
                           content_type='application/json',
                           headers={"Authorization": "Bearer testtoken"})

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {"status": "error", "message": "Invalid event data"}


def test_internal_track_event_success(client, mock_event_service):
    mock_event_service.track_event.return_value.dict.return_value = {
        "user_id": "123",
        "event_type": "click",
        "timestamp": "2024-08-13T00:00:00Z",
        "data": {},
        "source": "web"
    }

    event_data = {
        "user_id": "123",
        "event_type": "click",
        "timestamp": "2024-08-13T00:00:00Z",
        "data": {},
        "source": "web"
    }

    response = client.post('/tracking/internal_track_event/',
                           data=json.dumps(event_data),
                           content_type='application/json')

    assert response.status_code == HTTPStatus.OK
    assert response.json == mock_event_service.track_event.return_value.dict.return_value


def test_internal_track_event_bad_request(client, mock_event_service):
    mock_event_service.track_event.side_effect = ValueError("Invalid event data")

    event_data = {
        "user_id": "123",
        "event_type": "invalid_type",
        "timestamp": "2024-08-13T00:00:00Z",
        "data": {},
        "source": "web"
    }

    response = client.post('/tracking/internal_track_event/',
                           data=json.dumps(event_data),
                           content_type='application/json')

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {"status": "error", "message": "Invalid event data"}
