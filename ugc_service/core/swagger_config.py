from flasgger import Swagger


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
            "/track_event/": {
                "post": {
                    "summary": "Track user event",
                    "parameters": [
                        {
                            "name": "event_type",
                            "in": "query",
                            "type": "string",
                            "required": True
                        },
                        {
                            "name": "timestamp",
                            "in": "query",
                            "type": "string",
                            "required": True
                        },
                        {
                            "name": "data",
                            "in": "body",
                            "required": True,
                            "schema": {
                                "type": "object"
                            }
                        },
                        {
                            "name": "source",
                            "in": "query",
                            "type": "string",
                            "required": True
                        },
                        {
                            "name": "Authorization",
                            "in": "header",
                            "type": "string",
                            "required": True,
                            "description": "JWT Token for Authorization",
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Event tracked successfully"
                        }
                    }
                }
            }
        }
    }

    Swagger(app, config=swagger_config, template=template)
