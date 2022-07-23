from typing import Optional

from . import PermanentModel


class AuthInput(PermanentModel):
    _path = "/data/auth_input"

    email: str
    state: str
    code_verifier: bytes
    token: Optional[dict]
