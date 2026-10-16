from fastapi import FastAPI, Header, HTTPException

app = FastAPI(title="Physician Consent API")

from consent import grant_consent, revoke_consent

# Temporary demo credentials
physician_tokens = {
    "physician-key-krishna": "Krishna",
    "physician-key-advaita": "Advaita"
}


def authenticate_physician(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization")

    scheme, separator, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not separator:
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    physician_id = physician_tokens.get(token)

    if physician_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    return physician_id


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/me")
def get_current_physician(authorization: str | None = Header(default=None)):
    physician_id = authenticate_physician(authorization)

    return {"physician_id": physician_id}


@app.post("/consent/revoke")
def revoke_physician_concent(
    hospital_id: str,
    authorization: str | None = Header(default=None)
):
    physician_id = authenticate_physician(authorization)
    success = revoke_consent(physician_id, hospital_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Consent record not found"
        )

    return {
        "message": "Consent revoked successfully",
        "physician_id": physician_id,
        "hospital_id": hospital_id
    }


@app.post("/consent/grant")
def grant_physician_consent(
    hospital_id: str,
    authorization: str | None = Header(default=None)
):
    physician_id = authenticate_physician(authorization)

    success = grant_consent(physician_id, hospital_id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to grant consent")

    return {
        "message": "Consent granted successfully",
        "physician_id": physician_id,
        "hospital_id": hospital_id
    }
    

    
