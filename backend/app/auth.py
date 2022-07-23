import teslapy
from fastapi import APIRouter

from app import CACHE_FILE
from app.data.auth import AuthInput

router = APIRouter(prefix="/auth")


@router.post("/login", tags=["Authentication"])
async def login(email: str):
    with teslapy.Tesla(email, cache_file=CACHE_FILE) as tesla:
        if tesla.authorized:
            return

        data = AuthInput(
            email=email,
            state=tesla.new_state(),
            code_verifier=tesla.new_code_verifier(),
        )
        data.save()

        return tesla.authorization_url(
            state=data.state, code_verifier=data.code_verifier
        )


@router.put("/login", tags=["Authentication"])
async def fetch_token(email: str, url: str):
    data = AuthInput.load()

    with teslapy.Tesla(
        email,
        cache_file=CACHE_FILE,
        state=data.state,
        code_verifier=data.code_verifier,
    ) as tesla:
        if tesla.authorized:
            return

        data.token = tesla.fetch_token(authorization_response=url)
        data.save()
