from async_fastapi_jwt_auth import AuthJWT
from auth.core.config import settings

@AuthJWT.load_config
def get_config():
    return settings
