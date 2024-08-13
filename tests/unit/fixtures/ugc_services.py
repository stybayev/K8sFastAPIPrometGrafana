import pytest
from flask import Flask
from unittest.mock import patch
from ugc_service.main import app as flask_app
from services.tracking import EventService


@pytest.fixture
def app():
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_event_service():
    with patch("api.tracking.get_event_service") as mock:
        yield mock.return_value
