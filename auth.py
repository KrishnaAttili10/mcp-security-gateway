# auth.py
from mcp.server.auth.provider import TokenVerifier, AccessToken
import sys

from pathlib import Path
import jwt
from jwt_utils import verify_token

PUBLIC_KEY = Path(__file__).with_name("public_key.pem").read_text()
hospital_keys = {
    "key-a-123": "hospital_a",
    "key-b-456": "hospital_b"
}

class HospitalTokenVerifier(TokenVerifier):

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            payload = verify_token(token, PUBLIC_KEY)

            hospital_id = payload["sub"]

            if hospital_id not in {"hospital_a", "hospital_b"}:
                return None

            return AccessToken(
                token=token,
                client_id=hospital_id,
                scopes=[]
            )

        except jwt.InvalidTokenError:
            return None


def authenticate(api_key: str) -> str | None:
    return hospital_keys.get(api_key)