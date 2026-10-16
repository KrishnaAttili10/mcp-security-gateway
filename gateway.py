from pathlib import Path
import sys

from mcp.server import MCPServer
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from audit import init_audit_db, log_access
from auth import authenticate
from mcp.server.auth.settings import AuthSettings
from auth import HospitalTokenVerifier
from mcp.server.auth.middleware.auth_context import get_access_token
from consent import init_db, has_consent


mcp = MCPServer(
    "Security Gateway",
    token_verifier=HospitalTokenVerifier(),
    auth=AuthSettings(
        issuer_url="http://127.0.0.1:8000",
        resource_server_url="http://127.0.0.1:8000/mcp",
        required_scopes=[]
    )
)


permissions = {
    "hospital_a":{"Krishna"},
    "hospital_b":{"Advaita"}
}


def authorize(hospital_id:str, physician_id:str)->bool:
    has_permission = physician_id in permissions.get(hospital_id, set())
    return has_consent(physician_id, hospital_id) and has_permission



@mcp.tool()
async def verify_license( physician_id: str) -> str:
    """Check whether a hospital is allowed to verify a physician."""

    access_token = get_access_token()
    if access_token is None:
        return "Authentication Failed"

    hospital_id = access_token.client_id

    if not authorize(hospital_id, physician_id):
        log_access(hospital_id, physician_id, "DENIED")
        return "Access Denied"

    log_access(hospital_id, physician_id, "ALLOWED")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-u", str(Path(__file__).with_name("server.py"))]
    )

    async with stdio_client(server_params) as (read,write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(
                "verify_license",
                arguments={"physician_id": physician_id,
                           "hospital_id":hospital_id}
            )

            return "\n".join(
                content.text
                for content in result.content
                if content.type == "text"
            )



if __name__ == "__main__":
    init_db()
    init_audit_db()
    mcp.run(transport="streamable-http")