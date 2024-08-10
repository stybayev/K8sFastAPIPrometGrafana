from functools import wraps
from flask import request, jsonify
from pydantic import BaseModel, ValidationError


def validate_request(model: BaseModel):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Валидация JSON данных с использованием Pydantic модели
                json_data = request.get_json()
                validated_data = model(**json_data)
            except ValidationError as e:
                return jsonify({"errors": e.errors()}), 400

            # Передаем валидированные данные в качестве аргумента функции
            return f(validated_data, *args, **kwargs)

        return decorated_function

    return decorator
