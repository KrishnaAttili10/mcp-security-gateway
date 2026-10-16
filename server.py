from mcp.server import MCPServer

from gateway import authorize

# Creating an MCP Server named physician credentials


mcp = MCPServer("Physician Credentials")

# create database of some physican records

physicians = {
     "Krishna": {
        "name": "Dr. Krishna",
        "license": "Active"
    },
    "Advaita": {
        "name": "Dr. Advaita",
        "license": "Expired"
    }
}


@mcp.tool()
def verify_license(physician_id:str, hospital_id: str)->str:
    physician = physicians.get(physician_id)
    if physician is None:
        return "Physician Not Found"
    return f"{physician['name']}: License is {physician['license']}"
    


if __name__ == "__main__":
    mcp.run(transport="stdio")