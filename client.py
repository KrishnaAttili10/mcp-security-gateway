import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client
import httpx

from pathlib import Path
from jwt_utils import generate_token






async def main():
    async with httpx.AsyncClient() as auth_client:
        response = await auth_client.post(
            "http://127.0.0.1:8002/token",
            json={
                "hospital_id": "hospital_a",
                "password": "secret-a-123"
            }
        )

    response.raise_for_status()
    token = response.json()["access_token"]
    gateway_url = "http://127.0.0.1:8000/mcp"

    async with httpx.AsyncClient(headers = {"Authorization": f"Bearer {token}"}) as http_client:
         
        async with streamable_http_client(gateway_url, http_client=http_client) as (read, write):
            async with ClientSession(read, write) as session:

                await session.initialize()
                print("Session Intialized Correctly")
                print("Connected to MCP Gateway!")
                tools = await session.list_tools()

                print("Available tools:")
                for tool in tools.tools:
                    print(tool.name)


                result = await session.call_tool(
                "verify_license",
                arguments={
                    "physician_id": "Krishna"
                }
                
            )
                print("Gateway response:")
                for content in result.content: 
                        if content.type == "text":
                            print(content.text)



if __name__ == "__main__":
    asyncio.run(main())
