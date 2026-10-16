from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from jwt_utils import generate_token

app = FastAPI(title="Hospital Token Issuer")

PRIVATE_KEY = Path(__file__).with_name("private_key.pem").read_text()

HOSPITAL_CREDENTIALS = {
    "hospital_a": "secret-a-123",
    "hospital_b": "secret-b-456"
}


class TokenRequest(BaseModel):
    hospital_id: str
    password: str


@app.post("/token")
def issue_token(request: TokenRequest):
    expected_password = HOSPITAL_CREDENTIALS.get(request.hospital_id)

    if expected_password is None or request.password != expected_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid hospital credentials"
        )

    token = generate_token(request.hospital_id, PRIVATE_KEY)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 900
    }