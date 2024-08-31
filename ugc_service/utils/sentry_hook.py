import jwt
from jwt import PyJWTError
from core.config import settings


def before_send(event, hint):
    if 'exc_info' in hint:
        request = event.get("request")

        if request:
            user_data = {"anonymous": True}
            headers = request.get("headers", {})

            if "authorization" in headers:
                token = headers["authorization"]
                user_data = extract_user_data_from_token(token)

            # Добавление информации о пользователе в event
            event["user"] = {"user": user_data}

            # Добавление информации о пользователе в теги
            event.setdefault("tags", {})
            if user_data.get("id"):
                event["tags"]["user_id"] = user_data["id"]
            if user_data.get("first_name"):
                event["tags"]["user_name"] = f"{user_data['first_name']} {user_data.get('last_name', '')}".strip()
            if user_data.get("anonymous"):
                event["tags"]["user_name"] = "anonymous"

    return event


def extract_user_data_from_token(token: str) -> dict:
    """
    Извлекает информацию о пользователе из JWT-токена.

    :param token: JWT-токен из заголовка Authorization.
    :return: Словарь с id, first_name и last_name пользователя или {"anonymous": True}, если не удалось извлечь.
    """
    try:
        if token.startswith("Bearer "):
            token = token[len("Bearer "):]

        # Декодируем JWT-токен
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

        _id = payload.get("id")
        first_name = payload.get("first_name")
        last_name = payload.get("last_name")

        if _id:
            return {"id": _id, "first_name": first_name, "last_name": last_name}
        else:
            return {"anonymous": True}

    except PyJWTError:
        return {"anonymous": True}
