# MCP Security Gateway

A Python-based security gateway for MCP (Model Context Protocol) servers.

I built this project to explore how authentication, authorization, and access control can be implemented around MCP tools. The idea is pretty simple: instead of letting clients call an MCP server directly, requests go through a gateway that decides whether they're allowed.

For this project, I used a hospital-physician scenario. Hospitals can request license verification for physicians, but only if the hospital is authenticated, has permission to access that physician, and the physician has granted consent.

## How it works

There are four main components:

- **Hospital Client:** Requests a JWT and uses it to call MCP tools.
- **Token Issuer:** A FastAPI service that authenticates hospitals and generates RSA-signed JWTs.
- **Security Gateway:** Validates incoming tokens, checks rate limits, permissions, and consent, and forwards authorized requests.
- **Physician Consent API:** Lets physicians grant or revoke access to hospitals.

The backend MCP server handles the actual license verification.

### Architecture

```text
Hospital Client
      |
      | Hospital credentials
      v
Token Issuer (FastAPI :8002)
      |
      | Signed JWT
      v
Hospital Client
      |
      | MCP Request + JWT
      v
MCP Security Gateway (:8000)
      |
      |-- JWT Authentication
      |-- Rate Limiting
      |-- Authorization
      |-- Physician Consent Check
      |-- Audit Logging
      |
      v
Backend MCP Server (STDIO)
      |
      v
License Verification Result


Physician
    |
    v
Consent API (:8001)
    |
    v
SQLite Consent Database
```

## What I've implemented

**1. JWT Authentication**

Hospitals authenticate through a separate token issuer and receive RSA-signed JWTs. The gateway verifies the signature, issuer, audience, and expiration before accepting requests.

**2. Authorization and Consent**

Each hospital has access to specific physicians. Physicians can grant or revoke consent through a separate API, and changes take effect immediately without restarting the gateway.

**3. Rate Limiting**

Implemented a sliding-window rate limiter that allows up to 5 requests per hospital every 60 seconds. Used Python locks to make the check thread-safe.

**4. Audit Logging**

Every allowed, denied, or rate-limited tool request is recorded in SQLite. Audit records are linked using SHA-256 hashes, making modifications to existing records detectable.

**5. MCP Communication**

The gateway exposes MCP tools over Streamable HTTP and communicates with the backend MCP server over STDIO.

## Tech Stack

- **Language:** Python
- **Frameworks:** FastAPI, MCP Python SDK
- **Authentication:** PyJWT, RSA (RS256)
- **Database:** SQLite
- **Other:** HTTPX, SHA-256, pytest

## Running the Project

### 1. Clone the repository

```bash
git clone https://github.com/KrishnaAttili10/mcp-security-gateway.git
cd mcp-security-gateway
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Generate RSA keys

```bash
python generate_keys.py
```

This generates `private_key.pem` and `public_key.pem` for JWT signing and verification.

The script skips generation if either key file already exists, so it won't accidentally overwrite your existing keys.

Both files are excluded from Git.


### 4. Start the services

Open three separate terminals and run:

**MCP Gateway (Port 8000)**

```bash
python gateway.py
```

**Physician Consent API (Port 8001)**

```bash
python -m uvicorn physician_api:app --host 127.0.0.1 --port 8001
```

**Token Issuer (Port 8002)**

```bash
python -m uvicorn token_issuer:app --host 127.0.0.1 --port 8002
```

### 5. Run the client

In another terminal:

```bash
python client.py
```

The client requests a JWT from the token issuer and uses it to call the `verify_license` tool through the gateway.

## Testing

I used pytest to test JWT validation and physician consent management.

```bash
python -m pytest tests/ -v
```

I also manually tested:

- Expired JWT rejection
- JWT payload tampering and hospital impersonation
- Physician consent revocation and restoration
- Per-hospital rate limiting
- Audit-log tampering detection

## Limitations / Future Improvements

This is a learning project, so some parts are simplified:

- Hospital credentials are currently hardcoded.
- Services run locally over HTTP.
- The private signing key isn't isolated at the operating-system level.
- Rate limiting uses in-memory storage, so counters reset when the gateway restarts.
- Audit hash chaining detects modifications, but someone with full database access could recompute the hashes.

I'd like to explore Redis-based distributed rate limiting, Dockerizing the services, and better key management.

## Why I built this

I've previously worked with backend services, Kafka pipelines, and AI agents, but wanted to understand more about the infrastructure supporting these systems.

This project gave me a chance to work hands-on with MCP, authentication, concurrency, and access control.