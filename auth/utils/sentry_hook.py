from auth.core.jwt import JWTBearer


def before_send(event, hint):
    if 'exc_info' in hint:
        request = event.get("request")

        if request:
            user_data = {"anonymous": True}
            headers = request.get("headers", {})

            if "authorization" in headers:
                token = headers["authorization"]
                user_data = JWTBearer.parse_token(token)

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
