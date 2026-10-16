from pathlib import Path
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from jwt_utils import generate_token, verify_token, ISSUER, AUDIENCE


PRIVATE_KEY = Path("private_key.pem").read_text()
PUBLIC_KEY = Path("public_key.pem").read_text()


def test_valid_jwt():
    token = generate_token("hospital_a", PRIVATE_KEY)

    payload = verify_token(token, PUBLIC_KEY)

    assert payload["sub"] == "hospital_a"


def test_expired_jwt():
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "hospital_a",
            "iss": ISSUER,
            "aud": AUDIENCE,
            "iat": now - timedelta(minutes=30),
            "exp": now - timedelta(minutes=15),
        },
        PRIVATE_KEY,
        algorithm="RS256",
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        verify_token(token, PUBLIC_KEY)


def test_wrong_audience():
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "hospital_a",
            "iss": ISSUER,
            "aud": "some-other-service",
            "iat": now,
            "exp": now + timedelta(minutes=15),
        },
        PRIVATE_KEY,
        algorithm="RS256",
    )

    with pytest.raises(jwt.InvalidAudienceError):
        verify_token(token, PUBLIC_KEY)