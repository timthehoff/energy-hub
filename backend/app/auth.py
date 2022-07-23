import teslapy
from fastapi import APIRouter

from app.data.auth import AuthInput

_cache_file = "/data/cache.json"
router = APIRouter(prefix="/auth")


@router.post("/login", tags=["Authentication"])
def login(email: str):
    with teslapy.Tesla(email, cache_file=_cache_file) as tesla:
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
def fetch_token(email: str, url: str):
    data = AuthInput.load()

    with teslapy.Tesla(
        email,
        cache_file=_cache_file,
        state=data.state,
        code_verifier=data.code_verifier,
    ) as tesla:
        if tesla.authorized:
            return

        data.token = tesla.fetch_token(authorization_response=url)
        data.save()
