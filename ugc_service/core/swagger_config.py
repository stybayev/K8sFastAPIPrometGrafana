from flasgger import Swagger

track_event_spec = {
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
}

internal_track_event_spec = {
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID of the user"
                    },
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
                "required": ["user_id", "event_type", "timestamp", "data", "source"]
            },
            "description": "Event data in body"
        }
    ],
    "responses": {
        "200": {
            "description": "Event tracked successfully"
        }
    },
    "security": []
}


def configure_swagger(app):
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    }

    template = {
        "swagger": "2.0",
        "info": {
            "title": "UGC Service API",
            "description": "API for tracking user events",
            "version": "1.0.0"
        },
        "basePath": "/tracking",
        "schemes": [
            "http"
        ],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'",
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ],
        "paths": {
            "/external_track_event/": {
                "post": {
                    "summary": "Track external user event",
                    **track_event_spec
                }
            },
            "/internal_track_event/": {
                "post": {
                    "summary": "Track internal user event",
                    **internal_track_event_spec
                }
            }
        }
    }

    Swagger(app, config=swagger_config, template=template)
