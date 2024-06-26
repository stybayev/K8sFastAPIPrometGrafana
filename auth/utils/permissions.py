from functools import wraps

from fastapi import HTTPException, status


def admin_required(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        Authorize = kwargs.get('Authorize') or args[0]
        if not await self.is_admin(Authorize):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissions denied")
        return await func(self, *args, **kwargs)

    return wrapper
