from typing import AsyncGenerator

from fastapi import HTTPException
from starlette import status
from teslapy import Tesla

from app.data.auth import AuthInput

CACHE_FILE = "/data/cache.json"


async def get_tesla() -> AsyncGenerator[Tesla, None]:
    try:
        auth = AuthInput.load()
    except FileNotFoundError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="Not logged into Tesla account"
        )

    tesla = Tesla(auth.email, cache_file=CACHE_FILE)
    if not tesla.authorized:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="Tesla account not authorized"
        )
    try:
        yield tesla
    finally:
        tesla.close()
