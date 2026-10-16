import jwt
from datetime import datetime, timedelta, timezone

ISSUER = "mcp-security-gateway"
AUDIENCE = "mcp-gateway"


def generate_token(hospital_id: str, private_key: str) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": hospital_id,
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": now,
        "exp": now + timedelta(minutes=15)
    }

    token = jwt.encode(
        payload,
        private_key,
        algorithm="RS256"
    )

    return token


def verify_token(token: str, public_key: str) -> dict:
    payload = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        issuer=ISSUER,
        audience=AUDIENCE,
        options={
            "require": ["sub", "iss", "aud", "iat", "exp"]
        }
    )

    return payload