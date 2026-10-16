# auth.py
from mcp.server.auth.provider import TokenVerifier, AccessToken
import sys

hospital_keys = {
    "key-a-123": "hospital_a",
    "key-b-456": "hospital_b"
}

class HospitalTokenVerifier(TokenVerifier):

    async def verify_token(self, token: str)-> AccessToken:
        hospital_id = hospital_keys.get(token)
        if hospital_id is None:
            return None
        print("Token recognized:", hospital_id, file=sys.stderr, flush=True)
        return AccessToken(token = token, client_id=hospital_id, scopes=[])


def authenticate(api_key: str) -> str | None:
    return hospital_keys.get(api_key)